from pathlib import Path

root = Path(__file__).resolve().parent.parent
main_path = root / "scripts" / "main.gd"
source = main_path.read_text(encoding="utf-8").replace("\t", "    ")

def replace_func(name: str, replacement: str) -> None:
    global source
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        raise SystemExit("Function not found: " + name)
    end = source.find("\nfunc ", start + len(marker))
    if end < 0:
        end = len(source)
    source = source[:start] + replacement.rstrip() + "\n" + source[end:]

replace_func("_handle_game_board_click", r'''func _handle_game_board_click(screen_position: Vector2) -> void:
    if selected_mode != "Классика":
        status_label.text = "Этот режим пока в разработке. Сейчас тестируем механику классической партии."
        return
    if team_turn_label and team_turn_label.get_global_rect().has_point(screen_position):
        return
    var ray_origin: Vector3 = camera.project_ray_origin(screen_position)
    var ray_direction: Vector3 = camera.project_ray_normal(screen_position)
    var hit = Plane(Vector3.UP, 0.59).intersects_ray(ray_origin, ray_direction)
    if hit == null:
        return
    var col: int = roundi(hit.x / 1.05 + 3.5)
    var row: int = roundi((hit.z + 0.4) / 0.88 + 3.5)
    if col < 0 or col > 7 or row < 0 or row > 7:
        return
    var target_piece: Node3D = _get_game_piece_at(col, row)
    if selected_game_piece == null:
        if target_piece != null and str(target_piece.get_meta("team")) == current_team:
            selected_game_piece = target_piece
            status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + ". Выбери клетку для хода."
        else:
            status_label.text = "Сейчас ходят " + ("белые" if current_team == "white" else "чёрные") + ". Выбери свою фигуру."
        return
    if target_piece == selected_game_piece:
        selected_game_piece = null
        status_label.text = "Выбор отменён."
        return
    if target_piece != null and str(target_piece.get_meta("team")) == current_team:
        selected_game_piece = target_piece
        status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        return
    var piece := selected_game_piece
    var from_col: int = int(piece.get_meta("col"))
    var from_row: int = int(piece.get_meta("row"))
    var kind: String = str(piece.get_meta("kind"))
    if not _is_valid_classic_move(kind, current_team, from_col, from_row, col, row, target_piece):
        status_label.text = "Недопустимый ход для этой фигуры."
        return
    if not _move_keeps_king_safe(piece, col, row, target_piece):
        status_label.text = "Нельзя оставлять своего короля под шахом."
        return
    var is_castle: bool = kind == "K" and abs(col - from_col) == 2
    if target_piece != null:
        game_piece_nodes.erase(target_piece)
        target_piece.queue_free()
    piece.position = Vector3((col - 3.5) * 1.05, 0.64, (row - 3.5) * 0.88 - 0.4)
    piece.set_meta("col", col)
    piece.set_meta("row", row)
    piece.set_meta("has_moved", true)
    if is_castle:
        var rook_from_col := 7 if col > from_col else 0
        var rook_to_col := col - 1 if col > from_col else col + 1
        var rook := _get_game_piece_at(rook_from_col, from_row)
        if rook != null:
            rook.position = Vector3((rook_to_col - 3.5) * 1.05, 0.64, (from_row - 3.5) * 0.88 - 0.4)
            rook.set_meta("col", rook_to_col)
            rook.set_meta("has_moved", true)
    var promoted := kind == "P" and ((current_team == "white" and row == 0) or (current_team == "black" and row == 7))
    if promoted:
        piece.set_meta("kind", "Q")
        _rebuild_promoted_piece(piece)
    selected_game_piece = null
    var moving_team := current_team
    _advance_team_turn()
    if _is_in_check(current_team):
        if _has_any_legal_move(current_team):
            status_label.text = "ШАХ! Король под угрозой."
        else:
            status_label.text = "ШАХ И МАТ! Победа " + ("белых." if moving_team == "white" else "чёрных.")
    elif not _has_any_legal_move(current_team):
        status_label.text = "ПАТ! Ничья."
    elif promoted:
        status_label.text = "Пешка превратилась в ферзя."
    elif is_castle:
        status_label.text = "Рокировка выполнена."
    else:
        status_label.text = "Ход выполнен."''')

replace_func("_is_valid_classic_move", r'''func _is_valid_classic_move(kind: String, team: String, from_col: int, from_row: int, to_col: int, to_row: int, target_piece: Node3D = null) -> bool:
    var dc: int = to_col - from_col
    var dr: int = to_row - from_row
    if dc == 0 and dr == 0:
        return false
    if target_piece != null and str(target_piece.get_meta("team")) == team:
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
        return abs(dc) == 1 and dr == forward and target_piece != null
    if kind == "K" and abs(dc) == 2 and dr == 0:
        if bool(selected_game_piece.get_meta("has_moved", false)) or _is_in_check(team):
            return false
        var rook_col := 7 if dc > 0 else 0
        var rook := _get_game_piece_at(rook_col, from_row)
        if rook == null or str(rook.get_meta("kind")) != "R" or str(rook.get_meta("team")) != team or bool(rook.get_meta("has_moved", false)):
            return false
        var step := 1 if dc > 0 else -1
        var scan := from_col + step
        while scan != rook_col:
            if _get_game_piece_at(scan, from_row) != null:
                return false
            scan += step
        if _is_square_attacked(from_col + step, from_row, "black" if team == "white" else "white"):
            return false
        if _is_square_attacked(from_col + step * 2, from_row, "black" if team == "white" else "white"):
            return false
        return true
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
    return true''')

helpers = r'''func _find_king(team: String) -> Node3D:
    for piece in game_piece_nodes:
        if is_instance_valid(piece) and str(piece.get_meta("team")) == team and str(piece.get_meta("kind")) == "K":
            return piece
    return null

func _is_square_attacked(col: int, row: int, by_team: String) -> bool:
    for piece in game_piece_nodes:
        if not is_instance_valid(piece) or str(piece.get_meta("team")) != by_team:
            continue
        var pc := int(piece.get_meta("col"))
        var pr := int(piece.get_meta("row"))
        var dc := col - pc
        var dr := row - pr
        var kind := str(piece.get_meta("kind"))
        match kind:
            "P":
                var forward := -1 if by_team == "white" else 1
                if abs(dc) == 1 and dr == forward:
                    return true
            "N":
                if (abs(dc) == 1 and abs(dr) == 2) or (abs(dc) == 2 and abs(dr) == 1):
                    return true
            "K":
                if max(abs(dc), abs(dr)) == 1:
                    return true
            "R":
                if (dc == 0 or dr == 0) and (dc != 0 or dr != 0) and _is_classic_path_clear(pc, pr, col, row):
                    return true
            "B":
                if abs(dc) == abs(dr) and dc != 0 and _is_classic_path_clear(pc, pr, col, row):
                    return true
            "Q":
                if (dc == 0 or dr == 0 or abs(dc) == abs(dr)) and (dc != 0 or dr != 0) and _is_classic_path_clear(pc, pr, col, row):
                    return true
    return false

func _is_in_check(team: String) -> bool:
    var king := _find_king(team)
    if king == null:
        return true
    var enemy := "black" if team == "white" else "white"
    return _is_square_attacked(int(king.get_meta("col")), int(king.get_meta("row")), enemy)

func _move_keeps_king_safe(piece: Node3D, to_col: int, to_row: int, captured: Node3D) -> bool:
    var old_col := int(piece.get_meta("col"))
    var old_row := int(piece.get_meta("row"))
    var old_position := piece.position
    if captured != null:
        game_piece_nodes.erase(captured)
    piece.set_meta("col", to_col)
    piece.set_meta("row", to_row)
    piece.position = Vector3((to_col - 3.5) * 1.05, 0.64, (to_row - 3.5) * 0.88 - 0.4)
    var safe := not _is_in_check(current_team)
    piece.set_meta("col", old_col)
    piece.set_meta("row", old_row)
    piece.position = old_position
    if captured != null:
        game_piece_nodes.append(captured)
    return safe

func _has_any_legal_move(team: String) -> bool:
    var old_team := current_team
    var old_selected := selected_game_piece
    current_team = team
    for piece in game_piece_nodes:
        if not is_instance_valid(piece) or str(piece.get_meta("team")) != team:
            continue
        selected_game_piece = piece
        var fc := int(piece.get_meta("col"))
        var fr := int(piece.get_meta("row"))
        var kind := str(piece.get_meta("kind"))
        for tc in range(8):
            for tr in range(8):
                var target := _get_game_piece_at(tc, tr)
                if target == piece:
                    continue
                if _is_valid_classic_move(kind, team, fc, fr, tc, tr, target) and _move_keeps_king_safe(piece, tc, tr, target):
                    current_team = old_team
                    selected_game_piece = old_selected
                    return true
    current_team = old_team
    selected_game_piece = old_selected
    return false

func _rebuild_promoted_piece(piece: Node3D) -> void:
    for child in piece.get_children():
        piece.remove_child(child)
        child.queue_free()
    var color := Color(0.88, 0.80, 0.66) if str(piece.get_meta("team")) == "white" else Color(0.12, 0.095, 0.07)
    var mat := _material(color, 0.34, 0.15)
    _add_piece_cylinder(piece, 0.27, 0.12, 0.0, mat)
    _add_piece_cylinder(piece, 0.18, 0.48, 0.18, mat)
    _add_piece_cylinder(piece, 0.24, 0.10, 0.43, mat)
    _add_piece_sphere(piece, 0.22, 0.78, mat)
    _add_piece_cylinder(piece, 0.27, 0.10, 0.98, mat)

'''
insert_at = source.find("func _pass_to_teammate(")
if insert_at < 0:
    raise SystemExit("Cannot find helper insertion point")
source = source[:insert_at] + helpers + source[insert_at:]

main_path.write_text(source, encoding="utf-8")
print("Classic check, checkmate, castling and visible queen promotion rules applied.")
