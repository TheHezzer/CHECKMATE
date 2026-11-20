from pathlib import Path

root = Path(__file__).resolve().parent.parent
accounts = root / "server" / "accounts.js"
a = accounts.read_text(encoding="utf-8")
if 'import { calculateMatchReward } from "./rewards.js";' not in a:
    a = a.replace('import path from "node:path";', 'import path from "node:path";\nimport { calculateMatchReward } from "./rewards.js";', 1)
old = '''      const won = winnerTeam === player.team;
      const xp = won ? 100 : 50;
      const zloty = won ? 200 : 100;
      city.wallet.xp += xp;
      city.wallet.zloty += zloty;'''
new = '''      const won = winnerTeam === player.team;
      const reward = calculateMatchReward({ winnerTeam, playerTeam: player.team, stats: player.stats || {} });
      const xp = reward.xp;
      const zloty = reward.zloty;
      city.wallet.xp += xp;
      city.wallet.zloty += zloty;'''
if old not in a: raise SystemExit("Fixed reward block not found")
a = a.replace(old,new,1)
a = a.replace(
    'results.push({ playerId: account.id, xp, zloty, won, city: cityPayload(account) });',
    'results.push({ playerId: account.id, xp, zloty, won, result: reward.result, accuracy: reward.accuracy, moves: reward.moves, captures: reward.captures, checks: reward.checks, voteAccuracy: reward.voteAccuracy, breakdown: reward.breakdown, city: cityPayload(account) });',
    1
)
accounts.write_text(a, encoding="utf-8")

server = root / "server" / "server.js"
s = server.read_text(encoding="utf-8")
old = '''        if(req.method==="GET"&&action==="state"){
          const state=getGameState(match,playerId);
          return state?send(res,200,state):send(res,404,{error:"MATCH_NOT_FOUND"});
        }'''
new = '''        if(req.method==="GET"&&action==="state"){
          const state=getGameState(match,playerId);
          if(state&&match.rewardResults){
            state.reward=match.rewardResults.find(item=>item.playerId===playerId)||null;
          }
          return state?send(res,200,state):send(res,404,{error:"MATCH_NOT_FOUND"});
        }'''
if old not in s: raise SystemExit("State route anchor missing")
s = s.replace(old,new,1)
old = '''          if(result.status===200&&match.game.status==="finished"&&!match.rewardsPaid){
            await accounts.awardMatchById(match.game.players,match.game.winnerTeam);
            match.rewardsPaid=true;
          }
          return send(res,result.status,result.state||{error:result.error});'''
new = '''          if(result.status===200&&match.game.status==="finished"&&!match.rewardsPaid){
            match.rewardResults=await accounts.awardMatchById(match.game.players,match.game.winnerTeam);
            match.rewardsPaid=true;
          }
          if(result.state&&match.rewardResults){
            result.state.reward=match.rewardResults.find(item=>item.playerId===playerId)||null;
          }
          return send(res,result.status,result.state||{error:result.error});'''
if old not in s: raise SystemExit("Match reward route anchor missing")
s = s.replace(old,new,1)
server.write_text(s, encoding="utf-8")
print("CHECKMATE v38: dynamic match rewards and reward details in game state applied.")
