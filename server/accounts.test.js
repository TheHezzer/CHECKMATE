import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { createMatchmakingServer } from "./server.js";

async function withAccountServer(fn, overrides = {}) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), "checkmate-accounts-"));
  const options = { dataFile: path.join(dir, "accounts.json"), tokenSecret: "test-secret-for-account-api", ...overrides };
  const server = createMatchmakingServer(options);
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const base = "http://127.0.0.1:" + server.address().port;
  try { await fn(base, options); }
  finally {
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve));
    await fs.rm(dir, { recursive: true, force: true });
  }
}

async function post(base, endpoint, body) {
  const response = await fetch(base + endpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });
  return { status: response.status, data: await response.json() };
}

test("account registration creates a persistent bronze profile and bearer token", async () => {
  await withAccountServer(async base => {
    const result = await post(base, "/accounts/register", { username: "Knight_01", password: "safe-pass-123" });
    assert.equal(result.status, 201);
    assert.equal(result.data.account.username, "Knight_01");
    assert.equal(result.data.account.rating, 1000);
    assert.equal(result.data.account.division, "Bronze");
    assert.equal(result.data.account.matches, 0);
    assert.ok(result.data.token);
    const me = await fetch(base + "/account/me", { headers: { authorization: "Bearer " + result.data.token } });
    assert.equal(me.status, 200);
    assert.equal((await me.json()).account.playerId, result.data.account.playerId);
  });
});

test("registration rejects duplicate usernames and weak passwords", async () => {
  await withAccountServer(async base => {
    assert.equal((await post(base, "/accounts/register", { username: "player1", password: "short" })).status, 400);
    assert.equal((await post(base, "/accounts/register", { username: "player1", password: "password-123" })).status, 201);
    assert.equal((await post(base, "/accounts/register", { username: "PLAYER1", password: "password-456" })).status, 409);
  });
});

test("login verifies password and invalid credentials do not reveal account existence", async () => {
  await withAccountServer(async base => {
    await post(base, "/accounts/register", { username: "Rook_77", password: "correct-horse-7" });
    const ok = await post(base, "/accounts/login", { username: "rook_77", password: "correct-horse-7" });
    assert.equal(ok.status, 200);
    assert.ok(ok.data.token);
    const bad = await post(base, "/accounts/login", { username: "rook_77", password: "wrong-password" });
    const missing = await post(base, "/accounts/login", { username: "missing", password: "wrong-password" });
    assert.equal(bad.status, 401);
    assert.deepEqual(bad.data, missing.data);
  });
});

test("account data survives server restart and appears in leaderboard", async () => {
  await withAccountServer(async (base, options) => {
    const created = await post(base, "/accounts/register", { username: "TopPlayer", password: "very-safe-123" });
    const id = created.data.account.playerId;
    const server2 = createMatchmakingServer(options);
    await new Promise(resolve => server2.listen(0, "127.0.0.1", resolve));
    try {
      const base2 = "http://127.0.0.1:" + server2.address().port;
      const login = await post(base2, "/accounts/login", { username: "TopPlayer", password: "very-safe-123" });
      assert.equal(login.status, 200);
      assert.equal(login.data.account.playerId, id);
      const board = await fetch(base2 + "/leaderboard").then(r => r.json());
      assert.equal(board.players[0].username, "TopPlayer");
      assert.equal(board.players[0].rank, 1);
    } finally {
      server2.closeAllConnections();
      await new Promise(resolve => server2.close(resolve));
    }
  });
});

test("account endpoint rejects missing or invalid bearer token", async () => {
  await withAccountServer(async base => {
    const response = await fetch(base + "/account/me", { headers: { authorization: "Bearer invalid.token" } });
    assert.equal(response.status, 401);
  });
});

test("only configured admin can grant resources to another account", async () => {
  const adminPassword = "secure-admin-password-2026";
  await withAccountServer(async base => {
    const admin = await post(base, "/accounts/register", { username: "TheHezzer", password: adminPassword });
    const player = await post(base, "/accounts/register", { username: "TestPlayer", password: "player-password-123" });
    assert.equal(admin.status, 201);
    assert.equal(admin.data.account.isAdmin, true);
    assert.equal(player.data.account.isAdmin, false);
    const denied = await fetch(base + "/admin/grant", {
      method: "POST", headers: { "content-type": "application/json", authorization: "Bearer " + player.data.token },
      body: JSON.stringify({ username: "TestPlayer", zloty: 100, xp: 50 })
    });
    assert.equal(denied.status, 403);
    const granted = await fetch(base + "/admin/grant", {
      method: "POST", headers: { "content-type": "application/json", authorization: "Bearer " + admin.data.token },
      body: JSON.stringify({ username: "TestPlayer", zloty: 1000, xp: 250, gambits: 10 })
    });
    assert.equal(granted.status, 200);
    assert.equal((await granted.json()).wallet.zloty, 13750);
    const profile = await fetch(base + "/city/profile", { headers: { authorization: "Bearer " + player.data.token } }).then(r => r.json());
    assert.equal(profile.city.wallet.xp, 1100);
    assert.equal(profile.city.wallet.gambits, 10);
  }, { adminUsername: "TheHezzer", adminPassword });
});


test("match notifications are persistent, readable and can be marked as read", async () => {
  await withAccountServer(async base => {
    const created = await post(base, "/accounts/register", { username: "NotifyPlayer", password: "notify-pass-123" });
    const headers = { "content-type": "application/json", authorization: "Bearer " + created.data.token };
    const pushed = await fetch(base + "/notifications", { headers });
    assert.equal(pushed.status, 200);
    assert.deepEqual((await pushed.json()).notifications, []);
    const saved = await fetch(base + "/notifications/read", {
      method: "POST", headers, body: JSON.stringify({ ids: [] })
    });
    assert.equal(saved.status, 200);
  });
});

test("rating settlement updates each account once and applies abandonment penalty", async () => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), "checkmate-rating-"));
  const options = { dataFile: path.join(dir, "accounts.json"), tokenSecret: "rating-test-secret" };
  try {
    const { createAccountService } = await import("./accounts.js");
    const service = createAccountService(options);
    const a = await service.register({ username: "RatingWhite", password: "rating-pass-123" });
    const b = await service.register({ username: "RatingBlack", password: "rating-pass-123" });
    const players = [
      { playerId: a.body.account.playerId, team: "white", abandoned: true },
      { playerId: b.body.account.playerId, team: "black", abandoned: false }
    ];
    const results = await service.applyMatchRatingById(players, "black");
    assert.equal(results.length, 2);
    assert.equal(results.find(x => x.playerId === a.body.account.playerId).abandonmentPenalty, 20);
    const meA = await service.me(a.body.token);
    const meB = await service.me(b.body.token);
    assert.equal(meA.body.account.matches, 1);
    assert.equal(meB.body.account.matches, 1);
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
});
