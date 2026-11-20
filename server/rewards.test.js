import test from "node:test";
import assert from "node:assert/strict";
import { calculateMatchReward } from "./rewards.js";

test("strong individual performance earns more than an inactive loss", () => {
  const inactive = calculateMatchReward({ winnerTeam: "black", playerTeam: "white", stats: {} });
  const strong = calculateMatchReward({ winnerTeam: "black", playerTeam: "white", stats: {
    moves: 8, captures: 3, checks: 2, qualityTotal: 760
  } });
  assert.ok(strong.xp > inactive.xp);
  assert.ok(strong.zloty > inactive.zloty);
  assert.equal(strong.accuracy, 95);
});

test("team result matters, but a high-quality losing player still earns a performance bonus", () => {
  const win = calculateMatchReward({ winnerTeam: "white", playerTeam: "white", stats: { moves: 4, qualityTotal: 360 } });
  const loss = calculateMatchReward({ winnerTeam: "white", playerTeam: "black", stats: { moves: 4, qualityTotal: 360 } });
  assert.ok(win.xp > loss.xp);
  assert.ok(loss.xp > calculateMatchReward({ winnerTeam: "white", playerTeam: "black", stats: {} }).xp);
});

test("voting bonus requires at least three votes and 75 percent accuracy", () => {
  const noVotes = calculateMatchReward({ winnerTeam: "draw", playerTeam: "white", stats: { moves: 3, qualityTotal: 240 } });
  const badVotes = calculateMatchReward({ winnerTeam: "draw", playerTeam: "white", stats: { moves: 3, qualityTotal: 240, votes: 4, correctVotes: 2 } });
  const goodVotes = calculateMatchReward({ winnerTeam: "draw", playerTeam: "white", stats: { moves: 3, qualityTotal: 240, votes: 4, correctVotes: 3 } });
  assert.equal(badVotes.breakdown.voting.xp, 0);
  assert.ok(goodVotes.xp > noVotes.xp);
  assert.equal(goodVotes.breakdown.voting.zloty, 24);
});

test("reward values are capped by quality and tactical event limits", () => {
  const reward = calculateMatchReward({ winnerTeam: "white", playerTeam: "white", stats: {
    moves: 100, captures: 100, checks: 100, checkmates: 10, promotions: 20, qualityTotal: 10000
  } });
  assert.equal(reward.accuracy, 100);
  assert.equal(reward.breakdown.tactics.xp, 20);
  assert.equal(reward.breakdown.tactics.zloty, 40);
});

test("even an inactive Chess City loss receives the participation share", () => {
  const reward = calculateMatchReward({ winnerTeam: "black", playerTeam: "white", stats: {} });
  assert.equal(reward.zloty, 175);
  assert.equal(reward.xp, 88);
});

test("win, draw and loss use the agreed Chess City reward scale", () => {
  const win = calculateMatchReward({ winnerTeam: "white", playerTeam: "white", stats: { moves: 3 } });
  const draw = calculateMatchReward({ winnerTeam: "draw", playerTeam: "white", stats: { moves: 3 } });
  const loss = calculateMatchReward({ winnerTeam: "black", playerTeam: "white", stats: { moves: 3 } });
  assert.ok(win.xp > draw.xp && draw.xp > loss.xp);
  assert.ok(win.zloty > draw.zloty && draw.zloty > loss.zloty);
});
