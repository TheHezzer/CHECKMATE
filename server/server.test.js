import test from "node:test";
import assert from "node:assert/strict";
import { createMatchmakingServer } from "./server.js";
async function withServer(fn){const s=createMatchmakingServer();await new Promise(r=>s.listen(0,"127.0.0.1",r));const a=s.address();try{await fn("http://127.0.0.1:"+a.port)}finally{s.closeAllConnections();await new Promise(r=>s.close(r))}}
async function queue(base,id,rating,piece="Конь",mode="classic"){const r=await fetch(base+"/matchmaking/queue",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({playerId:id,playerName:"Player_"+id,mode,rating,piece})});return{status:r.status,data:await r.json()}}
test("health endpoint reports service",async()=>withServer(async base=>{const r=await fetch(base+"/health");assert.equal(r.status,200);assert.equal((await r.json()).ok,true)}));
test("manual room creation is disabled",async()=>withServer(async base=>{const r=await fetch(base+"/rooms",{method:"POST",headers:{"content-type":"application/json"},body:"{}"});assert.equal(r.status,404)}));
test("classic matchmaking creates 8v8 teams with a pawn and selected second piece per player",async()=>withServer(async base=>{
 let first;let n=0;
 const roles=["Ладья","Ладья","Ладья","Ладья","Конь","Конь","Конь","Конь","Слон","Слон","Слон","Слон","Ферзь","Ферзь","Король","Король"];
 for(let i=0;i<16;i++){
   const r=await queue(base,"p"+i,1000+(i%8)*5,roles[i%roles.length]);
   if(i===0)first=r;
   if(i<15)assert.equal(r.data.status,"waiting");else assert.equal(r.data.status,"matched");
   n++;
 }
 const s=await fetch(base+"/matchmaking/queue/"+first.data.ticket).then(r=>r.json());
 assert.equal(s.status,"matched");assert.equal(s.players.length,16);
 const white=s.players.filter(p=>p.team==="white"),black=s.players.filter(p=>p.team==="black");
 assert.equal(white.length,8);assert.equal(black.length,8);
 assert.equal(new Set(s.players.map(p=>p.playerId)).size,16);
 assert.equal(s.startingTeam,"white");
 assert.ok(s.players.some(p=>p.playerId===s.startingPlayerId&&p.team==="white"));
 for(const player of s.players){
   assert.deepEqual(player.pieces,["Пешка",player.secondPiece]);
   assert.equal(player.piece,player.secondPiece);
   assert.ok(roles.includes(player.secondPiece));
 }
 assert.deepEqual(Object.fromEntries(["Ладья","Конь","Слон","Ферзь","Король"].map(piece=>[piece,white.filter(p=>p.secondPiece===piece).length])),{"Ладья":2,"Конь":2,"Слон":2,"Ферзь":1,"Король":1});
 assert.deepEqual(Object.fromEntries(["Ладья","Конь","Слон","Ферзь","Король"].map(piece=>[piece,black.filter(p=>p.secondPiece===piece).length])),{"Ладья":2,"Конь":2,"Слон":2,"Ферзь":1,"Король":1});
}));
test("matchmaking never mixes game modes",async()=>withServer(async base=>{
 let cityFirst;for(let i=0;i<7;i++){const c=await queue(base,"c"+i,1000,"Конь","classic");const s=await queue(base,"s"+i,1000,"Конь","chess_city");if(i===0)cityFirst=s;assert.equal(c.data.status,i<4?"waiting":"waiting_piece_slot");assert.equal(s.data.status,i<4?"waiting":"waiting_piece_slot")}
 const cStatus=await fetch(base+"/matchmaking/queue/"+(await queue(base,"c-last",1000,"Конь","classic")).data.ticket).then(r=>r.json());assert.equal(cStatus.status,"waiting_piece_slot");
 const cityStatus=await fetch(base+"/matchmaking/queue/"+cityFirst.data.ticket).then(r=>r.json());assert.equal(cityStatus.status,"waiting");
}));
test("waiting roster returns player nicknames, ratings and chosen piece",async()=>withServer(async base=>{
 const a=await queue(base,"alpha",1000,"Конь","roster_test"),b=await queue(base,"bravo",1070,"Конь","roster_test");const s=await fetch(base+"/matchmaking/queue/"+a.data.ticket).then(r=>r.json());assert.equal(s.players.length,2);assert.ok(s.players.some(p=>p.name==="Player_alpha"));assert.ok(s.players.some(p=>p.rating===1070));assert.ok(s.players.every(p=>p.pieces[0]==="Пешка"&&p.pieces[1]==="Конь"));assert.equal(s.requiredPlayers,16);
}));
test("invalid chess piece is rejected",async()=>withServer(async base=>{const r=await queue(base,"bad-piece",1000,"Дракон");assert.equal(r.status,400)}));
test("a player can cancel a waiting ticket",async()=>withServer(async base=>{
 const w=await queue(base,"cancel-me",1000);const c=await fetch(base+"/matchmaking/queue/"+w.data.ticket+"/cancel",{method:"POST"});assert.equal(c.status,200);assert.equal((await c.json()).status,"cancelled");assert.equal((await fetch(base+"/matchmaking/queue/"+w.data.ticket).then(r=>r.json())).status,"cancelled");
}));

test("overbooked piece offers waitlist status and exposes remaining slots",async()=>withServer(async base=>{
 const a=await queue(base,"queen-a",1000,"Ферзь"),b=await queue(base,"queen-b",1000,"Ферзь"),c=await queue(base,"queen-c",1000,"Ферзь");
 assert.equal(a.data.status,"waiting");assert.equal(b.data.status,"waiting");assert.equal(c.data.status,"waiting_piece_slot");
 assert.equal(c.data.pieceCapacity["Ферзь"].selected,3);
 assert.equal(c.data.pieceCapacity["Ферзь"].capacity,2);
 assert.equal(c.data.pieceCapacity["Ферзь"].available,0);
 const polled=await fetch(base+"/matchmaking/queue/"+c.data.ticket).then(r=>r.json());
 assert.equal(polled.status,"waiting_piece_slot");
}));


test("Chess City keeps a separate XP unlock and permanent purchase inventory",async()=>withServer(async base=>{
 const registered=await fetch(base+"/accounts/register",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({username:"cityplayer",password:"securepass123"})}).then(r=>r.json());
 const headers={"content-type":"application/json","authorization":"Bearer "+registered.token};
 const initial=await fetch(base+"/city/profile",{headers}).then(r=>r.json());
 assert.deepEqual(initial.city.unlockedPieces,["Пешка"]);
 assert.deepEqual(initial.city.ownedPieces,["Пешка"]);
 const locked=await fetch(base+"/city/purchase-piece",{method:"POST",headers,body:JSON.stringify({piece:"Конь"})});
 assert.equal(locked.status,409);
 const unlock=await fetch(base+"/city/unlock-piece",{method:"POST",headers,body:JSON.stringify({piece:"Конь"})});
 assert.equal(unlock.status,200);
 assert.ok((await unlock.json()).city.unlockedPieces.includes("Конь"));
 const purchase=await fetch(base+"/city/purchase-piece",{method:"POST",headers,body:JSON.stringify({piece:"Конь"})});
 assert.equal(purchase.status,200);
 const final=await purchase.json();
 assert.ok(final.city.ownedPieces.includes("Конь"));
 assert.equal(final.city.wallet.xp,550);
 assert.equal(final.city.wallet.zloty,11850);
}));
test("Chess City skins remain locked until purchased with XP and zloty",async()=>withServer(async base=>{
 const registered=await fetch(base+"/accounts/register",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({username:"skinplayer",password:"securepass123"})}).then(r=>r.json());
 const headers={"content-type":"application/json","authorization":"Bearer "+registered.token};
 const initial=await fetch(base+"/city/profile",{headers}).then(r=>r.json());
 assert.deepEqual(initial.city.ownedSkins,["Дерево"]);
 const buy=await fetch(base+"/city/purchase-skin",{method:"POST",headers,body:JSON.stringify({skin:"Мрамор"})});
 assert.equal(buy.status,200);
 const city=(await buy.json()).city;
 assert.ok(city.ownedSkins.includes("Мрамор"));
 assert.equal(city.wallet.xp,600);
 assert.equal(city.wallet.zloty,11750);
}));

test("matched players receive private session tokens and can use the authoritative match API",async()=>withServer(async base=>{
 const roles=["Ладья","Ладья","Ладья","Ладья","Конь","Конь","Конь","Конь","Слон","Слон","Слон","Слон","Ферзь","Ферзь","Король","Король"];
 const ticketsByPlayer=new Map();
 for(let i=0;i<16;i++){
   const playerId="live"+i;
   const result=await queue(base,playerId,1000,roles[i],"live_api");
   ticketsByPlayer.set(playerId,result.data.ticket);
 }
 const firstTicket=ticketsByPlayer.get("live0");
 const matched=await fetch(base+"/matchmaking/queue/"+firstTicket).then(r=>r.json());
 assert.equal(matched.status,"matched");
 assert.ok(matched.playerSessionToken);
 const starter=matched.players.find(p=>p.playerId===matched.startingPlayerId);
 assert.ok(starter);
 const starterTicket=ticketsByPlayer.get(starter.playerId);
 assert.ok(starterTicket);
 const starterSession=await fetch(base+"/matchmaking/queue/"+starterTicket).then(r=>r.json());
 assert.ok(starterSession.playerSessionToken);
 const stateResponse=await fetch(base+"/matches/"+matched.matchId+"/state",{headers:{"x-player-session":starterSession.playerSessionToken}});
 assert.equal(stateResponse.status,200);
 const state=await stateResponse.json();
 assert.equal(state.activeTeam,"white");
 assert.equal(state.activePlayerId,"");
 assert.ok(state.openingVote);
 assert.equal(state.teamClocks.white,600000);
 assert.equal(state.teamClocks.black,600000);
 assert.equal(state.board.length,32);
 const whitePlayers=matched.players.filter(p=>p.team==="white").slice(0,5);
 for(const voter of whitePlayers){
   const voterSession=await fetch(base+"/matchmaking/queue/"+ticketsByPlayer.get(voter.playerId)).then(r=>r.json());
   const vote=await fetch(base+"/matches/"+matched.matchId+"/opening-vote",{method:"POST",headers:{"content-type":"application/json","x-player-session":voterSession.playerSessionToken},body:JSON.stringify({candidatePlayerId:starter.playerId})});
   assert.equal(vote.status,200);
 }
 const votedState=await fetch(base+"/matches/"+matched.matchId+"/state",{headers:{"x-player-session":starterSession.playerSessionToken}}).then(r=>r.json());
 assert.equal(votedState.activePlayerId,starter.playerId);
 assert.equal(votedState.openingVote,null);
 const move=await fetch(base+"/matches/"+matched.matchId+"/move",{method:"POST",headers:{"content-type":"application/json","x-player-session":starterSession.playerSessionToken},body:JSON.stringify({fromFile:starter.slot,fromRow:6,toFile:starter.slot,toRow:5})});
 assert.equal(move.status,200);
 const after=await move.json();
 assert.equal(after.activeTeam,"black");
 const denied=await fetch(base+"/matches/"+matched.matchId+"/state",{headers:{"x-player-session":"wrong-token"}});
 assert.equal(denied.status,401);
}));

test("Classic queue charges the consumable pawn-plus-knight bundle and refunds it on cancellation",async()=>withServer(async base=>{
 const registered=await fetch(base+"/accounts/register",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({username:"classicbuyer",password:"securepass123"})}).then(r=>r.json());
 const headers={"content-type":"application/json","authorization":"Bearer "+registered.token};
 const before=await fetch(base+"/city/profile",{headers}).then(r=>r.json());
 assert.equal(before.city.wallet.zloty,12750);
 const queued=await fetch(base+"/matchmaking/queue",{method:"POST",headers,body:JSON.stringify({playerId:"local-fake-id",playerName:"Buyer",piece:"Конь",mode:"reserve_test",rating:1000})}).then(r=>r.json());
 assert.equal(queued.status,"waiting");
 const afterQueue=await fetch(base+"/city/profile",{headers}).then(r=>r.json());
 assert.equal(afterQueue.city.wallet.zloty,12720);
 const cancelled=await fetch(base+"/matchmaking/queue/"+queued.ticket+"/cancel",{method:"POST",headers}).then(r=>r.json());
 assert.equal(cancelled.status,"cancelled");
 const afterCancel=await fetch(base+"/city/profile",{headers}).then(r=>r.json());
 assert.equal(afterCancel.city.wallet.zloty,12750);
}));
test("Classic entry bundle prices are consistent for every second-piece role",async()=>withServer(async base=>{
 const roles={"Конь":30,"Слон":35,"Ладья":40,"Король":45,"Ферзь":55};
 let index=0;
 for(const [piece,cost] of Object.entries(roles)){
   const name="pricebuyer"+index;
   index+=1;
   const registered=await fetch(base+"/accounts/register",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({username:name,password:"securepass123"})}).then(r=>r.json());
   const headers={"content-type":"application/json","authorization":"Bearer "+registered.token};
   const queued=await fetch(base+"/matchmaking/queue",{method:"POST",headers,body:JSON.stringify({piece,mode:"price_"+name,rating:1000})}).then(r=>r.json());
   assert.equal(queued.status,"waiting");
   const profile=await fetch(base+"/city/profile",{headers}).then(r=>r.json());
   assert.equal(profile.city.wallet.zloty,12750-cost);
 }
}));


test("abandoned team match finishes and sends a persistent result with rule warning and rating penalty",async()=>withServer(async base=>{
 const registered=await fetch(base+"/accounts/register",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({username:"LeaverTest",password:"leave-test-pass"})}).then(r=>r.json());
 const roles=["Ладья","Ладья","Ладья","Ладья","Конь","Конь","Конь","Конь","Слон","Слон","Слон","Слон","Ферзь","Ферзь","Король","Король"];
 const tickets=new Map();
 const playerId=registered.account.playerId;
 const accountQueue=await fetch(base+"/matchmaking/queue",{method:"POST",headers:{"content-type":"application/json",authorization:"Bearer "+registered.token},body:JSON.stringify({playerName:"LeaverTest",mode:"abandon_test",rating:1000,piece:"Ладья"})});
 assert.ok([200,201].includes(accountQueue.status));
 tickets.set(playerId,(await accountQueue.json()).ticket);
 for(let i=0;i<15;i++){
   const response=await queue(base,"abandon-bot-"+i,1000,roles[i],"abandon_test");
   tickets.set("abandon-bot-"+i,response.data.ticket);
 }
 const first=await fetch(base+"/matchmaking/queue/"+tickets.get(playerId)).then(r=>r.json());
 assert.equal(first.status,"matched");
 const sessions=new Map();
 for(const [id,ticket] of tickets){
   const status=await fetch(base+"/matchmaking/queue/"+ticket).then(r=>r.json());
   sessions.set(id,status.playerSessionToken);
 }
 const roster=first.players;
 const user=roster.find(p=>p.playerId===playerId);
 assert.ok(user);
 const white=roster.filter(p=>p.team==="white");
 for(const voter of white.slice(0,5)){
   const vote=await fetch(base+"/matches/"+first.matchId+"/opening-vote",{method:"POST",headers:{"content-type":"application/json","x-player-session":sessions.get(voter.playerId)},body:JSON.stringify({candidatePlayerId:white[0].playerId})});
   assert.equal(vote.status,200);
 }
 const abandonedTeam=roster.filter(p=>p.team===user.team);
 for(const player of abandonedTeam){
   const leave=await fetch(base+"/matches/"+first.matchId+"/leave",{method:"POST",headers:{"x-player-session":sessions.get(player.playerId)}});
   assert.equal(leave.status,200);
 }
 const inbox=await fetch(base+"/notifications",{headers:{authorization:"Bearer "+registered.token}}).then(r=>r.json());
 assert.equal(inbox.notifications.length,1);
 assert.equal(inbox.notifications[0].type,"match_result");
 assert.equal(inbox.notifications[0].data.abandoned,true);
 assert.ok(inbox.notifications[0].data.ratingDelta<0);
 assert.match(inbox.notifications[0].message,/запрещено правилами CHECKMATE/i);
}));
