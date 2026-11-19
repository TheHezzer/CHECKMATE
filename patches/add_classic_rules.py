from pathlib import Path

root = Path(__file__).resolve().parent.parent
main_path = root / "scripts" / "main.gd"
source = main_path.read_text(encoding="utf-8").replace("\t", "    ")

def replace_between(start_marker: str, end_marker: str, replacement: str, label: str) -> None:
    global source
    start = source.find(start_marker)
    if start < 0:
        raise SystemExit("Start marker not found: " + label)
    end = source.find(end_marker, start + len(start_marker))
    if end < 0:
        raise SystemExit("End marker not found: " + label)
    source = source[:start] + replacement + source[end:]

replace_between(
'''    if target_piece != null:
''',
'''    var from_col:''',
'''    if target_piece != null and str(target_piece.get_meta("team")) == current_team:
        selected_game_piece = target_piece
        status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        return
    var from_col:''',
"piece selection and capture"
)

replace_between(
'''    if not _is_valid_classic_move(''',
'''    _advance_team_turn()''',
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
"move capture and promotion"
)

classic_move = '''func _is_valid_classic_move(kind: String, team: String, from_col: int, from_row: int, to_col: int, to_row: int, target_piece: Node3D = null) -> bool:
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
                return _get_game_piece_at(from_col, from_row + forward) == null
            return false
        if abs(dc) == 1 and dr == forward and target_piece != null:
            return str(target_piece.get_meta("team")) != team
        return false
    var valid_shape := false
    match kind:
        "N":
            valid_shape = (abs(dc) == 1 and abs(dr) == 2) or (abs(dc) == 2 and abs(dr) == 1)
        "R":
            valid_shape = dc == 0 or dr == 0
        "B":
            valid_shape = abs(dc) == abs(dr)
        "Q":
            valid_shape = dc == 0 or dr == 0 or abs(dc) == abs(dr)
        "K":
            valid_shape = max(abs(dc), abs(dr)) == 1
    if not valid_shape:
        return false
    if kind in ["R", "B", "Q"]:
        return _is_classic_path_clear(from_col, from_row, to_col, to_row)
    return true

'''
replace_between(
'''func _is_valid_classic_move(''',
'''func _is_classic_path_clear(''',
classic_move,
"complete classic move validation"
)

if 'root.set_meta("has_moved", false)' not in source:
    marker = '    root.set_meta("kind", kind)\n'
    if marker not in source:
        raise SystemExit("Piece metadata anchor not found")
    source = source.replace(marker, marker + '    root.set_meta("has_moved", false)\n', 1)

main_path.write_text(source, encoding="utf-8")
print("Classic chess capture, pawn movement and promotion rules applied.")
