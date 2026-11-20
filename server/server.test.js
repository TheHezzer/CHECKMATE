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

test("first move vote resolves after 16 unique votes and picks a random player from winning side",async()=>withServer(async base=>{
 const roles=["Ладья","Ладья","Ладья","Ладья","Конь","Конь","Конь","Конь","Слон","Слон","Слон","Слон","Ферзь","Ферзь","Король","Король"];
 let matchResponse;
 for(let i=0;i<16;i++) matchResponse=await queue(base,"vote-player-"+i,1000,roles[i]);
 assert.equal(matchResponse.data.status,"matched");
 const matchId=matchResponse.data.matchId;
 for(let i=0;i<15;i++){
   const player=matchResponse.data.players[i];
   const vote=await fetch(base+"/matches/"+matchId+"/first-move-vote",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({playerId:player.playerId,vote:i<10?"white":"black"})});
   const result=await vote.json();assert.equal(vote.status,200);assert.equal(result.resolved,false);
 }
 const duplicate=await fetch(base+"/matches/"+matchId+"/first-move-vote",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({playerId:matchResponse.data.players[0].playerId,vote:"black"})});
 assert.equal(duplicate.status,409);
 const lastPlayer=matchResponse.data.players[15];
 const final=await fetch(base+"/matches/"+matchId+"/first-move-vote",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({playerId:lastPlayer.playerId,vote:"white"})});
 const resolved=await final.json();assert.equal(final.status,200);assert.equal(resolved.resolved,true);assert.equal(resolved.startingTeam,"white");
 assert.ok(matchResponse.data.players.some(p=>p.playerId===resolved.startingPlayerId&&p.team==="white"));
}));
