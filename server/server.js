import http from "node:http";
import crypto from "node:crypto";

const PORT = Number(process.env.PORT || 8080);
const ROOM_TTL_MS = 15 * 60 * 1000;
const QUEUE_TTL_MS = 2 * 60 * 1000;
const rooms = new Map();
const tickets = new Map();
const waiting = new Map();

function cleanExpired(now = Date.now()) {
  for (const [code, room] of rooms) if (room.expiresAt <= now) rooms.delete(code);
  for (const [id, ticket] of tickets) {
    if (ticket.expiresAt <= now) {
      tickets.delete(id);
      if (ticket.status === "waiting" && waiting.get(ticket.key) === id) waiting.delete(ticket.key);
    }
  }
}

function clientAddress(req) {
  const forwarded = req.headers["x-forwarded-for"];
  const value = typeof forwarded === "string" ? forwarded.split(",")[0].trim() : req.socket.remoteAddress;
  return String(value || "").replace(/^::ffff:/, "");
}

function send(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(body),
    "cache-control": "no-store",
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "content-type"
  });
  res.end(body);
}

async function readJson(req) {
  let raw = "";
  for await (const chunk of req) {
    raw += chunk;
    if (raw.length > 8192) throw new Error("BODY_TOO_LARGE");
  }
  if (!raw) return {};
  return JSON.parse(raw);
}

function roomCode() {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let code = "";
  for (let i = 0; i < 6; i++) code += alphabet[crypto.randomInt(alphabet.length)];
  return code;
}

function createRoom({ hostId, address, port, mode, rating }) {
  let code;
  do code = roomCode(); while (rooms.has(code));
  const room = {
    code, hostId, address, port, mode, rating,
    guestId: null,
    createdAt: Date.now(),
    expiresAt: Date.now() + ROOM_TTL_MS
  };
  rooms.set(code, room);
  return room;
}

export function createMatchmakingServer() {
  return http.createServer(async (req, res) => {
    if (req.method === "OPTIONS") return send(res, 204, {});
    const url = new URL(req.url, "http://localhost");
    cleanExpired();

    if (req.method === "GET" && url.pathname === "/health") {
      return send(res, 200, { ok: true, service: "CHECKMATE matchmaking", version: 1 });
    }

    try {
      if (req.method === "POST" && url.pathname === "/rooms") {
        const body = await readJson(req);
        const hostId = String(body.playerId || "").trim().slice(0, 64);
        const port = Number(body.port || 24567);
        const mode = String(body.mode || "classic").trim().slice(0, 32);
        const rating = Math.max(0, Math.min(100000, Number(body.rating || 0)));
        if (!hostId || !Number.isInteger(port) || port < 1 || port > 65535) {
          return send(res, 400, { error: "INVALID_ROOM_DATA" });
        }
        const room = createRoom({ hostId, address: clientAddress(req), port, mode, rating });
        return send(res, 201, { code: room.code, host: room.address, port: room.port, mode: room.mode, expiresIn: ROOM_TTL_MS / 1000 });
      }

      const joinMatch = url.pathname.match(/^\/rooms\/([A-Z2-9]{6})\/join$/);
      if (req.method === "POST" && joinMatch) {
        const body = await readJson(req);
        const playerId = String(body.playerId || "").trim().slice(0, 64);
        const room = rooms.get(joinMatch[1]);
        if (!playerId) return send(res, 400, { error: "PLAYER_ID_REQUIRED" });
        if (!room) return send(res, 404, { error: "ROOM_NOT_FOUND" });
        if (room.hostId === playerId) return send(res, 409, { error: "CANNOT_JOIN_OWN_ROOM" });
        if (room.guestId) return send(res, 409, { error: "ROOM_FULL" });
        room.guestId = playerId;
        room.expiresAt = Date.now() + ROOM_TTL_MS;
        return send(res, 200, { joined: true, host: room.address, port: room.port, mode: room.mode });
      }

      if (req.method === "POST" && url.pathname === "/matchmaking/queue") {
        const body = await readJson(req);
        const playerId = String(body.playerId || "").trim().slice(0, 64);
        const mode = String(body.mode || "classic").trim().slice(0, 32);
        const rating = Math.max(0, Math.min(100000, Number(body.rating || 0)));
        const port = Number(body.port || 24567);
        if (!playerId || !Number.isInteger(port) || port < 1 || port > 65535) {
          return send(res, 400, { error: "INVALID_QUEUE_DATA" });
        }
        const key = mode;
        const waitingId = waiting.get(key);
        const waitingTicket = waitingId ? tickets.get(waitingId) : null;
        if (waitingTicket && waitingTicket.playerId !== playerId && waitingTicket.status === "waiting") {
          const room = createRoom({
            hostId: waitingTicket.playerId,
            address: waitingTicket.address,
            port: waitingTicket.port,
            mode,
            rating: waitingTicket.rating
          });
          room.guestId = playerId;
          const ticketId = crypto.randomUUID();
          const ticket = {
            id: ticketId, playerId, key, status: "matched", role: "guest",
            host: room.address, port: room.port, code: room.code,
            expiresAt: Date.now() + QUEUE_TTL_MS
          };
          tickets.set(ticketId, ticket);
          waitingTicket.status = "matched";
          waitingTicket.role = "host";
          waitingTicket.host = room.address;
          waitingTicket.port = room.port;
          waitingTicket.code = room.code;
          waiting.delete(key);
          return send(res, 201, { ticket: ticketId, status: "matched", role: "guest", host: room.address, port: room.port, code: room.code });
        }
        const ticketId = crypto.randomUUID();
        tickets.set(ticketId, {
          id: ticketId, playerId, key, status: "waiting",
          address: clientAddress(req), port, rating,
          expiresAt: Date.now() + QUEUE_TTL_MS
        });
        waiting.set(key, ticketId);
        return send(res, 201, { ticket: ticketId, status: "waiting", pollAfterMs: 1500 });
      }

      const ticketMatch = url.pathname.match(/^\/matchmaking\/queue\/([0-9a-f-]+)$/);
      if (req.method === "GET" && ticketMatch) {
        const ticket = tickets.get(ticketMatch[1]);
        if (!ticket) return send(res, 404, { error: "TICKET_EXPIRED" });
        return send(res, 200, {
          ticket: ticket.id, status: ticket.status,
          ...(ticket.status === "matched" ? { role: ticket.role, host: ticket.host, port: ticket.port, code: ticket.code } : {})
        });
      }

      return send(res, 404, { error: "NOT_FOUND" });
    } catch (error) {
      if (error.message === "BODY_TOO_LARGE") return send(res, 413, { error: "BODY_TOO_LARGE" });
      if (error instanceof SyntaxError) return send(res, 400, { error: "INVALID_JSON" });
      return send(res, 500, { error: "INTERNAL_ERROR" });
    }
  });
}

if (process.env.NODE_ENV !== "test") {
  const server = createMatchmakingServer();
  server.listen(PORT, "0.0.0.0", () => {
    process.stdout.write("CHECKMATE matchmaking listening on " + PORT + "\n");
  });
}
