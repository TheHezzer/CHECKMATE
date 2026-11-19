from pathlib import Path

root = Path(__file__).resolve().parent.parent
main_path = root / "scripts" / "main.gd"
source = main_path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if old not in source:
        raise SystemExit("Patch anchor not found: " + label)
    source = source.replace(old, new, 1)

replace_once(
    "var mode_description_label: Label\n",
    "var mode_description_label: Label\nvar game_piece_nodes: Array[Node3D] = []\nvar selected_game_piece: Node3D\nvar current_team := \"white\"\nvar active_teammate := 1\nvar team_turn_label: Label\n",
    "classic game state"
)

replace_once(
    "func _build_game_pieces() -> void:\n\tvar back_rank",
    "func _build_game_pieces() -> void:\n\tgame_piece_nodes.clear()\n\tvar back_rank",
    "clear game pieces"
)

replace_once(
    "\troot.position = Vector3(x, 0.64, z)\n\tworld_root.add_child(root)",
    "\troot.position = Vector3(x, 0.64, z)\n\tvar col: int = roundi(x / 1.05 + 3.5)\n\tvar row: int = roundi((z + 0.4) / 0.88 + 3.5)\n\troot.set_meta(\"col\", col)\n\troot.set_meta(\"row\", row)\n\troot.set_meta(\"kind\", kind)\n\troot.set_meta(\"team\", \"black\" if color.r < 0.5 else \"white\")\n\tworld_root.add_child(root)\n\tgame_piece_nodes.append(root)",
    "piece board coordinates"
)

replace_once(
    "\tstatus_label.offset_bottom = -8\n\t_build_preparation_screen()",
    "\tstatus_label.offset_bottom = -8\n\tteam_turn_label = _add_label(game_panel, \"ХОД: БЕЛЫЕ • ИГРОК 1/4\", Vector2.ZERO, Vector2(420, 30), 16, PALE_GOLD)\n\tteam_turn_label.anchor_left = 0.5\n\tteam_turn_label.anchor_right = 0.5\n\tteam_turn_label.anchor_top = 0.12\n\tteam_turn_label.anchor_bottom = 0.12\n\tteam_turn_label.offset_left = -210\n\tteam_turn_label.offset_right = 210\n\tteam_turn_label.offset_top = 0\n\tteam_turn_label.offset_bottom = 30\n\tvar pass_turn := _ornate_button(game_panel, \"ПЕРЕДАТЬ ХОД СОЮЗНИКУ\", 0.27, 0.88, 0.49, 0.98, 13, \"nav\")\n\tpass_turn.pressed.connect(_pass_to_teammate)\n\tvar end_turn := _ornate_button(game_panel, \"ЗАВЕРШИТЬ ХОД\", 0.51, 0.88, 0.73, 0.98, 13, \"party\")\n\tend_turn.pressed.connect(_advance_team_turn)\n\t_build_preparation_screen()",
    "classic turn controls"
)

replace_once(
    "func _input(event: InputEvent) -> void:\n\tif menu_panel == null or not menu_panel.visible or preview_container == null:",
    "func _input(event: InputEvent) -> void:\n\tif game_panel != null and game_panel.visible and world_root.visible:\n\t\tif event is InputEventScreenTouch and event.pressed:\n\t\t\t_handle_game_board_click(event.position)\n\t\t\treturn\n\t\tif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:\n\t\t\t_handle_game_board_click(event.position)\n\t\t\treturn\n\tif menu_panel == null or not menu_panel.visible or preview_container == null:",
    "board click input"
)

replace_once(
    "func _start_game(mode_name: String) -> void:\n\tmenu_panel.visible = false",
    "func _start_game(mode_name: String) -> void:\n\tcurrent_team = \"white\"\n\tactive_teammate = 1\n\tselected_game_piece = null\n\t_refresh_team_turn_label()\n\tmenu_panel.visible = false",
    "reset classic turn state"
)

replace_once(
    "func _return_to_menu() -> void:\n\tgame_panel.visible = false",
    "func _return_to_menu() -> void:\n\tselected_game_piece = null\n\tgame_panel.visible = false",
    "clear selection on return"
)

functions = """
func _handle_game_board_click(screen_position: Vector2) -> void:
    if selected_mode != "Классика":
        status_label.text = "Этот режим пока в разработке. Сейчас тестируем механику классической партии."
        return
    if team_turn_label and team_turn_label.get_global_rect().has_point(screen_position):
        return
    var ray_origin: Vector3 = camera.project_ray_origin(screen_position)
    var ray_direction: Vector3 = camera.project_ray_normal(screen_position)
    var board_plane := Plane(Vector3.UP, 0.59)
    var hit = board_plane.intersects_ray(ray_origin, ray_direction)
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
            status_label.text = "Выбрана фигура: " + str(selected_game_piece.get_meta("kind")) + ". Выбери клетку для хода."
        else:
            status_label.text = "Сейчас ходят " + ("белые" if current_team == "white" else "чёрные") + ". Выбери свою фигуру."
        return
    if target_piece == selected_game_piece:
        selected_game_piece = null
        status_label.text = "Выбор отменён."
        return
    if target_piece != null:
        if str(target_piece.get_meta("team")) == current_team:
            selected_game_piece = target_piece
            status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        else:
            status_label.text = "На этой клетке противник. Боевой вызов добавим следующим этапом."
        return
    var from_col: int = int(selected_game_piece.get_meta("col"))
    var from_row: int = int(selected_game_piece.get_meta("row"))
    var kind: String = str(selected_game_piece.get_meta("kind"))
    if not _is_valid_classic_move(kind, current_team, from_col, from_row, col, row):
        status_label.text = "Недопустимый ход для этой фигуры."
        return
    selected_game_piece.position = Vector3((col - 3.5) * 1.05, 0.64, (row - 3.5) * 0.88 - 0.4)
    selected_game_piece.set_meta("col", col)
    selected_game_piece.set_meta("row", row)
    selected_game_piece = null
    status_label.text = "Ход выполнен. Очередь перешла другой команде."
    _advance_team_turn()

func _get_game_piece_at(col: int, row: int) -> Node3D:
    for piece in game_piece_nodes:
        if is_instance_valid(piece) and int(piece.get_meta("col")) == col and int(piece.get_meta("row")) == row:
            return piece
    return null

func _is_valid_classic_move(kind: String, team: String, from_col: int, from_row: int, to_col: int, to_row: int) -> bool:
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

func _is_classic_path_clear(from_col: int, from_row: int, to_col: int, to_row: int) -> bool:
    var step_col: int = int(sign(to_col - from_col))
    var step_row: int = int(sign(to_row - from_row))
    var col: int = from_col + step_col
    var row: int = from_row + step_row
    while col != to_col or row != to_row:
        if _get_game_piece_at(col, row) != null:
            return false
        col += step_col
        row += step_row
    return true

func _pass_to_teammate() -> void:
    if selected_mode != "Классика":
        status_label.text = "Передача хода будет доступна после подключения правил этого режима."
        return
    active_teammate = (active_teammate % 4) + 1
    selected_game_piece = null
    _refresh_team_turn_label()
    status_label.text = "Очередь передана союзнику. Ход всё ещё за вашей командой."

func _advance_team_turn() -> void:
    current_team = "black" if current_team == "white" else "white"
    active_teammate = 1
    selected_game_piece = null
    _refresh_team_turn_label()

func _refresh_team_turn_label() -> void:
    if team_turn_label:
        var team_name := "БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ"
        team_turn_label.text = "ХОД: " + team_name + " • ИГРОК " + str(active_teammate) + "/4"
"""
source += "\n" + "\n".join(("\t" * ((len(line) - len(line.lstrip(" "))) // 4) + line.lstrip(" ")) if line.startswith("    ") else line for line in functions.splitlines())
main_path.write_text(source, encoding="utf-8")
print("Classic local turn and movement prototype added.")
