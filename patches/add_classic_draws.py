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

state_anchor = 'var active_teammate := 1\n'
if state_anchor not in source:
    raise SystemExit("State anchor not found")
state_add = '''var game_over := false
var last_move: Dictionary = {}
var halfmove_clock := 0
var position_counts: Dictionary = {}
var game_over_panel: Control
var game_over_title: Label
var game_over_detail: Label
'''
if "var game_over := false" not in source:
    source = source.replace(state_anchor, state_anchor + state_add, 1)

replace_func("_start_game", r'''func _start_game(mode_name: String) -> void:
    game_over = false
    last_move.clear()
    halfmove_clock = 0
    position_counts.clear()
    selected_game_piece = null
    current_team = "white"
    active_teammate = 1
    for old_piece in game_piece_nodes:
        if is_instance_valid(old_piece):
            old_piece.queue_free()
    game_piece_nodes.clear()
    _build_game_pieces()
    if game_over_panel:
        game_over_panel.visible = false
    _refresh_team_turn_label()
    menu_panel.visible = false
    game_panel.visible = true
    world_root.visible = true
    for child in game_panel.get_children():
        if child is Panel:
            for sub in child.get_children():
                if sub is Label and sub.text.begins_with("ПАРТИЯ"):
                    sub.text = "ПАРТИЯ  •  " + mode_name
    status_label.text = "Режим: " + mode_name + "  |  Партия началась"
    camera.position = Vector3(0, 10.5, 12.0)
    camera.look_at(Vector3(0, 0.5, -0.4), Vector3.UP)
    _remember_position()''')

replace_func("_handle_game_board_click", r'''func _handle_game_board_click(screen_position: Vector2) -> void:
    if game_over:
        return
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
    var moving_team := current_team
    var is_castle: bool = kind == "K" and abs(col - from_col) == 2
    var is_en_passant: bool = kind == "P" and abs(col - from_col) == 1 and target_piece == null
    var ep_victim: Node3D = _en_passant_victim(piece, col, row) if is_en_passant else null
    var captured := target_piece != null or ep_victim != null
    if target_piece != null:
        game_piece_nodes.erase(target_piece)
        target_piece.queue_free()
    if ep_victim != null:
        game_piece_nodes.erase(ep_victim)
        ep_victim.queue_free()
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
    var promoted := kind == "P" and ((moving_team == "white" and row == 0) or (moving_team == "black" and row == 7))
    if promoted:
        piece.set_meta("kind", "Q")
        _rebuild_promoted_piece(piece)
    last_move = {
        "team": moving_team,
        "kind": kind,
        "from_col": from_col,
        "from_row": from_row,
        "to_col": col,
        "to_row": row,
        "double_pawn": kind == "P" and abs(row - from_row) == 2
    }
    if kind == "P" or captured:
        halfmove_clock = 0
    else:
        halfmove_clock += 1
    selected_game_piece = null
    _advance_team_turn()
    _remember_position()
    _evaluate_classic_position(moving_team, promoted, is_castle, is_en_passant)''')

replace_func("_is_valid_classic_move", r'''func _is_valid_classic_move(kind: String, team: String, from_col: int, from_row: int, to_col: int, to_row: int, target_piece: Node3D = null) -> bool:
    var dc: int = to_col - from_col
    var dr: int = to_row - from_row
    if dc == 0 and dr == 0:
        return false
    if target_piece != null and str(target_piece.get_meta("team")) == team:
        return false
    if target_piece != null and str(target_piece.get_meta("kind")) == "K":
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
        if abs(dc) == 1 and dr == forward:
            if target_piece != null:
                return str(target_piece.get_meta("team")) != team
            return _en_passant_victim(selected_game_piece, to_col, to_row) != null
        return false
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
        var enemy := "black" if team == "white" else "white"
        if _is_square_attacked(from_col + step, from_row, enemy) or _is_square_attacked(from_col + step * 2, from_row, enemy):
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

replace_func("_move_keeps_king_safe", r'''func _move_keeps_king_safe(piece: Node3D, to_col: int, to_row: int, captured: Node3D) -> bool:
    var old_col := int(piece.get_meta("col"))
    var old_row := int(piece.get_meta("row"))
    var old_position := piece.position
    var extra_capture: Node3D = null
    if str(piece.get_meta("kind")) == "P" and captured == null and abs(to_col - old_col) == 1:
        extra_capture = _en_passant_victim(piece, to_col, to_row)
    if captured != null:
        game_piece_nodes.erase(captured)
    if extra_capture != null:
        game_piece_nodes.erase(extra_capture)
    piece.set_meta("col", to_col)
    piece.set_meta("row", to_row)
    piece.position = Vector3((to_col - 3.5) * 1.05, 0.64, (to_row - 3.5) * 0.88 - 0.4)
    var safe := not _is_in_check(current_team)
    piece.set_meta("col", old_col)
    piece.set_meta("row", old_row)
    piece.position = old_position
    if captured != null:
        game_piece_nodes.append(captured)
    if extra_capture != null:
        game_piece_nodes.append(extra_capture)
    return safe''')

# Add terminal state and draw helpers before teammate turn functions.
insert_at = source.find("func _pass_to_teammate(")
if insert_at < 0:
    raise SystemExit("Cannot find teammate turn insertion point")
helpers = r'''func _en_passant_victim(piece: Node3D, to_col: int, to_row: int) -> Node3D:
    if last_move.is_empty() or not bool(last_move.get("double_pawn", false)):
        return null
    var team := str(piece.get_meta("team"))
    var enemy := "black" if team == "white" else "white"
    if str(last_move.get("team", "")) != enemy or str(last_move.get("kind", "")) != "P":
        return null
    var from_row := int(piece.get_meta("row"))
    var from_col := int(piece.get_meta("col"))
    var forward := -1 if team == "white" else 1
    if abs(to_col - from_col) != 1 or to_row - from_row != forward:
        return null
    if int(last_move.get("to_col", -1)) != to_col or int(last_move.get("to_row", -1)) != from_row:
        return null
    var victim := _get_game_piece_at(to_col, from_row)
    if victim == null or str(victim.get_meta("team")) != enemy or str(victim.get_meta("kind")) != "P":
        return null
    return victim

func _remember_position() -> void:
    var cells: Array[String] = []
    for piece in game_piece_nodes:
        if not is_instance_valid(piece):
            continue
        cells.append("%s%s%d%d" % [str(piece.get_meta("team")).substr(0, 1), str(piece.get_meta("kind")), int(piece.get_meta("col")), int(piece.get_meta("row"))])
    cells.sort()
    var key := current_team + "|" + "|".join(cells)
    position_counts[key] = int(position_counts.get(key, 0)) + 1

func _is_insufficient_material() -> bool:
    var minors: Array[Node3D] = []
    for piece in game_piece_nodes:
        if not is_instance_valid(piece):
            continue
        var kind := str(piece.get_meta("kind"))
        if kind == "P" or kind == "R" or kind == "Q":
            return false
        if kind == "B" or kind == "N":
            minors.append(piece)
    if minors.is_empty():
        return true
    if minors.size() == 1:
        return true
    if minors.size() == 2:
        var first := minors[0]
        var second := minors[1]
        if str(first.get_meta("kind")) == "B" and str(second.get_meta("kind")) == "B":
            var first_square := (int(first.get_meta("col")) + int(first.get_meta("row"))) % 2
            var second_square := (int(second.get_meta("col")) + int(second.get_meta("row"))) % 2
            return first_square == second_square
    return false

func _evaluate_classic_position(moving_team: String, promoted: bool, is_castle: bool, is_en_passant: bool) -> void:
    var in_check := _is_in_check(current_team)
    var has_moves := _has_any_legal_move(current_team)
    if in_check and not has_moves:
        _finish_game("ШАХ И МАТ", "Победа " + ("БЕЛЫХ" if moving_team == "white" else "ЧЁРНЫХ"))
        return
    if not in_check and not has_moves:
        _finish_game("ПАТ", "Ничья — у игрока нет допустимых ходов")
        return
    if halfmove_clock >= 100:
        _finish_game("НИЧЬЯ", "Правило 50 ходов — 100 полуходов без взятия и движения пешки")
        return
    for count in position_counts.values():
        if int(count) >= 3:
            _finish_game("НИЧЬЯ", "Троекратное повторение позиции")
            return
    if _is_insufficient_material():
        _finish_game("НИЧЬЯ", "Недостаточно материала для мата")
        return
    if in_check:
        status_label.text = "ШАХ! Король под угрозой."
    elif promoted:
        status_label.text = "Пешка превратилась в ферзя."
    elif is_castle:
        status_label.text = "Рокировка выполнена."
    elif is_en_passant:
        status_label.text = "Взятие на проходе выполнено."
    else:
        status_label.text = "Ход выполнен."

func _finish_game(title_text: String, detail_text: String) -> void:
    game_over = true
    selected_game_piece = null
    status_label.text = title_text + " — " + detail_text
    _show_game_over(title_text, detail_text)

func _show_game_over(title_text: String, detail_text: String) -> void:
    if game_over_panel == null:
        game_over_panel = Control.new()
        game_over_panel.name = "GameOverOverlay"
        game_over_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
        game_over_panel.mouse_filter = Control.MOUSE_FILTER_STOP
        game_panel.add_child(game_over_panel)
        var shade := ColorRect.new()
        shade.color = Color(0.01, 0.009, 0.008, 0.82)
        shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
        game_over_panel.add_child(shade)
        var frame := _panel(game_over_panel, 0.22, 0.27, 0.78, 0.73)
        game_over_title = _add_label(frame, "", Vector2(18, 24), Vector2(620, 52), 30, PALE_GOLD)
        game_over_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        game_over_detail = _add_label(frame, "", Vector2(24, 92), Vector2(590, 58), 16, Color(0.86, 0.81, 0.72))
        game_over_detail.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        var rematch := _ornate_button(frame, "НОВАЯ ПАРТИЯ", 0.08, 0.68, 0.48, 0.91, 16, "party")
        rematch.pressed.connect(_restart_game)
        var menu := _ornate_button(frame, "В МЕНЮ", 0.52, 0.68, 0.92, 0.91, 16, "card")
        menu.pressed.connect(_return_to_menu)
    game_over_title.text = title_text
    game_over_detail.text = detail_text
    game_over_panel.visible = true

func _restart_game() -> void:
    _start_game(selected_mode)

'''
source = source[:insert_at] + helpers + source[insert_at:]

replace_func("_pass_to_teammate", r'''func _pass_to_teammate() -> void:
    if game_over:
        return
    if selected_mode != "Классика":
        status_label.text = "Передача хода будет доступна после подключения правил этого режима."
        return
    active_teammate = (active_teammate % 4) + 1
    selected_game_piece = null
    _refresh_team_turn_label()
    status_label.text = "Очередь передана союзнику. Ход всё ещё за вашей командой."''')

replace_func("_advance_team_turn", r'''func _advance_team_turn() -> void:
    if game_over:
        return
    current_team = "black" if current_team == "white" else "white"
    active_teammate = 1
    selected_game_piece = null
    _refresh_team_turn_label()''')

main_path.write_text(source, encoding="utf-8")
print("Classic draws v20: en passant, 50-move rule, threefold repetition, insufficient material, terminal overlay and board reset applied.")
