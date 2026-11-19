import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

const TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60;

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

  async function leaderboard(limit = 50) {
    await load();
    const rows = [...accounts]
      .sort((a, b) => b.rating - a.rating || b.wins - a.wins || a.username.localeCompare(b.username))
      .slice(0, Math.max(1, Math.min(100, limit)))
      .map((account, index) => ({ rank: index + 1, ...publicProfile(account) }));
    return rows;
  }

  return { register, login, me, leaderboard };
}
