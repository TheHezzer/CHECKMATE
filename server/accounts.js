import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { calculateMatchReward } from "./rewards.js";

const TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60;
const CITY_PIECES = {
  "Пешка": { xp: 0, zloty: 0 },
  "Конь": { xp: 300, zloty: 900 },
  "Слон": { xp: 400, zloty: 1100 },
  "Ладья": { xp: 500, zloty: 1200 },
  "Ферзь": { xp: 1200, zloty: 3000 },
  "Король": { xp: 1000, zloty: 2600 }
};
const CITY_SKINS = {
  "Дерево": { xp: 0, zloty: 0 },
  "Мрамор": { xp: 250, zloty: 1000 },
  "Обсидиан": { xp: 500, zloty: 2000 },
  "Сталь": { xp: 400, zloty: 1800 },
  "Аниме": { xp: 700, zloty: 2500 }
};
function ensureCity(account) {
  if (!account.city || typeof account.city !== "object") account.city = {};
  const city = account.city;
  if (!city.wallet) city.wallet = { zloty: 12750, xp: 850, gambits: 0 };
  if (!Array.isArray(city.unlockedPieces)) city.unlockedPieces = ["Пешка"];
  if (!Array.isArray(city.ownedPieces)) city.ownedPieces = ["Пешка"];
  if (!Array.isArray(city.ownedSkins)) city.ownedSkins = ["Дерево"];
  return city;
}

function safeEqual(a, b) {
  const left = Buffer.from(a);
  const right = Buffer.from(b);
  return left.length === right.length && crypto.timingSafeEqual(left, right);
}

function publicProfile(account) {
  return {
    playerId: account.id,
    username: account.username,
    rating: account.rating,
    division: divisionFor(account.rating),
    wins: account.wins,
    losses: account.losses,
    draws: account.draws,
    matches: account.matches,
    createdAt: account.createdAt
  };
}

export function divisionFor(rating) {
  if (rating >= 1800) return "Diamond";
  if (rating >= 1600) return "Platinum";
  if (rating >= 1400) return "Gold";
  if (rating >= 1200) return "Silver";
  return "Bronze";
}

export function createAccountService({ dataFile = process.env.CHECKMATE_DATA_FILE || path.join(process.cwd(), "data", "accounts.json"), tokenSecret = process.env.CHECKMATE_TOKEN_SECRET || crypto.randomBytes(32).toString("hex") } = {}) {
  let accounts = [];
  let loaded = false;
  let writeQueue = Promise.resolve();

  async function load() {
    if (loaded) return;
    try {
      const parsed = JSON.parse(await fs.readFile(dataFile, "utf8"));
      if (!Array.isArray(parsed)) throw new Error("INVALID_ACCOUNT_DATABASE");
      accounts = parsed;
      for (const account of accounts) ensureCity(account);
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
      accounts = [];
    }
    loaded = true;
  }

  async function persist() {
    const snapshot = JSON.stringify(accounts, null, 2);
    writeQueue = writeQueue.then(async () => {
      await fs.mkdir(path.dirname(dataFile), { recursive: true });
      const temporary = dataFile + ".tmp";
      await fs.writeFile(temporary, snapshot, { mode: 0o600 });
      await fs.rename(temporary, dataFile);
    });
    return writeQueue;
  }

  function issueToken(account) {
    const payload = Buffer.from(JSON.stringify({
      sub: account.id,
      exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SECONDS
    })).toString("base64url");
    const signature = crypto.createHmac("sha256", tokenSecret).update(payload).digest("base64url");
    return payload + "." + signature;
  }

  function verifyToken(token) {
    if (typeof token !== "string") return null;
    const parts = token.split(".");
    if (parts.length !== 2) return null;
    const expected = crypto.createHmac("sha256", tokenSecret).update(parts[0]).digest("base64url");
    if (!safeEqual(parts[1], expected)) return null;
    try {
      const payload = JSON.parse(Buffer.from(parts[0], "base64url").toString("utf8"));
      if (!payload.sub || !Number.isFinite(payload.exp) || payload.exp <= Date.now() / 1000) return null;
      return accounts.find(account => account.id === payload.sub) || null;
    } catch {
      return null;
    }
  }

  async function register({ username, password }) {
    await load();
    const cleanName = String(username || "").trim();
    if (!/^[A-Za-z0-9_]{3,20}$/.test(cleanName)) {
      return { status: 400, body: { error: "USERNAME_INVALID", message: "Username must be 3-20 letters, numbers or underscores." } };
    }
    if (typeof password !== "string" || password.length < 8 || password.length > 128) {
      return { status: 400, body: { error: "PASSWORD_INVALID", message: "Password must be 8-128 characters." } };
    }
    if (accounts.some(account => account.username.toLowerCase() === cleanName.toLowerCase())) {
      return { status: 409, body: { error: "USERNAME_TAKEN" } };
    }
    const salt = crypto.randomBytes(16);
    const passwordHash = await new Promise((resolve, reject) => {
      crypto.scrypt(password, salt, 64, (error, derived) => error ? reject(error) : resolve(derived.toString("hex")));
    });
    const account = {
      id: crypto.randomUUID(),
      username: cleanName,
      salt: salt.toString("hex"),
      passwordHash,
      rating: 1000,
      wins: 0,
      losses: 0,
      draws: 0,
      matches: 0,
      city: { wallet: { zloty: 12750, xp: 850, gambits: 0 }, unlockedPieces: ["Пешка"], ownedPieces: ["Пешка"], ownedSkins: ["Дерево"] },
      createdAt: new Date().toISOString()
    };
    accounts.push(account);
    await persist();
    return { status: 201, body: { token: issueToken(account), account: publicProfile(account) } };
  }

  async function login({ username, password }) {
    await load();
    const cleanName = String(username || "").trim().toLowerCase();
    const account = accounts.find(item => item.username.toLowerCase() === cleanName);
    if (!account || typeof password !== "string") return { status: 401, body: { error: "INVALID_CREDENTIALS" } };
    const candidate = await new Promise((resolve, reject) => {
      crypto.scrypt(password, Buffer.from(account.salt, "hex"), 64, (error, derived) => error ? reject(error) : resolve(derived.toString("hex")));
    });
    if (!safeEqual(candidate, account.passwordHash)) return { status: 401, body: { error: "INVALID_CREDENTIALS" } };
    return { status: 200, body: { token: issueToken(account), account: publicProfile(account) } };
  }

  async function me(token) {
    await load();
    const account = verifyToken(token);
    return account ? { status: 200, body: { account: publicProfile(account) } } : { status: 401, body: { error: "UNAUTHORIZED" } };
  }

  function cityPayload(account) {
    const city = ensureCity(account);
    return {
      wallet: { ...city.wallet },
      unlockedPieces: [...city.unlockedPieces],
      ownedPieces: [...city.ownedPieces],
      ownedSkins: [...city.ownedSkins],
      pieceCatalog: Object.fromEntries(Object.entries(CITY_PIECES).map(([name,cost])=>[name,{...cost,unlocked:city.unlockedPieces.includes(name),owned:city.ownedPieces.includes(name)}])),
      skinCatalog: Object.fromEntries(Object.entries(CITY_SKINS).map(([name,cost])=>[name,{...cost,owned:city.ownedSkins.includes(name)}]))
    };
  }

  async function cityProfile(token) {
    await load();
    const account = verifyToken(token);
    return account ? { status: 200, body: { city: cityPayload(account) } } : { status: 401, body: { error: "UNAUTHORIZED" } };
  }

  async function cityUnlockPiece(token, piece) {
    await load();
    const account = verifyToken(token);
    if (!account) return { status: 401, body: { error: "UNAUTHORIZED" } };
    const city = ensureCity(account), cost = CITY_PIECES[String(piece)];
    if (!cost) return { status: 400, body: { error: "UNKNOWN_PIECE" } };
    if (city.unlockedPieces.includes(piece)) return { status: 409, body: { error: "PIECE_ALREADY_UNLOCKED", city: cityPayload(account) } };
    if (city.wallet.xp < cost.xp) return { status: 409, body: { error: "NOT_ENOUGH_XP", required: cost.xp, available: city.wallet.xp } };
    city.wallet.xp -= cost.xp;
    city.unlockedPieces.push(piece);
    await persist();
    return { status: 200, body: { city: cityPayload(account), unlocked: piece } };
  }

  async function cityPurchasePiece(token, piece) {
    await load();
    const account = verifyToken(token);
    if (!account) return { status: 401, body: { error: "UNAUTHORIZED" } };
    const city = ensureCity(account), cost = CITY_PIECES[String(piece)];
    if (!cost) return { status: 400, body: { error: "UNKNOWN_PIECE" } };
    if (!city.unlockedPieces.includes(piece)) return { status: 409, body: { error: "PIECE_LOCKED" } };
    if (city.ownedPieces.includes(piece)) return { status: 409, body: { error: "PIECE_ALREADY_OWNED", city: cityPayload(account) } };
    if (city.wallet.zloty < cost.zloty) return { status: 409, body: { error: "NOT_ENOUGH_ZLOTY", required: cost.zloty, available: city.wallet.zloty } };
    city.wallet.zloty -= cost.zloty;
    city.ownedPieces.push(piece);
    await persist();
    return { status: 200, body: { city: cityPayload(account), purchased: piece } };
  }

  async function cityPurchaseSkin(token, skin) {
    await load();
    const account = verifyToken(token);
    if (!account) return { status: 401, body: { error: "UNAUTHORIZED" } };
    const city = ensureCity(account), cost = CITY_SKINS[String(skin)];
    if (!cost) return { status: 400, body: { error: "UNKNOWN_SKIN" } };
    if (city.ownedSkins.includes(skin)) return { status: 409, body: { error: "SKIN_ALREADY_OWNED", city: cityPayload(account) } };
    if (city.wallet.xp < cost.xp) return { status: 409, body: { error: "NOT_ENOUGH_XP", required: cost.xp, available: city.wallet.xp } };
    if (city.wallet.zloty < cost.zloty) return { status: 409, body: { error: "NOT_ENOUGH_ZLOTY", required: cost.zloty, available: city.wallet.zloty } };
    city.wallet.xp -= cost.xp;
    city.wallet.zloty -= cost.zloty;
    city.ownedSkins.push(skin);
    await persist();
    return { status: 200, body: { city: cityPayload(account), purchasedSkin: skin } };
  }

  async function reserveClassicMatchPiece(token, piece) {
    await load();
    const account = verifyToken(token);
    if (!account) return { status: 401, body: { error: "UNAUTHORIZED" } };
    const costs = { "Пешка": 0, "Конь": 0, "Слон": 0, "Ладья": 0, "Ферзь": 0, "Король": 0 };
    if (!Object.hasOwn(costs, piece)) return { status: 400, body: { error: "UNKNOWN_PIECE" } };
    const city = ensureCity(account), cost = costs[piece];
    if (city.wallet.zloty < cost) return { status: 409, body: { error: "NOT_ENOUGH_ZLOTY", required: cost, available: city.wallet.zloty } };
    city.wallet.zloty -= cost;
    await persist();
    return { status: 200, body: { cost, wallet: { ...city.wallet } } };
  }

  async function refundClassicMatchPieceById(playerId, cost) {
    await load();
    const account = accounts.find(item => item.id === playerId);
    if (!account) return false;
    const city = ensureCity(account);
    city.wallet.zloty += Math.max(0, Number(cost) || 0);
    await persist();
    return true;
  }

  async function awardMatchById(players, winnerTeam) {
    await load();
    const results = [];
    for (const player of players || []) {
      const account = accounts.find(item => item.id === player.playerId);
      if (!account) continue;
      const city = ensureCity(account);
      const won = winnerTeam === player.team;
      const reward = calculateMatchReward({ winnerTeam, playerTeam: player.team, stats: player.stats || {} });
      const xp = reward.xp;
      const zloty = reward.zloty;
      city.wallet.xp += xp;
      city.wallet.zloty += zloty;
      account.matches = (account.matches || 0) + 1;
      if (winnerTeam === "draw") account.draws = (account.draws || 0) + 1;
      else if (won) account.wins = (account.wins || 0) + 1;
      else account.losses = (account.losses || 0) + 1;
      results.push({ playerId: account.id, xp, zloty, won, result: reward.result, accuracy: reward.accuracy, moves: reward.moves, captures: reward.captures, checks: reward.checks, voteAccuracy: reward.voteAccuracy, breakdown: reward.breakdown, city: cityPayload(account) });
    }
    if (results.length) await persist();
    return results;
  }

  async function leaderboard(limit = 50) {
    await load();
    const rows = [...accounts]
      .sort((a, b) => b.rating - a.rating || b.wins - a.wins || a.username.localeCompare(b.username))
      .slice(0, Math.max(1, Math.min(100, limit)))
      .map((account, index) => ({ rank: index + 1, ...publicProfile(account) }));
    return rows;
  }

  return { register, login, me, leaderboard, cityProfile, cityUnlockPiece, cityPurchasePiece, cityPurchaseSkin, awardMatchById, reserveClassicMatchPiece, refundClassicMatchPieceById };
}
