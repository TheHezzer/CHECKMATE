import test from "node:test";
import assert from "node:assert/strict";
import { createMatchmakingServer } from "./server.js";
async function withServer(fn){const s=createMatchmakingServer();await new Promise(r=>s.listen(0,"127.0.0.1",r));const a=s.address();try{await fn("http://127.0.0.1:"+a.port)}finally{s.closeAllConnections();await new Promise(r=>s.close(r))}}
async function queue(base,id,rating,mode="classic"){const r=await fetch(base+"/matchmaking/queue",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({playerId:id,playerName:"Player_"+id,mode,rating})});return{status:r.status,data:await r.json()}}
test("health endpoint reports service",async()=>withServer(async base=>{const r=await fetch(base+"/health");assert.equal(r.status,200);assert.equal((await r.json()).ok,true)}));
test("manual room creation is disabled",async()=>withServer(async base=>{const r=await fetch(base+"/rooms",{method:"POST",headers:{"content-type":"application/json"},body:"{}"});assert.equal(r.status,404)}));
test("classic matchmaking waits for 32 and creates balanced 16v16 teams",async()=>withServer(async base=>{
 let first;for(let i=0;i<32;i++){const r=await queue(base,"p"+i,1000+i*2);if(i===0)first=r;if(i<31)assert.equal(r.data.status,"waiting");else assert.equal(r.data.status,"matched")}
 const s=await fetch(base+"/matchmaking/queue/"+first.data.ticket).then(r=>r.json());assert.equal(s.status,"matched");assert.equal(s.players.length,32);
 const w=s.players.filter(p=>p.team==="white"),b=s.players.filter(p=>p.team==="black");assert.equal(w.length,16);assert.equal(b.length,16);assert.equal(new Set(s.players.map(p=>p.playerId)).size,32);
 assert.ok(Math.abs(w.reduce((a,p)=>a+p.rating,0)-b.reduce((a,p)=>a+p.rating,0))<=32);
}));
test("matchmaking never mixes game modes",async()=>withServer(async base=>{
 let cityFirst;for(let i=0;i<31;i++){const c=await queue(base,"c"+i,1000+i,"classic");const s=await queue(base,"s"+i,1000+i,"chess_city");if(i===0)cityFirst=s;assert.equal(c.data.status,"waiting");assert.equal(s.data.status,"waiting")}
 assert.equal((await queue(base,"c-last",1000,"classic")).data.status,"matched");
 assert.equal((await fetch(base+"/matchmaking/queue/"+cityFirst.data.ticket).then(r=>r.json())).status,"waiting");
 assert.equal((await queue(base,"s-last",1000,"chess_city")).data.status,"matched");
}));
test("waiting roster returns player nicknames and ratings",async()=>withServer(async base=>{
 const a=await queue(base,"alpha",1000),b=await queue(base,"bravo",1070);const s=await fetch(base+"/matchmaking/queue/"+a.data.ticket).then(r=>r.json());assert.equal(s.players.length,2);assert.ok(s.players.some(p=>p.name==="Player_alpha"));assert.ok(s.players.some(p=>p.rating===1070));assert.equal(s.requiredPlayers,32);
}));
test("a player can cancel a waiting ticket",async()=>withServer(async base=>{
 const w=await queue(base,"cancel-me",1000,"cancel_test");const c=await fetch(base+"/matchmaking/queue/"+w.data.ticket+"/cancel",{method:"POST"});assert.equal(c.status,200);assert.equal((await c.json()).status,"cancelled");assert.equal((await fetch(base+"/matchmaking/queue/"+w.data.ticket).then(r=>r.json())).status,"cancelled");
}));
