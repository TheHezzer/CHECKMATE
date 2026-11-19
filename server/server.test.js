import test from "node:test";
import assert from "node:assert/strict";
import { createMatchmakingServer } from "./server.js";

async function withServer(fn) {
  const server = createMatchmakingServer();
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  try { await fn("http://127.0.0.1:" + address.port); }
  finally { server.closeAllConnections(); await new Promise(resolve => server.close(resolve)); }
}

async function queue(base, playerId, rating, mode = "classic", ip = "203.0.113.1") {
  const response = await fetch(base + "/matchmaking/queue", {
    method: "POST",
    headers: { "content-type": "application/json", "x-forwarded-for": ip },
    body: JSON.stringify({ playerId, mode, port: 24567, rating })
  });
  return { status: response.status, data: await response.json() };
}

test("health endpoint reports service", async () => {
  await withServer(async base => {
    const response = await fetch(base + "/health");
    assert.equal(response.status, 200);
    assert.equal((await response.json()).ok, true);
  });
});

test("private room can be created and joined once", async () => {
  await withServer(async base => {
    const created = await fetch(base + "/rooms", {
      method: "POST", headers: { "content-type": "application/json", "x-forwarded-for": "203.0.113.8" },
      body: JSON.stringify({ playerId: "host-1", port: 24567 })
    });
    assert.equal(created.status, 201);
    const room = await created.json();
    assert.match(room.code, /^[A-Z2-9]{6}$/);
    assert.equal(room.host, "203.0.113.8");
    const joined = await fetch(base + "/rooms/" + room.code + "/join", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ playerId: "guest-1" })
    });
    assert.equal(joined.status, 200);
    assert.equal((await joined.json()).joined, true);
    const second = await fetch(base + "/rooms/" + room.code + "/join", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ playerId: "guest-2" })
    });
    assert.equal(second.status, 409);
  });
});

test("quick matchmaking pairs only players within the initial rating gap", async () => {
  await withServer(async base => {
    const first = await queue(base, "p1", 1000, "classic", "203.0.113.1");
    assert.equal(first.data.status, "waiting");
    const tooStrong = await queue(base, "p2", 1600, "classic", "203.0.113.2");
    assert.equal(tooStrong.data.status, "waiting");
    const close = await queue(base, "p3", 1080, "classic", "203.0.113.3");
    assert.equal(close.data.status, "matched");
    assert.equal(close.data.ratingDifference, 80);
    const firstStatus = await fetch(base + "/matchmaking/queue/" + first.data.ticket).then(r => r.json());
    assert.equal(firstStatus.status, "matched");
    const strongStatus = await fetch(base + "/matchmaking/queue/" + tooStrong.data.ticket).then(r => r.json());
    assert.equal(strongStatus.status, "waiting");
  });
});

test("quick matchmaking never pairs different game modes", async () => {
  await withServer(async base => {
    const classic = await queue(base, "p1", 1000, "classic");
    const city = await queue(base, "p2", 1000, "chess_city", "203.0.113.2");
    assert.equal(classic.data.status, "waiting");
    assert.equal(city.data.status, "waiting");
  });
});

test("a player can cancel a waiting matchmaking ticket", async () => {
  await withServer(async base => {
    const waiting = await queue(base, "cancel-me", 1000, "cancel_test");
    assert.equal(waiting.data.status, "waiting");
    const cancelled = await fetch(base + "/matchmaking/queue/" + waiting.data.ticket + "/cancel", { method: "POST" });
    assert.equal(cancelled.status, 200);
    assert.equal((await cancelled.json()).status, "cancelled");
    const status = await fetch(base + "/matchmaking/queue/" + waiting.data.ticket).then(r => r.json());
    assert.equal(status.status, "cancelled");
  });
});
