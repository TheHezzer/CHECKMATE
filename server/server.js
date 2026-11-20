import http from "node:http";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import { createAccountService } from "./accounts.js";
import { createGameState, getGameState, applyGameMove, passGameTurn, sendTeamChat } from "./gameplay.js";

const PORT = Number(process.env.PORT || 8080);
const QUEUE_TTL_MS = 10 * 60 * 1000;
const ALLOWED_SECOND_PIECES = new Set(["Ладья", "Конь", "Слон", "Ферзь", "Король"]);
const PIECE_TEAM_SLOTS = { "Ладья": 2, "Конь": 2, "Слон": 2, "Ферзь": 1, "Король": 1 };
const PIECE_MATCH_SLOTS = Object.fromEntries(Object.entries(PIECE_TEAM_SLOTS).map(([piece, count]) => [piece, count * 2]));
const INITIAL_RATING_GAP = 100;
const RATING_GAP_STEP = 50;
const RATING_GAP_STEP_MS = 15 * 1000;
const MAX_RATING_GAP = 500;
const matches = new Map();
const CLASSIC_TEAM_SIZE = 8;
const CLASSIC_MATCH_SIZE = 16;
const tickets = new Map();
const waiting = new Map();

function cleanExpired(now = Date.now()) {
  for (const [id, ticket] of tickets) {
    if (ticket.expiresAt <= now) {
      tickets.delete(id);
      if (["waiting","waiting_piece_slot"].includes(ticket.status)) {
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

function balanceTeams(candidates) {
  if (candidates.length === CLASSIC_MATCH_SIZE) {
    const teams = { white: [], black: [] };
    const sums = { white: 0, black: 0 };
    for (const [piece, perTeam] of Object.entries(PIECE_TEAM_SLOTS)) {
      const pool = candidates.filter(p => p.piece === piece).sort((a,b) => b.rating-a.rating || a.createdAt-b.createdAt);
      if (pool.length !== perTeam * 2) return [];
      for (const player of pool) {
        const team = teams.white.length < CLASSIC_TEAM_SIZE && (teams.black.length >= CLASSIC_TEAM_SIZE || teams.white.length < teams.black.length || (teams.white.length === teams.black.length && sums.white <= sums.black)) ? "white" : "black";
        teams[team].push(player);
        sums[team] += player.rating;
      }
    }
    if (teams.white.length !== CLASSIC_TEAM_SIZE || teams.black.length !== CLASSIC_TEAM_SIZE) return [];
    return [...teams.white.map((p,slot)=>({playerId:p.playerId,name:p.playerName,rating:p.rating,piece:p.piece,secondPiece:p.piece,pieces:["Пешка",p.piece],team:"white",slot})),...teams.black.map((p,slot)=>({playerId:p.playerId,name:p.playerName,rating:p.rating,piece:p.piece,secondPiece:p.piece,pieces:["Пешка",p.piece],team:"black",slot}))];
  }
  const sorted=[...candidates].sort((a,b)=>b.rating-a.rating||a.createdAt-b.createdAt);
  const teams={white:[],black:[]},sums={white:0,black:0};
  for(const p of sorted){
    let team;
    if(teams.white.length>=CLASSIC_TEAM_SIZE)team="black";
    else if(teams.black.length>=CLASSIC_TEAM_SIZE)team="white";
    else if(teams.white.length<teams.black.length)team="white";
    else if(teams.black.length<teams.white.length)team="black";
    else team=sums.white<=sums.black?"white":"black";
    teams[team].push(p);sums[team]+=p.rating;
  }
  return [...teams.white.map((p,slot)=>({playerId:p.playerId,name:p.playerName,rating:p.rating,piece:p.piece,secondPiece:p.piece,pieces:["Пешка",p.piece],team:"white",slot})),...teams.black.map((p,slot)=>({playerId:p.playerId,name:p.playerName,rating:p.rating,piece:p.piece,secondPiece:p.piece,pieces:["Пешка",p.piece],team:"black",slot}))];
}
function pieceCapacity(mode) {
  const queue = waiting.get(mode);
  const ticketsInQueue = queue ? [...queue].map(id => tickets.get(id)).filter(p => p && ["waiting","waiting_piece_slot"].includes(p.status)) : [];
  return Object.fromEntries(Object.entries(PIECE_MATCH_SLOTS).map(([piece, capacity]) => {
    const selected = ticketsInQueue.filter(p => p.piece === piece).length;
    return [piece, { selected, capacity, available: Math.max(0, capacity - selected), full: selected >= capacity }];
  }));
}

function eligiblePlayers(ticket,now=Date.now()){
  const queue=waiting.get(ticket.key);if(!queue)return[];
  return [...queue].map(id=>tickets.get(id)).filter(p=>p&&["waiting","waiting_piece_slot"].includes(p.status)&&p.playerId!==ticket.playerId)
    .filter(p=>Math.abs(p.rating-ticket.rating)<=Math.max(allowedRatingGap(now-p.createdAt),allowedRatingGap(now-ticket.createdAt)))
    .sort((a,b)=>Math.abs(a.rating-ticket.rating)-Math.abs(b.rating-ticket.rating)||a.createdAt-b.createdAt);
}
function queuePreview(ticket,now=Date.now()){
  const queue=waiting.get(ticket.key);
  const count=queue?[...queue].map(id=>tickets.get(id)).filter(p=>p&&["waiting","waiting_piece_slot"].includes(p.status)).length:0;
  return {players:balanceTeams([ticket,...eligiblePlayers(ticket,now)].slice(0,CLASSIC_MATCH_SIZE)),queueCount:count,requiredPlayers:CLASSIC_MATCH_SIZE,allowedRatingGap:allowedRatingGap(now-ticket.createdAt),pieceCapacity:pieceCapacity(ticket.key)};
}
function composeClassicRoster(candidates, referenceTicket) {
  if (candidates.length < CLASSIC_MATCH_SIZE) return null;
  const selected = [];
  for (const [piece, required] of Object.entries(PIECE_MATCH_SLOTS)) {
    const pool = candidates.filter(p => p.piece === piece)
      .sort((a,b) => Math.abs(a.rating-referenceTicket.rating)-Math.abs(b.rating-referenceTicket.rating) || a.createdAt-b.createdAt);
    if (pool.length < required) return null;
    selected.push(...pool.slice(0, required));
  }
  if (selected.length !== CLASSIC_MATCH_SIZE) return null;
  return balanceTeams(selected);
}

function tryMatch(ticket, now=Date.now()) {
  const candidates=[ticket,...eligiblePlayers(ticket,now)];
  let roster=composeClassicRoster(candidates,ticket);
  if(!roster || roster.length!==CLASSIC_MATCH_SIZE)return null;
  // Assign colors only after the full 16-player roster is ready.
  if (crypto.randomInt(0, 2) === 1) {
    roster = roster.map(player => ({...player, team: player.team === "white" ? "black" : "white"}));
  }
  const matchId=crypto.randomUUID();
  const whitePlayers=roster.filter(p=>p.team==="white");
  const startingPlayer=whitePlayers[crypto.randomInt(0, whitePlayers.length)];
  const match={id:matchId,mode:ticket.key,createdAt:now,players:roster,startingTeam:"white",startingPlayerId:startingPlayer.playerId,gameServerHost:process.env.GAME_SERVER_HOST||"",gameServerPort:Number(process.env.GAME_SERVER_PORT||24567),sessionTokens:new Map()};
  for (const player of roster) match.sessionTokens.set(player.playerId, crypto.randomBytes(32).toString("hex"));
  match.game=createGameState(match);
  matches.set(matchId,match);
  const selectedIds=new Set(roster.map(p=>p.playerId));
  const queue=waiting.get(ticket.key);
  for(const p of candidates.filter(p=>selectedIds.has(p.playerId))){
    if(queue)queue.delete(p.id);
    p.status="matched";p.matchId=matchId;p.players=roster;
    const entry=roster.find(x=>x.playerId===p.playerId);p.team=entry.team;p.slot=entry.slot;p.pieceSlot=entry.pieceSlot;
    p.gameServerHost=match.gameServerHost;p.gameServerPort=match.gameServerPort;p.startingPlayerId=match.startingPlayerId;p.playerSessionToken=match.sessionTokens.get(p.playerId);p.expiresAt=now+QUEUE_TTL_MS;
  }
  if(queue&&queue.size===0)waiting.delete(ticket.key);
  return match;
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

      if (req.method === "POST" && url.pathname === "/matchmaking/queue") {
        const body=await readJson(req);
        const playerId=String(body.playerId||"").trim().slice(0,64);
        const playerName=String(body.playerName||("Игрок-"+playerId.slice(0,5))).trim().slice(0,20)||"Игрок";
        const piece=String(body.piece||"Конь").trim();
        const mode=String(body.mode||"classic").trim().slice(0,32);
        const rating=normalizeRating(body.rating??1000);
        if(!playerId||!mode||!ALLOWED_SECOND_PIECES.has(piece))return send(res,400,{error:"INVALID_QUEUE_DATA"});
        const existing=[...tickets.values()].find(t=>t.playerId===playerId&&["waiting","waiting_piece_slot"].includes(t.status));
        if(existing)return send(res,409,{error:"ALREADY_IN_QUEUE",ticket:existing.id});
        const ticketId=crypto.randomUUID();
        const ticket={id:ticketId,playerId,playerName,piece,key:mode,status:"waiting",rating,createdAt:Date.now(),expiresAt:Date.now()+QUEUE_TTL_MS};
        tickets.set(ticketId,ticket);
        const queue=waiting.get(mode)||new Set();queue.add(ticketId);waiting.set(mode,queue);
        tryMatch(ticket);
        if(ticket.status==="matched")return send(res,201,{ticket:ticketId,status:"matched",matchId:ticket.matchId,team:ticket.team,players:ticket.players,startingTeam:"white",startingPlayerId:ticket.startingPlayerId||"",playerSessionToken:ticket.playerSessionToken||"",gameServerHost:ticket.gameServerHost,gameServerPort:ticket.gameServerPort});
        const slots=pieceCapacity(mode);
        const status=slots[piece].selected>slots[piece].capacity?"waiting_piece_slot":"waiting";
        ticket.status=status;
        return send(res,201,{ticket:ticketId,status,pollAfterMs:1500,rating,initialRatingGap:INITIAL_RATING_GAP,maxRatingGap:MAX_RATING_GAP,...queuePreview(ticket)});
      }

      const gameplayRoute=url.pathname.match(/^\/matches\/([0-9a-f-]+)\/(state|move|pass|chat)$/);
      if(gameplayRoute){
        const match=matches.get(gameplayRoute[1]);
        if(!match)return send(res,404,{error:"MATCH_NOT_FOUND"});
        const supplied=String(req.headers["x-player-session"]||"");
        const auth=String(req.headers.authorization||"");
        const sessionToken=supplied||(auth.startsWith("Bearer ")?auth.slice(7):"");
        const entry=[...match.sessionTokens.entries()].find(([,token])=>token===sessionToken);
        if(!entry)return send(res,401,{error:"INVALID_MATCH_SESSION"});
        const playerId=entry[0],action=gameplayRoute[2];
        if(req.method==="GET"&&action==="state"){
          const state=getGameState(match,playerId);
          return state?send(res,200,state):send(res,404,{error:"MATCH_NOT_FOUND"});
        }
        if(req.method!=="POST")return send(res,405,{error:"METHOD_NOT_ALLOWED"});
        const body=await readJson(req);
        if(action==="move"){
          const result=applyGameMove(match,playerId,body);
          return send(res,result.status,result.state||{error:result.error});
        }
        if(action==="pass"){
          const result=passGameTurn(match,playerId);
          return send(res,result.status,result.state||{error:result.error});
        }
        if(action==="chat"){
          const result=sendTeamChat(match,playerId,body.message);
          return send(res,result.status,result.message?{message:result.message}:{error:result.error});
        }
      }
      const cancelMatch = url.pathname.match(/^\/matchmaking\/queue\/([0-9a-f-]+)\/cancel$/);
      if (req.method === "POST" && cancelMatch) {
        const ticket = tickets.get(cancelMatch[1]);
        if (!ticket) return send(res, 404, { error: "TICKET_EXPIRED" });
        if (!["waiting","waiting_piece_slot"].includes(ticket.status)) return send(res, 409, { error: "QUEUE_NOT_WAITING" });
        const queue = waiting.get(ticket.key);
        if (queue) {
          queue.delete(ticket.id);
          if (queue.size === 0) waiting.delete(ticket.key);
        }
        ticket.status = "cancelled";
        ticket.expiresAt = Date.now() + QUEUE_TTL_MS;
        return send(res, 200, { cancelled: true, status: "cancelled" });
      }

      const queuePrefix="/matchmaking/queue/";
      if(req.method==="GET"&&url.pathname.startsWith(queuePrefix)){
        const ticketId=url.pathname.slice(queuePrefix.length);
        const ticket=tickets.get(ticketId);
        if(!ticket)return send(res,404,{error:"TICKET_EXPIRED"});
        if(ticket.status==="matched")return send(res,200,{ticket:ticket.id,status:"matched",matchId:ticket.matchId,team:ticket.team,players:ticket.players,startingTeam:"white",startingPlayerId:ticket.startingPlayerId||"",gameServerHost:ticket.gameServerHost,gameServerPort:ticket.gameServerPort});
        const preview=ticket.status==="waiting"?queuePreview(ticket):{players:[],queueCount:0,requiredPlayers:CLASSIC_MATCH_SIZE};
        return send(res,200,{ticket:ticket.id,status:ticket.status,...preview});
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
