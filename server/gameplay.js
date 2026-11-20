import crypto from "node:crypto";

const FILES = [0,1,2,3,4,5,6,7];
const BACK_RANK = ["R","N","B","Q","K","B","N","R"];
const ROLE_FILES = { "Ладья":[0,7], "Конь":[1,6], "Слон":[2,5], "Ферзь":[3], "Король":[4] };
const LETTERS = { P:"Пешка", R:"Ладья", N:"Конь", B:"Слон", Q:"Ферзь", K:"Король" };
export const VOTE_DISCUSSION_MS = 5_000;
export const VOTE_DURATION_MS = 15_000;

function clone(value) { return JSON.parse(JSON.stringify(value)); }
function inside(file,row) { return file>=0 && file<8 && row>=0 && row<8; }
function at(board,file,row) { return board.find(p=>p.file===file&&p.row===row) || null; }
function clearPath(board,from,to) {
  const df=Math.sign(to.file-from.file), dr=Math.sign(to.row-from.row);
  let f=from.file+df, r=from.row+dr;
  while(f!==to.file||r!==to.row){if(at(board,f,r))return false;f+=df;r+=dr;}
  return true;
}
function attacksSquare(board,piece,file,row) {
  const df=file-piece.file, dr=row-piece.row;
  switch(piece.kind){
    case "P": return Math.abs(df)===1 && dr===(piece.team==="white"?-1:1);
    case "N": return (Math.abs(df)===1&&Math.abs(dr)===2)||(Math.abs(df)===2&&Math.abs(dr)===1);
    case "K": return Math.max(Math.abs(df),Math.abs(dr))===1;
    case "R": return (df===0||dr===0)&&(df!==0||dr!==0)&&clearPath(board,piece,{file,row});
    case "B": return Math.abs(df)===Math.abs(dr)&&df!==0&&clearPath(board,piece,{file,row});
    case "Q": return (df===0||dr===0||Math.abs(df)===Math.abs(dr))&&(df!==0||dr!==0)&&clearPath(board,piece,{file,row});
    default:return false;
  }
}
function kingOf(board,team){return board.find(p=>p.team===team&&p.kind==="K")||null;}
function inCheck(board,team){
  const king=kingOf(board,team); if(!king)return true;
  return board.some(p=>p.team!==team && attacksSquare(board,p,king.file,king.row));
}
function pseudoLegal(board,piece,toFile,toRow){
  if(!inside(toFile,toRow)||piece.file===toFile&&piece.row===toRow)return false;
  const target=at(board,toFile,toRow);
  if(target?.team===piece.team||target?.kind==="K")return false;
  const df=toFile-piece.file, dr=toRow-piece.row;
  switch(piece.kind){
    case "P":{
      const step=piece.team==="white"?-1:1, start=piece.team==="white"?6:1;
      if(df===0&&dr===step&&!target)return true;
      if(df===0&&dr===2*step&&piece.row===start&&!piece.hasMoved&&!target&&!at(board,piece.file,piece.row+step))return true;
      return Math.abs(df)===1&&dr===step&&!!target;
    }
    case "N":return (Math.abs(df)===1&&Math.abs(dr)===2)||(Math.abs(df)===2&&Math.abs(dr)===1);
    case "R":return (df===0||dr===0)&&clearPath(board,piece,{file:toFile,row:toRow});
    case "B":return Math.abs(df)===Math.abs(dr)&&clearPath(board,piece,{file:toFile,row:toRow});
    case "Q":return (df===0||dr===0||Math.abs(df)===Math.abs(dr))&&clearPath(board,piece,{file:toFile,row:toRow});
    case "K":{
      if(Math.max(Math.abs(df),Math.abs(dr))===1)return true;
      if(dr!==0||Math.abs(df)!==2||piece.hasMoved||inCheck(board,piece.team))return false;
      const rookFile=df>0?7:0, rook=at(board,rookFile,piece.row);
      if(!rook||rook.kind!=="R"||rook.team!==piece.team||rook.hasMoved)return false;
      const step=df>0?1:-1;
      for(let f=piece.file+step;f!==rookFile;f+=step)if(at(board,f,piece.row))return false;
      const enemy=piece.team==="white"?"black":"white";
      return !attackedBy(board,piece.file+step,piece.row,enemy)&&!attackedBy(board,piece.file+2*step,piece.row,enemy);
    }
    default:return false;
  }
}
function attackedBy(board,file,row,team){return board.some(p=>p.team===team&&attacksSquare(board,p,file,row));}
function legalMove(board,piece,toFile,toRow){
  if(!pseudoLegal(board,piece,toFile,toRow))return false;
  const copy=clone(board), moving=copy.find(p=>p.id===piece.id);
  const target=at(copy,toFile,toRow);
  if(target)copy.splice(copy.indexOf(target),1);
  const oldFile=moving.file;
  moving.file=toFile;moving.row=toRow;moving.hasMoved=true;
  if(moving.kind==="K"&&Math.abs(toFile-oldFile)===2){
    const rookFrom=toFile>oldFile?7:0, rookTo=toFile>oldFile?toFile-1:toFile+1;
    const rook=at(copy,rookFrom,moving.row); if(rook){rook.file=rookTo;rook.hasMoved=true;}
  }
  return !inCheck(copy,piece.team);
}
function hasLegalMove(board,team){
  for(const p of board.filter(x=>x.team===team))
    for(const f of FILES)for(const r of FILES)if(legalMove(board,p,f,r))return true;
  return false;
}
function activePlayerFor(state,team,startAfter=-1){
  const teamPlayers=state.players.filter(p=>p.team===team).sort((a,b)=>a.slot-b.slot);
  if(!teamPlayers.length)return null;
  for(let step=1;step<=8;step++){
    const slot=(startAfter+step+8)%8;
    const player=teamPlayers.find(p=>p.slot===slot&&!p.eliminated);
    if(player)return player;
  }
  return null;
}
function finishTurn(state,team,afterSlot){
  state.nextSlot[team]=(afterSlot+1)%8;
  const other=team==="white"?"black":"white";
  const next=activePlayerFor(state,other,state.nextSlot[other]-1);
  if(!next){state.status="finished";state.result=team;state.winnerTeam=team;return;}
  state.activeTeam=other;state.activePlayerId=next.playerId;state.passedThisTurn=[];
  state.turn+=1;
}
function updateEliminations(state){
  for(const player of state.players){
    const count=state.board.filter(p=>p.ownerPlayerId===player.playerId).length;
    player.remainingPieces=count;
    player.eliminated=count===0;
  }
}
function makeInitialBoard(players){
  const board=[];
  for(const team of ["white","black"]){
    const backRow=team==="white"?7:0, pawnRow=team==="white"?6:1;
    const teamPlayers=players.filter(p=>p.team===team).sort((a,b)=>a.slot-b.slot);
    for(const player of teamPlayers){
      const pawnId=crypto.randomUUID();
      board.push({id:pawnId,kind:"P",team,file:player.slot,row:pawnRow,ownerPlayerId:player.playerId,hasMoved:false});
    }
    const used=new Map(Object.keys(ROLE_FILES).map(role=>[role,0]));
    for(const player of teamPlayers){
      const role=player.secondPiece;
      const positions=ROLE_FILES[role];
      const occurrence=used.get(role)||0;
      const file=positions?.[occurrence];
      if(file===undefined)continue;
      used.set(role,occurrence+1);
      board.push({id:crypto.randomUUID(),kind:Object.keys(LETTERS).find(k=>LETTERS[k]===role),team,file,row:backRow,ownerPlayerId:player.playerId,hasMoved:false});
    }
  }
  return board;
}
function isVoteMode(state){return /голос|vote/i.test(String(state?.mode||""));}
export function createGameState(match){
  const players=match.players.map(p=>({playerId:p.playerId,name:p.name,team:p.team,slot:p.slot,secondPiece:p.secondPiece||p.piece,eliminated:false,remainingPieces:2,stats:{moves:0,captures:0,checks:0,checkmates:0,promotions:0,castlings:0,passes:0,qualityTotal:0,votes:0,correctVotes:0}}));
  const whiteStart=players.find(p=>p.playerId===match.startingPlayerId&&p.team==="white")||players.find(p=>p.team==="white");
  const blackPlayers=players.filter(p=>p.team==="black");
  const blackStart=blackPlayers.length?blackPlayers[crypto.randomInt(0,blackPlayers.length)]:null;
  return {
    matchId:match.id,mode:match.mode,createdAt:Date.now(),status:"active",result:null,winnerTeam:null,
    players,board:makeInitialBoard(players),activeTeam:"white",activePlayerId:whiteStart?.playerId||"",
    startingPlayerId:whiteStart?.playerId||"",nextSlot:{white:whiteStart?(whiteStart.slot+1)%8:0,black:blackStart?blackStart.slot:0},
    turn:1,moveNumber:1,halfmoveClock:0,history:[],chat:[],passedThisTurn:[],pendingVote:null,updatedAt:Date.now()
  };
}
function sanitizeState(state,viewerId){
  const viewer=state.players.find(p=>p.playerId===viewerId);
  return {
    matchId:state.matchId,status:state.status,result:state.result,winnerTeam:state.winnerTeam,
    activeTeam:state.activeTeam,activePlayerId:state.activePlayerId,startingPlayerId:state.startingPlayerId,
    turn:state.turn,moveNumber:state.moveNumber,board:clone(state.board),
    players:state.players.map(p=>({...p,stats:{...(p.stats||{})}})),viewer:{playerId:viewerId,team:viewer?.team||null,eliminated:viewer?.eliminated??true},
    chat:state.chat.filter(m=>m.team===viewer?.team).slice(-50),pendingVote:state.pendingVote&&state.pendingVote.team===viewer?.team?{proposerId:state.pendingVote.proposerId,team:state.pendingVote.team,move:clone(state.pendingVote.move),votes:Object.values(state.pendingVote.votes),approveCount:voteCounts(state.pendingVote).approveCount,rejectCount:voteCounts(state.pendingVote).rejectCount,requiredVotes:state.pendingVote.requiredVotes,createdAt:state.pendingVote.createdAt,discussionEndsAt:state.pendingVote.discussionEndsAt,expiresAt:state.pendingVote.expiresAt,remainingMs:Math.max(0,state.pendingVote.expiresAt-Date.now()),viewerVote:state.pendingVote.votes[viewerId]||null}:null,lastMove:state.history.at(-1)||null,updatedAt:state.updatedAt
  };
}
function voteCounts(pending){
  const choices=Object.values(pending.votes||{});
  return {approveCount:choices.filter(v=>v==="approve").length,rejectCount:choices.filter(v=>v==="reject").length};
}
function finalizeVote(match,decision){
  const state=match.game,pending=state.pendingVote;
  if(!pending)return null;
  const {approveCount,rejectCount}=voteCounts(pending);
  for(const [voterId,choice] of Object.entries(pending.votes)){
    const voter=state.players.find(p=>p.playerId===voterId);
    if(voter){voter.stats=voter.stats||{};voter.stats.votes=(voter.stats.votes||0)+1;if(choice===decision)voter.stats.correctVotes=(voter.stats.correctVotes||0)+1;}
  }
  const move=clone(pending.move),proposerId=pending.proposerId,requiredVotes=pending.requiredVotes;
  state.pendingVote=null;
  const result=decision==="approve"?applyGameMove(match,proposerId,move,true):passGameTurn(match,proposerId);
  if(result.state)result.vote={decision,approveCount,rejectCount,requiredVotes,timedOut:Date.now()>=pending.expiresAt};
  return result;
}
function expirePendingVote(match,now=Date.now()){
  const pending=match?.game?.pendingVote;
  if(!pending||now<pending.expiresAt)return null;
  const {approveCount,rejectCount}=voteCounts(pending);
  // A tie is not approval: the proposed move is rejected and the turn is passed.
  return finalizeVote(match,approveCount>rejectCount?"approve":"reject");
}
export function getGameState(match,viewerId){
  if(!match?.game)return null;
  expirePendingVote(match);
  return sanitizeState(match.game,viewerId);
}
export function applyGameMove(match,playerId,move,approvedByVote=false){
  const state=match?.game;if(!state||state.status!=="active")return{status:409,error:"MATCH_NOT_ACTIVE"};
  if(isVoteMode(state)&&!approvedByVote)return{status:403,error:"VOTE_REQUIRED"};
  if(state.pendingVote&&!approvedByVote)return{status:409,error:"VOTE_IN_PROGRESS"};
  if(approvedByVote)state.pendingVote=null;
  if(state.activePlayerId!==playerId)return{status:403,error:"NOT_YOUR_TURN"};
  const fromFile=Number(move.fromFile),fromRow=Number(move.fromRow),toFile=Number(move.toFile),toRow=Number(move.toRow);
  if(![fromFile,fromRow,toFile,toRow].every(Number.isInteger)||![fromFile,fromRow,toFile,toRow].every(n=>n>=0&&n<8))return{status:400,error:"INVALID_COORDINATES"};
  const piece=at(state.board,fromFile,fromRow);
  if(!piece||piece.ownerPlayerId!==playerId||piece.team!==state.activeTeam)return{status:403,error:"PIECE_NOT_OWNED"};
  if(!legalMove(state.board,piece,toFile,toRow))return{status:400,error:"ILLEGAL_MOVE"};
  const movingTeam=piece.team,from={file:fromFile,row:fromRow},target=at(state.board,toFile,toRow);
  const movingKind=piece.kind;
  const wasPromotion=movingKind==="P"&&(toRow===0||toRow===7);
  const wasCastling=movingKind==="K"&&Math.abs(toFile-fromFile)===2;
  if(target)state.board.splice(state.board.indexOf(target),1);
  const oldFile=piece.file;piece.file=toFile;piece.row=toRow;piece.hasMoved=true;
  if(piece.kind==="K"&&Math.abs(toFile-oldFile)===2){
    const rookFrom=toFile>oldFile?7:0,rookTo=toFile>oldFile?toFile-1:toFile+1,rook=at(state.board,rookFrom,toRow);
    if(rook){rook.file=rookTo;rook.hasMoved=true;}
  }
  if(wasPromotion)piece.kind="Q";
  const opponent=movingTeam==="white"?"black":"white";
  const givesCheck=inCheck(state.board,opponent);
  const ownPlayer=state.players.find(p=>p.playerId===playerId);
  if(ownPlayer){
    const stats=ownPlayer.stats||(ownPlayer.stats={moves:0,captures:0,checks:0,checkmates:0,promotions:0,castlings:0,passes:0,qualityTotal:0,votes:0,correctVotes:0});
    let quality=65;
    if(target){stats.captures+=1;quality+=12;}
    if(givesCheck){stats.checks+=1;quality+=10;}
    if(wasPromotion){stats.promotions+=1;quality+=8;}
    if(wasCastling){stats.castlings+=1;quality+=7;}
    if((movingKind==="N"||movingKind==="B")&&from.row===(movingTeam==="white"?7:0)&&Math.abs(toFile-3.5)<=2)quality+=5;
    if(attackedBy(state.board,toFile,toRow,opponent)&&!attackedBy(state.board,toFile,toRow,movingTeam))quality-=20;
    stats.moves+=1;
    stats.qualityTotal+=Math.max(0,Math.min(100,quality));
  }
  state.history.push({playerId,team:movingTeam,from,to:{file:toFile,row:toRow},piece:LETTERS[piece.kind],captured:target?LETTERS[target.kind]:null,check:givesCheck,at:Date.now()});
  state.moveNumber+=movingTeam==="black"?1:0;
  state.halfmoveClock=(piece.kind==="P"||target)?0:state.halfmoveClock+1;
  updateEliminations(state);state.updatedAt=Date.now();
  if(!hasLegalMove(state.board,opponent)){
    state.status="finished";state.result=inCheck(state.board,opponent)?"checkmate":"stalemate";
    state.winnerTeam=state.result==="checkmate"?movingTeam:"draw";
    if(state.result==="checkmate"&&ownPlayer)ownPlayer.stats.checkmates=(ownPlayer.stats.checkmates||0)+1;
    state.activePlayerId="";
  }else{
    const current=state.players.find(p=>p.playerId===playerId);
    finishTurn(state,movingTeam,current?.slot??-1);
  }
  return{status:200,state:sanitizeState(state,playerId)};
}
export function passGameTurn(match,playerId){
  const state=match?.game;if(!state||state.status!=="active")return{status:409,error:"MATCH_NOT_ACTIVE"};
  if(state.pendingVote)return{status:409,error:"VOTE_IN_PROGRESS"};
  if(state.activePlayerId!==playerId)return{status:403,error:"NOT_YOUR_TURN"};
  const player=state.players.find(p=>p.playerId===playerId);
  if(!player)return{status:404,error:"PLAYER_NOT_IN_MATCH"};
  state.passedThisTurn.push(playerId);
  const passingPlayer=state.players.find(p=>p.playerId===playerId);
  if(passingPlayer){passingPlayer.stats=passingPlayer.stats||{};passingPlayer.stats.passes=(passingPlayer.stats.passes||0)+1;}
  const eligible=state.players.filter(p=>p.team===state.activeTeam&&!p.eliminated&&!state.passedThisTurn.includes(p.playerId)).sort((a,b)=>a.slot-b.slot);
  if(eligible.length){
    const next=eligible.find(p=>p.slot>player.slot)||eligible[0];
    state.activePlayerId=next.playerId;
  }else{
    finishTurn(state,state.activeTeam,player.slot);
  }
  if (state.status === "active") state.updatedAt=Date.now();
  return{status:200,state:sanitizeState(state,playerId)};
}

export function proposeGameMove(match,playerId,move){
  const state=match?.game;
  if(!state||state.status!=="active")return{status:409,error:"MATCH_NOT_ACTIVE"};
  if(!isVoteMode(state))return{status:409,error:"VOTING_MODE_REQUIRED"};
  if(state.pendingVote)return{status:409,error:"VOTE_IN_PROGRESS"};
  if(state.activePlayerId!==playerId)return{status:403,error:"NOT_YOUR_TURN"};
  const fromFile=Number(move.fromFile),fromRow=Number(move.fromRow),toFile=Number(move.toFile),toRow=Number(move.toRow);
  if(![fromFile,fromRow,toFile,toRow].every(Number.isInteger)||![fromFile,fromRow,toFile,toRow].every(n=>n>=0&&n<8))return{status:400,error:"INVALID_COORDINATES"};
  const piece=at(state.board,fromFile,fromRow);
  if(!piece||piece.ownerPlayerId!==playerId||piece.team!==state.activeTeam)return{status:403,error:"PIECE_NOT_OWNED"};
  if(!legalMove(state.board,piece,toFile,toRow))return{status:400,error:"ILLEGAL_MOVE"};
  const voters=state.players.filter(p=>p.team===state.activeTeam&&!p.eliminated);
  const createdAt=Date.now();
  state.pendingVote={proposerId:playerId,team:state.activeTeam,move:{fromFile,fromRow,toFile,toRow},votes:{},requiredVotes:Math.floor(voters.length/2)+1,createdAt,discussionEndsAt:createdAt+VOTE_DISCUSSION_MS,expiresAt:createdAt+VOTE_DISCUSSION_MS+VOTE_DURATION_MS};
  state.updatedAt=Date.now();
  return{status:200,state:sanitizeState(state,playerId)};
}
export function castGameVote(match,playerId,vote){
  const state=match?.game;
  if(!state||state.status!=="active")return{status:409,error:"MATCH_NOT_ACTIVE"};
  if(!isVoteMode(state))return{status:409,error:"VOTING_MODE_REQUIRED"};
  const pending=state.pendingVote;
  if(!pending)return{status:409,error:"NO_PENDING_VOTE"};
  if(Date.now()<pending.discussionEndsAt){
    return{status:409,error:"DISCUSSION_IN_PROGRESS",state:sanitizeState(state,playerId),discussionEndsAt:pending.discussionEndsAt};
  }
  if(Date.now()>=pending.expiresAt){
    const expired=expirePendingVote(match);
    return{status:409,error:"VOTE_CLOSED",state:expired?.state||sanitizeState(state,playerId),vote:expired?.vote||null};
  }
  const player=state.players.find(p=>p.playerId===playerId);
  if(!player)return{status:403,error:"PLAYER_NOT_IN_MATCH"};
  if(player.team!==pending.team||player.eliminated)return{status:403,error:"VOTE_NOT_ALLOWED"};
  if(!["approve","reject"].includes(vote))return{status:400,error:"INVALID_VOTE"};
  if(Object.prototype.hasOwnProperty.call(pending.votes,playerId))return{status:409,error:"ALREADY_VOTED"};
  pending.votes[playerId]=vote;
  const {approveCount,rejectCount}=voteCounts(pending);
  const voters=state.players.filter(p=>p.team===pending.team&&!p.eliminated);
  const allVoted=Object.keys(pending.votes).length>=voters.length;
  let decision=null;
  if(approveCount>=pending.requiredVotes)decision="approve";
  else if(rejectCount>=pending.requiredVotes)decision="reject";
  else if(allVoted)decision=approveCount>rejectCount?"approve":"reject";
  if(!decision){
    state.updatedAt=Date.now();
    return{status:200,state:sanitizeState(state,playerId),vote:{decision:null,approveCount,rejectCount,requiredVotes:pending.requiredVotes,expiresAt:pending.expiresAt}};
  }
  return finalizeVote(match,decision);
}

export function sendTeamChat(match,playerId,message){
  const state=match?.game;if(!state)return{status:404,error:"MATCH_NOT_FOUND"};
  const player=state.players.find(p=>p.playerId===playerId);if(!player)return{status:403,error:"PLAYER_NOT_IN_MATCH"};
  const text=String(message||"").trim().slice(0,300);if(!text)return{status:400,error:"EMPTY_MESSAGE"};
  const item={id:crypto.randomUUID(),playerId,playerName:player.name,team:player.team,text,at:Date.now(),spectator:player.eliminated};
  state.chat.push(item);if(state.chat.length>200)state.chat.splice(0,state.chat.length-200);
  state.updatedAt=Date.now();return{status:201,message:item};
}
