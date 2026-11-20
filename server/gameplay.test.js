import test from "node:test";
import assert from "node:assert/strict";
import {createGameState,getGameState,applyGameMove,passGameTurn,sendTeamChat} from "./gameplay.js";

function fixture(){
 const roles=["Ладья","Ладья","Конь","Конь","Слон","Слон","Ферзь","Король"];
 const players=[];
 for(const team of ["white","black"])for(let slot=0;slot<8;slot++)players.push({playerId:team+"-"+slot,name:team+"_"+slot,team,slot,secondPiece:roles[slot],piece:roles[slot]});
 return{id:"match-test",mode:"classic",players,startingPlayerId:"white-0"};
}
test("creates one pawn and one assigned extra figure per each of 16 players",()=>{
 const game=createGameState(fixture());
 assert.equal(game.board.length,32);
 for(const p of game.players)assert.equal(game.board.filter(x=>x.ownerPlayerId===p.playerId).length,2);
 assert.equal(game.activeTeam,"white");
 assert.equal(game.activePlayerId,"white-0");
 assert.equal(game.board.filter(p=>p.team==="white").length,16);
 assert.equal(game.board.filter(p=>p.team==="black").length,16);
});
test("only the active player can move their own piece and white opens",()=>{
 const match={players:fixture().players,game:createGameState(fixture())};
 const wrong=applyGameMove(match,"white-1",{fromFile:1,fromRow:6,toFile:1,toRow:5});
 assert.equal(wrong.status,403);
 const moved=applyGameMove(match,"white-0",{fromFile:0,fromRow:6,toFile:0,toRow:5});
 assert.equal(moved.status,200);
 assert.equal(match.game.activeTeam,"black");
 assert.notEqual(match.game.activePlayerId,"white-0");
});
test("server rejects illegal moves and pieces owned by another teammate",()=>{
 const match={players:fixture().players,game:createGameState(fixture())};
 assert.equal(applyGameMove(match,"white-0",{fromFile:0,fromRow:6,toFile:0,toRow:3}).error,"ILLEGAL_MOVE");
 assert.equal(applyGameMove(match,"white-0",{fromFile:1,fromRow:6,toFile:1,toRow:5}).error,"PIECE_NOT_OWNED");
});
test("passing gives the same team turn to the next living teammate",()=>{
 const match={players:fixture().players,game:createGameState(fixture())};
 const result=passGameTurn(match,"white-0");
 assert.equal(result.status,200);
 assert.equal(match.game.activeTeam,"white");
 assert.equal(match.game.activePlayerId,"white-1");
});
test("team chat is private to the player's team and eliminated players may chat",()=>{
 const match={players:fixture().players,game:createGameState(fixture())};
 const msg=sendTeamChat(match,"white-0","Вперёд!");
 assert.equal(msg.status,201);
 const white=getGameState(match,"white-1"),black=getGameState(match,"black-0");
 assert.equal(white.chat.length,1);
 assert.equal(black.chat.length,0);
 match.game.players.find(p=>p.playerId==="white-0").eliminated=true;
 assert.equal(sendTeamChat(match,"white-0","Я наблюдаю").status,201);
});
