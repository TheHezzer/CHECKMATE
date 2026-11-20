from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
main = root / "scripts" / "main.gd"
s = main.read_text(encoding="utf-8")

s = s.replace(
    'var match_piece_costs := {"Пешка": 0, "Конь": 180, "Слон": 220, "Ладья": 260, "Ферзь": 520, "Король": 0}',
    'var match_piece_costs := {"Пешка": 0, "Конь": 0, "Слон": 0, "Ладья": 0, "Ферзь": 0, "Король": 0}'
)
s = s.replace(
    'Открытие фигуры: XP списывается один раз.\\nПокупка перед матчем: злотые списываются за каждую партию.\\nВ Шахматном городе открытые фигуры не расходуются.',
    'Все фигуры доступны с начала игры.\\nВ обычном режиме выбирай любую дополнительную фигуру бесплатно.\\nЗдесь продаются только косметические скины без боевых бонусов.'
)

def replace_func(source, name, body):
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        raise SystemExit("Missing function " + name)
    end = source.find("\nfunc ", start + len(marker))
    if end < 0:
        end = len(source)
    return source[:start] + body.rstrip() + "\n" + source[end:]

s = replace_func(s, "_refresh_preparation_ui", '''func _refresh_preparation_ui() -> void:
    if preparation_panel == null:
        return
    for i in range(prep_piece_buttons.size()):
        var piece: String = ["Конь", "Слон", "Ладья", "Ферзь", "Король"][i]
        prep_piece_buttons[i].text = "✓  " + piece.to_upper()
    var piece_name: String = PIECES[selected_prep_piece]
    var info := preparation_panel.find_child("PrepSelectedLabel", true, false) as Label
    var action := preparation_panel.find_child("PrepActionButton", true, false) as Button
    if info:
        info.text = "ВЫБРАНА: " + piece_name.to_upper()
    if action:
        action.text = "ВЫБРАТЬ И НАЧАТЬ"
    if prep_status:
        prep_status.text = "Фигура доступна бесплатно. Все боевые фигуры открыты с начала игры."
    _save_economy()''')

s = replace_func(s, "_purchase_or_unlock_selected", '''func _purchase_or_unlock_selected() -> void:
    var piece_name: String = PIECES[selected_prep_piece]
    if piece_name == "Пешка":
        prep_status.text = "Пешка обязательна и уже входит в комплект. Выбери дополнительную фигуру."
        return
    selected_match_piece = piece_name
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _confirm_preparation()''')

s = replace_func(s, "_refund_pending_match_purchase", '''func _refund_pending_match_purchase() -> void:
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""''')

# Update the tutorial's explanation to match the free Classic roster.
s = s.replace(
    'Фигуры открываются за XP. Дополнительная боевая фигура покупается за злотые перед классической партией. Скины после покупки остаются навсегда. Закрытые фигуры отмечены замком.',
    'В обычной партии все боевые фигуры доступны сразу и выбираются бесплатно. За злотые можно покупать косметические скины, которые не усиливают фигуры. Прокачка характеристик будет отдельной системой Шахматного города.'
)
main.write_text(s, encoding="utf-8")

# Classic entry is free for every piece; retain the account API for compatibility.
accounts = root / "server" / "accounts.js"
a = accounts.read_text(encoding="utf-8")
a = a.replace(
    'const costs = { "Пешка": 0, "Конь": 180, "Слон": 220, "Ладья": 260, "Ферзь": 520, "Король": 0 };',
    'const costs = { "Пешка": 0, "Конь": 0, "Слон": 0, "Ладья": 0, "Ферзь": 0, "Король": 0 };'
)
if a == accounts.read_text(encoding="utf-8"):
    raise SystemExit("Classic piece prices anchor missing")
accounts.write_text(a, encoding="utf-8")

# Track individual match contribution on the authoritative server.
gameplay = root / "server" / "gameplay.js"
g = gameplay.read_text(encoding="utf-8")
g = g.replace(
    'const players=match.players.map(p=>({playerId:p.playerId,name:p.name,team:p.team,slot:p.slot,secondPiece:p.secondPiece||p.piece,eliminated:false,remainingPieces:2}));',
    'const players=match.players.map(p=>({playerId:p.playerId,name:p.name,team:p.team,slot:p.slot,secondPiece:p.secondPiece||p.piece,eliminated:false,remainingPieces:2,stats:{moves:0,captures:0,checks:0,checkmates:0,promotions:0,castlings:0,passes:0,qualityTotal:0,votes:0,correctVotes:0}}));'
)
g = g.replace(
    'players:state.players.map(p=>({...p})),viewer:',
    'players:state.players.map(p=>({...p,stats:{...(p.stats||{})}})),viewer:'
)
old = '''  const movingTeam=piece.team,from={file:fromFile,row:fromRow},target=at(state.board,toFile,toRow);
  if(target)state.board.splice(state.board.indexOf(target),1);
  const oldFile=piece.file;piece.file=toFile;piece.row=toRow;piece.hasMoved=true;'''
new = '''  const movingTeam=piece.team,from={file:fromFile,row:fromRow},target=at(state.board,toFile,toRow);
  const movingKind=piece.kind;
  const wasPromotion=movingKind==="P"&&(toRow===0||toRow===7);
  const wasCastling=movingKind==="K"&&Math.abs(toFile-fromFile)===2;
  if(target)state.board.splice(state.board.indexOf(target),1);
  const oldFile=piece.file;piece.file=toFile;piece.row=toRow;piece.hasMoved=true;'''
if old not in g: raise SystemExit("Move stats prelude anchor missing")
g = g.replace(old,new,1)
old = '''  if(piece.kind==="P"&&(toRow===0||toRow===7))piece.kind="Q";
  state.history.push({playerId,team:movingTeam,from,to:{file:toFile,row:toRow},piece:LETTERS[piece.kind],captured:target?LETTERS[target.kind]:null,at:Date.now()});'''
new = '''  if(wasPromotion)piece.kind="Q";
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
  state.history.push({playerId,team:movingTeam,from,to:{file:toFile,row:toRow},piece:LETTERS[piece.kind],captured:target?LETTERS[target.kind]:null,check:givesCheck,at:Date.now()});'''
if old not in g: raise SystemExit("Move stats update anchor missing")
g = g.replace(old,new,1)
# Remove the duplicate opponent declaration from the original move completion block.
g = g.replace('  const opponent=movingTeam==="white"?"black":"white";\n  if(!hasLegalMove(state.board,opponent)){',
              '  if(!hasLegalMove(state.board,opponent)){',1)
g = g.replace(
    '  state.passedThisTurn.push(playerId);',
    '  state.passedThisTurn.push(playerId);\n  const passingPlayer=state.players.find(p=>p.playerId===playerId);\n  if(passingPlayer){passingPlayer.stats=passingPlayer.stats||{};passingPlayer.stats.passes=(passingPlayer.stats.passes||0)+1;}'
)
# Mark checkmate in the individual contribution record.
g = g.replace(
    'state.winnerTeam=state.result==="checkmate"?movingTeam:"draw";\n    state.activePlayerId="";',
    'state.winnerTeam=state.result==="checkmate"?movingTeam:"draw";\n    if(state.result==="checkmate"&&ownPlayer)ownPlayer.stats.checkmates=(ownPlayer.stats.checkmates||0)+1;\n    state.activePlayerId="";'
)
gameplay.write_text(g, encoding="utf-8")

print("CHECKMATE v38: free Classic figures and server-side individual match statistics applied.")
