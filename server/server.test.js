import test from "node:test";
import assert from "node:assert/strict";
import { createMatchmakingServer } from "./server.js";
async function withServer(fn){const s=createMatchmakingServer();await new Promise(r=>s.listen(0,"127.0.0.1",r));const a=s.address();try{await fn("http://127.0.0.1:"+a.port)}finally{s.closeAllConnections();await new Promise(r=>s.close(r))}}
async function queue(base,id,rating,piece="Пешка",mode="classic"){const r=await fetch(base+"/matchmaking/queue",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({playerId:id,playerName:"Player_"+id,mode,rating,piece})});return{status:r.status,data:await r.json()}}
test("health endpoint reports service",async()=>withServer(async base=>{const r=await fetch(base+"/health");assert.equal(r.status,200);assert.equal((await r.json()).ok,true)}));
test("manual room creation is disabled",async()=>withServer(async base=>{const r=await fetch(base+"/rooms",{method:"POST",headers:{"content-type":"application/json"},body:"{}"});assert.equal(r.status,404)}));
test("classic matchmaking waits for exact chess piece composition and balances 16v16 teams",async()=>withServer(async base=>{
 let first;const roles=[["Пешка",16],["Ладья",4],["Конь",4],["Слон",4],["Ферзь",2],["Король",2]];let n=0;
 for(const [piece,count] of roles)for(let i=0;i<count;i++){const r=await queue(base,"p"+n,1000+(n%8)*5,piece);if(n===0)first=r;if(n<31)assert.equal(r.data.status,"waiting");else assert.equal(r.data.status,"matched");n++}
 const s=await fetch(base+"/matchmaking/queue/"+first.data.ticket).then(r=>r.json());assert.equal(s.status,"matched");assert.equal(s.players.length,32);
 const white=s.players.filter(p=>p.team==="white"),black=s.players.filter(p=>p.team==="black");assert.equal(white.length,16);assert.equal(black.length,16);
 const counts={"Пешка":8,"Ладья":2,"Конь":2,"Слон":2,"Ферзь":1,"Король":1};
 for(const [piece,count] of Object.entries(counts)){assert.equal(white.filter(p=>p.piece===piece).length,count);assert.equal(black.filter(p=>p.piece===piece).length,count)}
 assert.equal(new Set(s.players.map(p=>p.playerId)).size,32);
 assert.ok(Math.abs(white.reduce((a,p)=>a+p.rating,0)-black.reduce((a,p)=>a+p.rating,0))<=40);
}));
test("matchmaking never mixes game modes",async()=>withServer(async base=>{
 let cityFirst;for(let i=0;i<31;i++){const c=await queue(base,"c"+i,1000,"Пешка","classic");const s=await queue(base,"s"+i,1000,"Пешка","chess_city");if(i===0)cityFirst=s;assert.equal(c.data.status,"waiting");assert.equal(s.data.status,"waiting")}
 const cStatus=await fetch(base+"/matchmaking/queue/"+(await queue(base,"c-last",1000,"Пешка","classic")).data.ticket).then(r=>r.json());assert.equal(cStatus.status,"waiting");
 const cityStatus=await fetch(base+"/matchmaking/queue/"+cityFirst.data.ticket).then(r=>r.json());assert.equal(cityStatus.status,"waiting");
}));
test("waiting roster returns player nicknames, ratings and chosen piece",async()=>withServer(async base=>{
 const a=await queue(base,"alpha",1000,"Пешка","roster_test"),b=await queue(base,"bravo",1070,"Пешка","roster_test");const s=await fetch(base+"/matchmaking/queue/"+a.data.ticket).then(r=>r.json());assert.equal(s.players.length,2);assert.ok(s.players.some(p=>p.name==="Player_alpha"));assert.ok(s.players.some(p=>p.rating===1070));assert.ok(s.players.every(p=>p.piece==="Пешка"));assert.equal(s.requiredPlayers,32);
}));
test("invalid chess piece is rejected",async()=>withServer(async base=>{const r=await queue(base,"bad-piece",1000,"Дракон");assert.equal(r.status,400)}));
test("a player can cancel a waiting ticket",async()=>withServer(async base=>{
 const w=await queue(base,"cancel-me",1000);const c=await fetch(base+"/matchmaking/queue/"+w.data.ticket+"/cancel",{method:"POST"});assert.equal(c.status,200);assert.equal((await c.json()).status,"cancelled");assert.equal((await fetch(base+"/matchmaking/queue/"+w.data.ticket).then(r=>r.json())).status,"cancelled");
}));
