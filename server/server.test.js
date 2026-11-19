import test from "node:test";
import assert from "node:assert/strict";
import { createMatchmakingServer } from "./server.js";

async function withServer(fn) {
  const server = createMatchmakingServer();
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  try { await fn("http://127.0.0.1:" + address.port); }
  finally { await new Promise(resolve => server.close(resolve)); }
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

test("quick matchmaking pairs two players in the same mode", async () => {
  await withServer(async base => {
    const enqueue = async (playerId, ip) => fetch(base + "/matchmaking/queue", {
      method: "POST",
      headers: { "content-type": "application/json", "x-forwarded-for": ip },
      body: JSON.stringify({ playerId, mode: "classic", port: 24567, rating: 1000 })
    }).then(r => r.json());
    const first = await enqueue("p1", "203.0.113.1");
    assert.equal(first.status, "waiting");
    const second = await enqueue("p2", "203.0.113.2");
    assert.equal(second.status, "matched");
    assert.equal(second.role, "guest");
    const status = await fetch(base + "/matchmaking/queue/" + first.ticket).then(r => r.json());
    assert.equal(status.status, "matched");
    assert.equal(status.role, "host");
    assert.equal(status.code, second.code);
  });
});
