import http from "node:http";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import { createAccountService } from "./accounts.js";

const PORT = Number(process.env.PORT || 8080);
const ROOM_TTL_MS = 15 * 60 * 1000;
const QUEUE_TTL_MS = 2 * 60 * 1000;
const INITIAL_RATING_GAP = 100;
const RATING_GAP_STEP = 50;
const RATING_GAP_STEP_MS = 15 * 1000;
const MAX_RATING_GAP = 500;
const rooms = new Map();
const tickets = new Map();
const waiting = new Map();

function cleanExpired(now = Date.now()) {
  for (const [code, room] of rooms) if (room.expiresAt <= now) rooms.delete(code);
  for (const [id, ticket] of tickets) {
    if (ticket.expiresAt <= now) {
      tickets.delete(id);
      if (ticket.status === "waiting") {
        const queue = waiting.get(ticket.key);
        if (queue) {
          queue.delete(id);
          if (queue.size === 0) waiting.delete(ticket.key);
        }
      }
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

function normalizeRating(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.min(100000, Math.round(number))) : 1000;
}

function allowedRatingGap(waitMs) {
  return Math.min(MAX_RATING_GAP, INITIAL_RATING_GAP + Math.floor(Math.max(0, waitMs) / RATING_GAP_STEP_MS) * RATING_GAP_STEP);
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

function tryMatch(ticket, now = Date.now()) {
  const queue = waiting.get(ticket.key);
  if (!queue) return null;
  let best = null;
  let bestDifference = Infinity;
  for (const id of queue) {
    const candidate = tickets.get(id);
    if (!candidate || candidate.id === ticket.id || candidate.status !== "waiting" || candidate.playerId === ticket.playerId) continue;
    const difference = Math.abs(candidate.rating - ticket.rating);
    const candidateGap = allowedRatingGap(now - candidate.createdAt);
    const ticketGap = allowedRatingGap(now - ticket.createdAt);
    const allowedGap = Math.max(candidateGap, ticketGap);
    if (difference <= allowedGap && difference < bestDifference) {
      best = candidate;
      bestDifference = difference;
    }
  }
  if (!best) return null;

  queue.delete(best.id);
  queue.delete(ticket.id);
  if (queue.size === 0) waiting.delete(ticket.key);
  const room = createRoom({
    hostId: best.playerId,
    address: best.address,
    port: best.port,
    mode: best.key,
    rating: best.rating
  });
  room.guestId = ticket.playerId;
  best.status = "matched";
  best.role = "host";
  best.host = room.address;
  best.port = room.port;
  best.code = room.code;
  best.opponentRating = ticket.rating;
  best.ratingDifference = bestDifference;
  best.expiresAt = now + QUEUE_TTL_MS;
  ticket.status = "matched";
  ticket.role = "guest";
  ticket.host = room.address;
  ticket.port = room.port;
  ticket.code = room.code;
  ticket.opponentRating = best.rating;
  ticket.ratingDifference = bestDifference;
  ticket.expiresAt = now + QUEUE_TTL_MS;
  return room;
}

export function createMatchmakingServer(options = {}) {
  const accounts = createAccountService(options);
  return http.createServer(async (req, res) => {
    if (req.method === "OPTIONS") return send(res, 204, {});
    const url = new URL(req.url, "http://localhost");
    cleanExpired();

    if (req.method === "GET" && url.pathname === "/health") {
      return send(res, 200, { ok: true, service: "CHECKMATE matchmaking", version: 2 });
    }

    try {
      if (req.method === "POST" && url.pathname === "/accounts/register") {
        const body = await readJson(req);
        const result = await accounts.register(body);
        return send(res, result.status, result.body);
      }

      if (req.method === "POST" && url.pathname === "/accounts/login") {
        const body = await readJson(req);
        const result = await accounts.login(body);
        return send(res, result.status, result.body);
      }

      if (req.method === "GET" && url.pathname === "/account/me") {
        const authorization = String(req.headers.authorization || "");
        const token = authorization.startsWith("Bearer ") ? authorization.slice(7) : "";
        const result = await accounts.me(token);
        return send(res, result.status, result.body);
      }

      if (req.method === "GET" && url.pathname === "/leaderboard") {
        const limit = Number(url.searchParams.get("limit") || 50);
        return send(res, 200, { players: await accounts.leaderboard(limit) });
      }

      if (req.method === "POST" && url.pathname === "/rooms") {
        const body = await readJson(req);
        const hostId = String(body.playerId || "").trim().slice(0, 64);
        const port = Number(body.port || 24567);
        const mode = String(body.mode || "classic").trim().slice(0, 32);
        const rating = normalizeRating(body.rating ?? 1000);
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
        const rating = normalizeRating(body.rating ?? 1000);
        const port = Number(body.port || 24567);
        if (!playerId || !Number.isInteger(port) || port < 1 || port > 65535) {
          return send(res, 400, { error: "INVALID_QUEUE_DATA" });
        }
        const ticketId = crypto.randomUUID();
        const ticket = {
          id: ticketId, playerId, key: mode, status: "waiting",
          address: clientAddress(req), port, rating,
          createdAt: Date.now(),
          expiresAt: Date.now() + QUEUE_TTL_MS
        };
        tickets.set(ticketId, ticket);
        const queue = waiting.get(mode) || new Set();
        queue.add(ticketId);
        waiting.set(mode, queue);
        const room = tryMatch(ticket);
        if (!room) {
          return send(res, 201, {
            ticket: ticketId, status: "waiting", pollAfterMs: 1500,
            rating, initialRatingGap: INITIAL_RATING_GAP,
            maxRatingGap: MAX_RATING_GAP
          });
        }
        return send(res, 201, {
          ticket: ticketId, status: "matched", role: "guest",
          host: ticket.host, port: ticket.port, code: ticket.code,
          opponentRating: ticket.opponentRating,
          ratingDifference: ticket.ratingDifference
        });
      }

      const cancelMatch = url.pathname.match(/^\/matchmaking\/queue\/([0-9a-f-]+)\/cancel$/);
      if (req.method === "POST" && cancelMatch) {
        const ticket = tickets.get(cancelMatch[1]);
        if (!ticket) return send(res, 404, { error: "TICKET_EXPIRED" });
        if (ticket.status !== "waiting") return send(res, 409, { error: "QUEUE_NOT_WAITING" });
        const queue = waiting.get(ticket.key);
        if (queue) {
          queue.delete(ticket.id);
          if (queue.size === 0) waiting.delete(ticket.key);
        }
        ticket.status = "cancelled";
        ticket.expiresAt = Date.now() + QUEUE_TTL_MS;
        return send(res, 200, { cancelled: true, status: "cancelled" });
      }

      const ticketMatch = url.pathname.match(/^\/matchmaking\/queue\/([0-9a-f-]+)$/);
      if (req.method === "GET" && ticketMatch) {
        const ticket = tickets.get(ticketMatch[1]);
        if (!ticket) return send(res, 404, { error: "TICKET_EXPIRED" });
        return send(res, 200, {
          ticket: ticket.id, status: ticket.status,
          ...(ticket.status === "matched" ? {
            role: ticket.role, host: ticket.host, port: ticket.port, code: ticket.code,
            opponentRating: ticket.opponentRating, ratingDifference: ticket.ratingDifference
          } : {})
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

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const server = createMatchmakingServer();
  server.listen(PORT, "0.0.0.0", () => {
    process.stdout.write("CHECKMATE matchmaking listening on " + PORT + "\n");
  });
}
