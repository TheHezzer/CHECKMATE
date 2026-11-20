import test from "node:test";
import assert from "node:assert/strict";
import {createGameState,getGameState,applyGameMove,passGameTurn,proposeGameMove,castGameVote,castOpeningVote,sendTeamChat} from "./gameplay.js";

function startedMatch(f){
 const match={players:f.players,game:createGameState(f)};
 const now=Date.now();
 for(let slot=0;slot<5;slot++)castOpeningVote(match,"white-"+slot,"white-0",now);
 return match;
}
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
 assert.equal(game.activePlayerId,"");
 assert.ok(game.openingVote);
 assert.equal(game.board.filter(p=>p.team==="white").length,16);
 assert.equal(game.board.filter(p=>p.team==="black").length,16);
});
test("only the active player can move their own piece and white opens",()=>{
 const f=fixture();const match=startedMatch(f);
 const wrong=applyGameMove(match,"white-1",{fromFile:1,fromRow:6,toFile:1,toRow:5});
 assert.equal(wrong.status,403);
 const moved=applyGameMove(match,"white-0",{fromFile:0,fromRow:6,toFile:0,toRow:5});
 assert.equal(moved.status,200);
 assert.equal(match.game.activeTeam,"black");
 assert.notEqual(match.game.activePlayerId,"white-0");
});
test("server rejects illegal moves and pieces owned by another teammate",()=>{
 const f=fixture();const match=startedMatch(f);
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

test("team voting requires a proposal and a majority before applying the move",()=>{
 const f=fixture();f.mode="team_vote";const match={players:f.players,game:createGameState(f)};
 const starter=match.game.activePlayerId;
 const move={fromFile:0,fromRow:6,toFile:0,toRow:5};
 assert.equal(applyGameMove(match,starter,move).error,"VOTE_REQUIRED");
 const proposed=proposeGameMove(match,starter,move);
 match.game.pendingVote.discussionEndsAt=Date.now()-1;
 assert.equal(proposed.status,200);
 assert.equal(match.game.board.find(p=>p.ownerPlayerId===starter&&p.kind==="P").row,6);
 assert.equal(castGameVote(match,"black-0","approve").error,"VOTE_NOT_ALLOWED");
 assert.equal(castGameVote(match,"white-1","approve").status,200);
 assert.equal(castGameVote(match,"white-2","approve").status,200);
 assert.equal(castGameVote(match,"white-3","approve").status,200);
 assert.equal(castGameVote(match,starter,"approve").status,200);
 const accepted=castGameVote(match,"white-4","approve");
 assert.equal(accepted.status,200);
 assert.equal(accepted.vote.decision,"approve");
 assert.equal(match.game.board.find(p=>p.ownerPlayerId===starter&&p.kind==="P").row,5);
 assert.equal(match.game.activeTeam,"black");
 assert.equal(match.game.players.find(p=>p.playerId==="white-1").stats.correctVotes,1);
});
test("team vote rejects duplicates and a majority rejection passes the turn to the next teammate",()=>{
 const f=fixture();f.mode="team_vote";const match={players:f.players,game:createGameState(f)};
 const starter=match.game.activePlayerId;
 const move={fromFile:0,fromRow:6,toFile:0,toRow:5};
 proposeGameMove(match,starter,move);
 match.game.pendingVote.discussionEndsAt=Date.now()-1;
 assert.equal(castGameVote(match,"white-1","reject").status,200);
 assert.equal(castGameVote(match,"white-1","reject").error,"ALREADY_VOTED");
 castGameVote(match,"white-2","reject");
 castGameVote(match,"white-3","reject");
 castGameVote(match,starter,"reject");
 const rejected=castGameVote(match,"white-4","reject");
 assert.equal(rejected.status,200);
 assert.equal(rejected.vote.decision,"reject");
 assert.equal(match.game.board.find(p=>p.ownerPlayerId===starter&&p.kind==="P").row,6);
 assert.notEqual(match.game.activePlayerId,starter);
 assert.equal(match.game.players.find(p=>p.playerId==="white-1").stats.correctVotes,1);
});
test("team voting is unavailable in the standard classic mode",()=>{
 const f=fixture();f.mode="classic";const match={players:f.players,game:createGameState(f)};
 assert.equal(proposeGameMove(match,"white-0",{fromFile:0,fromRow:6,toFile:0,toRow:5}).error,"VOTING_MODE_REQUIRED");
});

test("vote timeout accepts the option with more votes even without all teammates voting",()=>{
 const f=fixture();f.mode="team_vote";const match={players:f.players,game:createGameState(f)};
 const starter=match.game.activePlayerId;
 const move={fromFile:0,fromRow:6,toFile:0,toRow:5};
 proposeGameMove(match,starter,move);
 match.game.pendingVote.discussionEndsAt=Date.now()-1;
 for(const id of ["white-1","white-2","white-3","white-7"])assert.equal(castGameVote(match,id,"approve").status,200);
 for(const id of ["white-4","white-5","white-6"])assert.equal(castGameVote(match,id,"reject").status,200);
 assert.ok(match.game.pendingVote);
 match.game.pendingVote.expiresAt=Date.now()-1;
 const state=getGameState(match,"white-1");
 assert.equal(match.game.pendingVote,null);
 assert.equal(match.game.board.find(p=>p.ownerPlayerId===starter&&p.kind==="P").row,5);
 assert.equal(match.game.activeTeam,"black");
 assert.equal(match.game.players.find(p=>p.playerId==="white-1").stats.correctVotes,1);
});
test("a tied vote at timeout rejects the proposal and passes the turn",()=>{
 const f=fixture();f.mode="team_vote";const match={players:f.players,game:createGameState(f)};
 const starter=match.game.activePlayerId;
 proposeGameMove(match,starter,{fromFile:0,fromRow:6,toFile:0,toRow:5});
 match.game.pendingVote.discussionEndsAt=Date.now()-1;
 for(const id of ["white-1","white-2","white-3"])castGameVote(match,id,"approve");
 for(const id of ["white-4","white-5","white-6"])castGameVote(match,id,"reject");
 match.game.pendingVote.expiresAt=Date.now()-1;
 getGameState(match,"white-1");
 assert.equal(match.game.pendingVote,null);
 assert.equal(match.game.board.find(p=>p.ownerPlayerId===starter&&p.kind==="P").row,6);
 assert.equal(match.game.activeTeam,"white");
 assert.notEqual(match.game.activePlayerId,starter);
});
test("discussion lasts five seconds and voting stays closed until it ends",()=>{
 const f=fixture();f.mode="team_vote";const match={players:f.players,game:createGameState(f)};
 proposeGameMove(match,"white-0",{fromFile:0,fromRow:6,toFile:0,toRow:5});
 const pending=match.game.pendingVote;
 assert.equal(pending.discussionEndsAt-pending.createdAt,5000);
 assert.equal(pending.expiresAt-pending.discussionEndsAt,15000);
 assert.equal(castGameVote(match,"white-1","approve").error,"DISCUSSION_IN_PROGRESS");
 pending.discussionEndsAt=Date.now()-1;
 assert.equal(castGameVote(match,"white-1","approve").status,200);
});
test("votes are closed after the 5-second discussion plus 15-second voting window and are resolved on state refresh",()=>{
 const f=fixture();f.mode="team_vote";const match={players:f.players,game:createGameState(f)};
 proposeGameMove(match,"white-0",{fromFile:0,fromRow:6,toFile:0,toRow:5});
 match.game.pendingVote.discussionEndsAt=Date.now()-1;
 match.game.pendingVote.expiresAt=Date.now()-1;
 const result=castGameVote(match,"white-1","approve");
 assert.equal(result.error,"VOTE_CLOSED");
 assert.equal(match.game.pendingVote,null);
});

test("white opening vote lasts 20 seconds and majority chooses the first player",()=>{
 const f=fixture(),match={players:f.players,game:createGameState(f)},now=Date.now();
 assert.equal(match.game.activePlayerId,"");
 assert.equal(match.game.openingVote.expiresAt-match.game.openingVote.createdAt,20000);
 for(let slot=0;slot<4;slot++)assert.equal(castOpeningVote(match,"white-"+slot,"white-3",now).status,200);
 assert.equal(match.game.openingVote!==null,true);
 const chosen=castOpeningVote(match,"white-4","white-3",now);
 assert.equal(chosen.status,200);
 assert.equal(match.game.activePlayerId,"white-3");
 assert.equal(match.game.openingVote,null);
 assert.equal(match.game.teamClocks.white,600000);
});
test("a player who misses 20 seconds is skipped to the next teammate",()=>{
 const f=fixture(),match=startedMatch(f),now=Date.now();
 match.game.playerTurnEndsAt=now-1;match.game.clockLastTickAt=now;
 const state=getGameState(match,"white-0");
 assert.equal(match.game.activePlayerId,"white-1");
 assert.equal(state.activeTurnRemainingMs,20000);
});
test("team loses when its shared ten-minute clock expires",()=>{
 const f=fixture(),match=startedMatch(f),now=Date.now();
 match.game.teamClocks.white=50;match.game.clockLastTickAt=now-100;
 const state=getGameState(match,"white-0");
 assert.equal(state.status,"finished");
 assert.equal(state.result,"timeout");
 assert.equal(state.winnerTeam,"black");
 assert.equal(state.teamClocks.white,0);
});
test("opening vote auto-selects the most voted player when 20 seconds expire",()=>{
 const f=fixture(),match={players:f.players,game:createGameState(f)},now=Date.now();
 castOpeningVote(match,"white-0","white-2",now);
 castOpeningVote(match,"white-1","white-2",now);
 match.game.openingVote.expiresAt=now-1;
 getGameState(match,"white-0");
 assert.equal(match.game.activePlayerId,"white-2");
 assert.equal(match.game.openingVote,null);
});
