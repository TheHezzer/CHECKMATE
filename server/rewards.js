const QUALITY_BONUSES = [
  { minimum: 92, xp: 35, zloty: 70 },
  { minimum: 85, xp: 28, zloty: 55 },
  { minimum: 75, xp: 20, zloty: 40 },
  { minimum: 65, xp: 10, zloty: 20 }
];

export function calculateMatchReward({ winnerTeam, playerTeam, stats = {} }) {
  const result = winnerTeam === "draw" ? "draw" : winnerTeam === playerTeam ? "win" : "loss";
  const base = result === "win" ? { xp: 400, zloty: 800 }
    : result === "draw" ? { xp: 325, zloty: 650 }
    : { xp: 250, zloty: 500 };

  const moves = Math.max(0, Number(stats.moves) || 0);
  const captures = Math.max(0, Number(stats.captures) || 0);
  const checks = Math.max(0, Number(stats.checks) || 0);
  const checkmates = Math.max(0, Number(stats.checkmates) || 0);
  const promotions = Math.max(0, Number(stats.promotions) || 0);
  const quality = moves ? Math.max(0, Math.min(100, (Number(stats.qualityTotal) || 0) / moves)) : 0;
  const qualityBonus = QUALITY_BONUSES.find(item => quality >= item.minimum) || { xp: 0, zloty: 0 };

  const tacticalXp = Math.min(20, captures * 2 + checks * 3 + checkmates * 8 + promotions * 4);
  const tacticalZloty = Math.min(40, captures * 4 + checks * 6 + checkmates * 16 + promotions * 8);
  const voteCount = Math.max(0, Number(stats.votes) || 0);
  const correctVotes = Math.max(0, Math.min(voteCount, Number(stats.correctVotes) || 0));
  const voteAccuracy = voteCount ? correctVotes / voteCount : 0;
  const voteBonus = voteCount >= 3 && voteAccuracy >= 0.75 ? { xp: 12, zloty: 24 } : { xp: 0, zloty: 0 };
  const participation = moves >= 3 ? 1 : moves > 0 ? 0.65 : 0.35;
  const participationXp = moves >= 3 ? 8 : moves > 0 ? 4 : 0;
  const participationZloty = moves >= 3 ? 15 : moves > 0 ? 8 : 0;

  const xp = Math.round((base.xp + qualityBonus.xp + tacticalXp + voteBonus.xp + participationXp) * participation);
  const zloty = Math.max(0, Math.round((base.zloty + qualityBonus.zloty + tacticalZloty + voteBonus.zloty + participationZloty) * participation));
  return {
    result, xp, zloty, accuracy: Math.round(quality), moves, captures, checks,
    voteAccuracy: Math.round(voteAccuracy * 100),
    breakdown: {
      base, quality: { ...qualityBonus, accuracy: Math.round(quality) },
      tactics: { xp: tacticalXp, zloty: tacticalZloty },
      voting: voteBonus, participation: { xp: participationXp, zloty: participationZloty, factor: participation }
    }
  };
}
