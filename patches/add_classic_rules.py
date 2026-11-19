from pathlib import Path

root = Path(__file__).resolve().parent.parent
main_path = root / "scripts" / "main.gd"
source = main_path.read_text(encoding="utf-8").replace("\\t", "    ")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if old not in source:
        raise SystemExit("Patch anchor not found: " + label)
    source = source.replace(old, new, 1)

# Friendly pieces remain selectable; enemy pieces are captured by a legal move.
replace_once(
'''    if target_piece != null:
        if str(target_piece.get_meta("team")) == current_team:
            selected_game_piece = target_piece
            status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        else:
            status_label.text = "На этой клетке противник. Боевой вызов добавим следующим этапом."
        return
    var from_col: int = int(selected_game_piece.get_meta("col"))''',
'''    if target_piece != null and str(target_piece.get_meta("team")) == current_team:
        selected_game_piece = target_piece
        status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        return
    var from_col: int = int(selected_game_piece.get_meta("col"))''',
"enemy capture selection")

replace_once(
'''    if not _is_valid_classic_move(kind, current_team, from_col, from_row, col, row):
        status_label.text = "Недопустимый ход для этой фигуры."
        return
    selected_game_piece.position = Vector3((col - 3.5) * 1.05, 0.64, (row - 3.5) * 0.88 - 0.4)
    selected_game_piece.set_meta("col", col)
    selected_game_piece.set_meta("row", row)
    selected_game_piece = null
    status_label.text = "Ход выполнен. Очередь перешла другой команде."
    _advance_team_turn()''',
'''    if not _is_valid_classic_move(kind, current_team, from_col, from_row, col, row, target_piece):
        status_label.text = "Недопустимый ход для этой фигуры."
        return
    if target_piece != null:
        game_piece_nodes.erase(target_piece)
        target_piece.queue_free()
    selected_game_piece.position = Vector3((col - 3.5) * 1.05, 0.64, (row - 3.5) * 0.88 - 0.4)
    selected_game_piece.set_meta("col", col)
    selected_game_piece.set_meta("row", row)
    selected_game_piece.set_meta("has_moved", true)
    var promoted := false
    if kind == "P" and ((current_team == "white" and row == 0) or (current_team == "black" and row == 7)):
        selected_game_piece.set_meta("kind", "Q")
        promoted = true
    selected_game_piece = null
    status_label.text = "Пешка превращена в ферзя." if promoted else "Ход выполнен. Очередь перешла другой команде."
    _advance_team_turn()''',
"capture and promotion")

replace_once(
'''func _is_valid_classic_move(kind: String, team: String, from_col: int, from_row: int, to_col: int, to_row: int) -> bool:
    var dc: int = to_col - from_col
    var dr: int = to_row - from_row
    if dc == 0 and dr == 0:
        return false
    var valid_shape := false
    match kind:
        "P":
            var forward: int = -1 if team == "white" else 1
            var start_row: int = 6 if team == "white" else 1
            valid_shape = (dc == 0 and dr == forward) or (dc == 0 and from_row == start_row and dr == forward * 2)
        "N":''',
'''func _is_valid_classic_move(kind: String, team: String, from_col: int, from_row: int, to_col: int, to_row: int, target_piece: Node3D = null) -> bool:
    var dc: int = to_col - from_col
    var dr: int = to_row - from_row
    if dc == 0 and dr == 0:
        return false
    if kind == "P":
        var forward: int = -1 if team == "white" else 1
        var start_row: int = 6 if team == "white" else 1
        if dc == 0:
            if target_piece != null:
                return false
            if dr == forward:
                return true
            if dr == forward * 2 and from_row == start_row and not bool(selected_game_piece.get_meta("has_moved", false)):
                var middle_row: int = from_row + forward
                return _get_game_piece_at(from_col, middle_row) == null
            return false
        if abs(dc) == 1 and dr == forward and target_piece != null:
            return str(target_piece.get_meta("team")) != team
        return false
    var valid_shape := false
    match kind:
        "P":
            valid_shape = false
        "N":''',
"pawn move rules")

# Record first move state on all pieces.
replace_once(
'''    root.set_meta("kind", kind)
    root.set_meta("team", "black" if color.r < 0.5 else "white")''',
'''    root.set_meta("kind", kind)
    root.set_meta("team", "black" if color.r < 0.5 else "white")
    root.set_meta("has_moved", false)''',
"piece moved metadata")

main_path.write_text(source, encoding="utf-8")
print("Classic chess captures, pawn rules and promotion patch applied.")
