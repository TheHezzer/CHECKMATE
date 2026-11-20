from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing main.gd anchor: " + label)
    s = s.replace(old, new, 1)

# Route board taps to the actual rendered piece before falling back to the board plane.
rep('''    var hit = Plane(Vector3.UP, 0.59).intersects_ray(ray_origin, ray_direction)
    if hit == null:
        return
    var col: int = roundi(hit.x / 1.12 + 3.5)
    var row: int = roundi((hit.z + 0.4) / 1.0 + 3.5)
''', '''    var hit = Plane(Vector3.UP, 0.59).intersects_ray(ray_origin, ray_direction)
    if hit == null:
        return
    var col: int = roundi(hit.x / 1.12 + 3.5)
    var row: int = roundi((hit.z + 0.4) / 1.0 + 3.5)
    # Perspective can shift a tap from the piece's base to a neighbouring cell.
    # Prefer the nearest visible piece when the user taps directly on a model.
    var nearest_piece: Node3D = null
    var cell_a := camera.unproject_position(Vector3(0.0, 0.64, -0.4))
    var cell_b := camera.unproject_position(Vector3(1.12, 0.64, -0.4))
    var nearest_distance := clampf(cell_a.distance_to(cell_b) * 0.43, 18.0, 52.0)
    for visible_piece in game_piece_nodes:
        if not is_instance_valid(visible_piece):
            continue
        var projected := camera.unproject_position(visible_piece.global_position + Vector3(0, 0.62, 0))
        var distance := projected.distance_to(screen_position)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_piece = visible_piece
    if nearest_piece != null:
        col = int(nearest_piece.get_meta("col"))
        row = int(nearest_piece.get_meta("row"))
''', "screen-space piece hit detection")

# Include the explicit offline session flag in ownership checks.
rep('''if not standard_chess_mode_active and (developer_mode or local_bot_test_active) and (current_team != local_user_team or active_teammate != local_user_slot or int(target_piece.get_meta("owner_slot", 0)) != local_user_slot):''',
    '''if not standard_chess_mode_active and (developer_mode or local_bot_test_active or local_offline_mode_active) and (current_team != local_user_team or active_teammate != local_user_slot or int(target_piece.get_meta("owner_slot", 0)) != local_user_slot):''',
    "offline own-piece selection")
rep('''if not standard_chess_mode_active and (developer_mode or local_bot_test_active) and int(target_piece.get_meta("owner_slot", 0)) != local_user_slot:''',
    '''if not standard_chess_mode_active and (developer_mode or local_bot_test_active or local_offline_mode_active) and int(target_piece.get_meta("owner_slot", 0)) != local_user_slot:''',
    "offline own-piece reselection")

# Passing is supported in both team modes; only ordinary 1v1 chess has no teammate queue.
rep('''    if selected_mode != "Классика":
        status_label.text = "Передача хода будет доступна после подключения правил этого режима."
        return
''', '''    if standard_chess_mode_active or selected_mode == "Стандартные шахматы":
        status_label.text = "В обычных шахматах ход передаётся сопернику только после завершения хода."
        return
''', "pass turn mode gate")
rep('''    if (developer_mode or local_bot_test_active) and active_teammate != local_user_slot:
''', '''    if (developer_mode or local_bot_test_active or local_offline_mode_active) and active_teammate != local_user_slot:
''', "pass schedules offline bot")

# Every teammate owns only the pieces in their file. Refresh highlights immediately on every turn handoff.
rep('''    _refresh_team_turn_label()
    if (developer_mode or local_bot_test_active) and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):
''', '''    _refresh_team_turn_label()
    _update_turn_highlights()
    if (developer_mode or local_bot_test_active or local_offline_mode_active) and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):
''', "advance turn refresh and offline bot")

rep('''        if not is_instance_valid(piece) or str(piece.get_meta("team")) != current_team:
            continue
        var fc := int(piece.get_meta("col"))
''', '''        if not is_instance_valid(piece) or str(piece.get_meta("team")) != current_team:
            continue
        if not standard_chess_mode_active and int(piece.get_meta("owner_slot", 0)) != active_teammate:
            continue
        var fc := int(piece.get_meta("col"))
''', "bot controls only its assigned pair")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v69: reliable piece tapping, working teammate pass, bot ownership and turn-highlight refresh applied.")
