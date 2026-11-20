from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

# Add a dedicated in-game hint line.
rep("var team_turn_label: Label\n", "var team_turn_label: Label\nvar game_hint_label: Label\n", "game hint variable")

rep('''    team_turn_label.offset_bottom = 30
''', '''    team_turn_label.offset_bottom = 34
    team_turn_label.add_theme_font_size_override("font_size", 22)
    game_hint_label = _add_label(game_panel, "ТВОИ ФИГУРЫ БУДУТ ПОДСВЕЧЕНЫ", Vector2.ZERO, Vector2(680, 26), 14, Color(0.55, 0.92, 0.98))
    game_hint_label.anchor_left = 0.5
    game_hint_label.anchor_right = 0.5
    game_hint_label.anchor_top = 0.17
    game_hint_label.anchor_bottom = 0.17
    game_hint_label.offset_left = -340
    game_hint_label.offset_right = 340
    game_hint_label.offset_top = 0
    game_hint_label.offset_bottom = 26
    game_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
''', "turn label and hint")

# The lower chess glyphs are preview navigation only, not kit selection.
start = s.index("func _select_main_piece(index: int) -> void:")
end = s.index("func _refresh_main_piece_shelf() -> void:", start)
new_select = '''func _select_main_piece(index: int) -> void:
    if index < 0 or index >= PIECES.size():
        return
    selected_piece = index
    var name: String = PIECES[index]
    _build_preview_piece(name)
    var title := menu_panel.find_child("PieceName", true, false) as Label
    if title:
        title.text = name.to_upper() + ("  •  🔒" if not unlocked_pieces.has(name) else "")
    var hint := menu_panel.find_child("PieceLockHint", true, false) as Label
    if hint:
        hint.visible = false
    _refresh_main_piece_shelf()

'''
s = s[:start] + new_select + s[end:]

# Make the central carousel arrows obey the same preview-only behavior.
start = s.index("func _change_piece(direction: int) -> void:")
end = s.index("func _panel(", start)
new_change = '''func _change_piece(direction: int) -> void:
    selected_piece = posmod(selected_piece + direction, PIECES.size())
    var piece_name: String = PIECES[selected_piece]
    _select_main_piece(selected_piece)

'''
s = s[:start] + new_change + s[end:]

# Each column belongs to one teammate: pawn + the back-rank figure in that file.
rep('''    root.set_meta("kind", kind)
    root.set_meta("has_moved", false)
''', '''    root.set_meta("kind", kind)
    root.set_meta("owner_slot", col + 1)
    root.set_meta("has_moved", false)
''', "piece owner slot")
rep('''    root.scale = Vector3(1.12, 1.12, 1.12)
''', '''    root.scale = Vector3(1.30, 1.30, 1.30)
''', "larger game pieces")

# Make personal pieces visible at all times with cyan rings; active team pieces retain gold rings.
rep('''        var ring := MeshInstance3D.new()
        var ring_mesh := TorusMesh.new()
        ring_mesh.inner_radius = 0.30
        ring_mesh.outer_radius = 0.39
''', '''        var is_my_piece := developer_mode and str(piece.get_meta("team")) == local_user_team and int(piece.get_meta("owner_slot", 0)) == local_user_slot
        if str(piece.get_meta("team")) != current_team and not is_my_piece:
            continue
        var ring := MeshInstance3D.new()
        var ring_mesh := TorusMesh.new()
        ring_mesh.inner_radius = 0.34 if is_my_piece else 0.30
        ring_mesh.outer_radius = 0.45 if is_my_piece else 0.39
''', "personal ring geometry")
rep('''        ring_material.albedo_color = Color(0.95, 0.72, 0.28, 0.82)
        ring_material.emission_enabled = true
        ring_material.emission = Color(0.62, 0.32, 0.08)
''', '''        ring_material.albedo_color = Color(0.20, 0.92, 1.0, 0.96) if is_my_piece else Color(0.95, 0.72, 0.28, 0.82)
        ring_material.emission_enabled = true
        ring_material.emission = Color(0.05, 0.62, 0.82) if is_my_piece else Color(0.62, 0.32, 0.08)
''', "personal ring colors")

# Start the developer user on a file matching their selected role.
rep('''    active_teammate = randi_range(1, CLASSIC_TEAM_SIZE)
''', '''    active_teammate = local_user_slot if developer_mode else randi_range(1, CLASSIC_TEAM_SIZE)
''', "user starts on own slot")
rep('''    team_next_player = {"white": (active_teammate % CLASSIC_TEAM_SIZE) + 1, "black": randi_range(1, CLASSIC_TEAM_SIZE)}
''', '''    team_next_player = {"white": (active_teammate % CLASSIC_TEAM_SIZE) + 1, "black": randi_range(1, CLASSIC_TEAM_SIZE)}
''', "team queue initialization")

# Board framing: tighter, higher-resolution view and bigger squares.
rep('''    camera.fov = 54.0
    camera.position = Vector3(0, 15.5, 13.8)
    camera.look_at(Vector3(0, 0.45, -0.4), Vector3.UP)
''', '''    camera.fov = 47.0
    camera.position = Vector3(0, 13.2, 11.9)
    camera.look_at(Vector3(0, 0.50, -0.4), Vector3.UP)
''', "board camera")
rep('''Vector3(1.10, 0.055, 0.98), square_color''', '''Vector3(1.105, 0.065, 0.99), square_color''', "larger squares")

# Make active turn label show the actual nickname rather than only a slot number.
start = s.index("func _refresh_team_turn_label() -> void:")
end = s.index("func _select_main_piece(index: int) -> void:", start)
new_turn = '''func _refresh_team_turn_label() -> void:
    if not team_turn_label:
        return
    var team_name := "БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ"
    var active_name := "Игрок " + str(active_teammate)
    if developer_mode:
        for entry in local_bot_roster:
            if str(entry.get("team", "")) == current_team and int(entry.get("slot", -1)) + 1 == active_teammate:
                active_name = str(entry.get("name", active_name))
                break
        if current_team == local_user_team and active_teammate == local_user_slot:
            active_name = "TheHezzer • ВЫ"
    elif current_team == _local_team():
        active_name = account_username if not account_username.is_empty() else "Вы"
    team_turn_label.text = "ХОД: " + team_name + "  •  " + active_name
    if online_active:
        team_turn_label.text += "  |  " + ("ВАША КОМАНДА" if _local_team() == current_team else "СОПЕРНИК")

'''
s = s[:start] + new_turn + s[end:]

# On the board, the local tester may select only their own two pieces.
rep('''        if target_piece != null and str(target_piece.get_meta("team")) == local_team and (not online_active or online_match_id.is_empty() or str(target_piece.get_meta("ownerPlayerId", "")) == online_player_id):
            selected_game_piece = target_piece
''', '''        if target_piece != null and str(target_piece.get_meta("team")) == local_team and (not online_active or online_match_id.is_empty() or str(target_piece.get_meta("ownerPlayerId", "")) == online_player_id):
            if developer_mode and (current_team != local_user_team or active_teammate != local_user_slot or int(target_piece.get_meta("owner_slot", 0)) != local_user_slot):
                status_label.text = "Эта фигура принадлежит другому игроку. Твои две фигуры отмечены голубым кольцом."
                return
            selected_game_piece = target_piece
''', "restrict human piece ownership")
rep('''    if target_piece != null and str(target_piece.get_meta("team")) == local_team:
        selected_game_piece = target_piece
''', '''    if target_piece != null and str(target_piece.get_meta("team")) == local_team:
        if developer_mode and int(target_piece.get_meta("owner_slot", 0)) != local_user_slot:
            status_label.text = "Это фигура союзника. Ищи голубое кольцо."
            return
        selected_game_piece = target_piece
''', "restrict switching to teammate pieces")

# Player's two figures are named in the tutorial hint.
rep('''    status_label.text = "Первыми ходят БЕЛЫЕ. Команда белых решает, какой ход сделать."
''', '''    status_label.text = "Выбери фигуру с ГОЛУБЫМ кольцом, затем нажми клетку назначения."
    if developer_mode and game_hint_label:
        var role_name := _role_name_for_slot(local_user_slot)
        game_hint_label.text = "ТВОИ ФИГУРЫ: ПЕШКА + " + role_name.to_upper() + "  •  ГОЛУБОЕ КОЛЬЦО  •  ТВОЯ ЛИНИЯ №" + str(local_user_slot)
    elif game_hint_label:
        game_hint_label.text = "НАЖМИ НА СВОЮ ФИГУРУ, ЗАТЕМ НА КЛЕТКУ ДЛЯ ХОДА"
''', "gameplay hint")

# Each bot is assigned the unique back-rank role on its own file, not the same selected role.
rep('''func _start_local_bot_queue() -> void:
    local_bot_roster.clear()
    var white := PackedStringArray()
    var black := PackedStringArray()
    local_user_team = "white"
    local_user_slot = randi_range(1, CLASSIC_TEAM_SIZE)
    for slot in range(CLASSIC_TEAM_SIZE):
        var white_name := "TheHezzer" if slot + 1 == local_user_slot else "Bot_%d" % (slot + 1 if slot + 1 < local_user_slot else slot)
        var black_name := "Bot_%d" % (slot + 8)
        white.append("%02d  %s  •  Пешка + %s" % [slot + 1, white_name, selected_match_piece])
        black.append("%02d  %s  •  Пешка + %s" % [slot + 1, black_name, selected_match_piece])
        local_bot_roster.append({"name": white_name, "team": "white", "slot": slot, "bot": white_name != "TheHezzer"})
        local_bot_roster.append({"name": black_name, "team": "black", "slot": slot, "bot": true})
''', '''func _start_local_bot_queue() -> void:
    local_bot_roster.clear()
    var white := PackedStringArray()
    var black := PackedStringArray()
    local_user_team = "white"
    var role_slots := _slots_for_role(selected_match_piece)
    local_user_slot = role_slots[randi_range(0, role_slots.size() - 1)] + 1 if not role_slots.is_empty() else randi_range(1, CLASSIC_TEAM_SIZE)
    for slot in range(CLASSIC_TEAM_SIZE):
        var role := _role_name_for_slot(slot + 1)
        var white_name := "TheHezzer" if slot + 1 == local_user_slot else "Bot_%d" % (slot + 1 if slot + 1 < local_user_slot else slot)
        var black_name := "Bot_%d" % (slot + 8)
        white.append("%02d  %s  •  Пешка + %s" % [slot + 1, white_name, role])
        black.append("%02d  %s  •  Пешка + %s" % [slot + 1, black_name, role])
        local_bot_roster.append({"name": white_name, "team": "white", "slot": slot, "role": role, "bot": white_name != "TheHezzer"})
        local_bot_roster.append({"name": black_name, "team": "black", "slot": slot, "role": role, "bot": true})
''', "diverse bot roles")

# Add helper functions mapping each file to the two-piece loadout.
marker = "func _launch_local_bot_match() -> void:\n"
helpers = '''func _role_name_for_slot(slot: int) -> String:
    var roles := ["Ладья", "Конь", "Слон", "Ферзь", "Король", "Слон", "Конь", "Ладья"]
    return roles[clampi(slot - 1, 0, 7)]

func _slots_for_role(role: String) -> Array[int]:
    var result: Array[int] = []
    for slot in range(1, CLASSIC_TEAM_SIZE + 1):
        if _role_name_for_slot(slot) == role:
            result.append(slot - 1)
    return result

'''
if marker not in s:
    raise SystemExit("Missing bot launch function")
s = s.replace(marker, helpers + marker, 1)

# The local test starts with the selected player as the active white teammate.
rep('''    _start_game(selected_mode)
    local_user_team = "white"
    status_label.text = "ТЕСТ С БОТАМИ • Вы за белых. Чёрные и союзники — Bot_1…Bot_16."
''', '''    local_user_team = "white"
    _start_game(selected_mode)
    active_teammate = local_user_slot
    team_next_player["white"] = (local_user_slot % CLASSIC_TEAM_SIZE) + 1
    _refresh_team_turn_label()
    _update_turn_highlights()
    status_label.text = "ТЫ ИГРАЕШЬ ЗА БЕЛЫХ. Твои фигуры отмечены голубыми кольцами."
''', "start user-controlled bot game")

# Advance turns to the next named teammate and schedule bot actions on BOTH sides.
rep('''    if developer_mode and current_team != local_user_team and not game_over:
        if bot_turn_timer == null:
            bot_turn_timer = Timer.new()
            bot_turn_timer.one_shot = true
            add_child(bot_turn_timer)
            bot_turn_timer.timeout.connect(_make_bot_move)
        bot_turn_timer.start(1.15)
''', '''    if developer_mode and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):
        if bot_turn_timer == null:
            bot_turn_timer = Timer.new()
            bot_turn_timer.one_shot = true
            add_child(bot_turn_timer)
            bot_turn_timer.timeout.connect(_make_bot_move)
        bot_turn_timer.start(1.0)
''', "schedule teammate bots")

# Bot searches only moves for the currently active bot's owned file and announces correct nickname.
rep('''        if not is_instance_valid(piece) or str(piece.get_meta("team")) != current_team:
            continue
''', '''        if not is_instance_valid(piece) or str(piece.get_meta("team")) != current_team:
            continue
        if int(piece.get_meta("owner_slot", 0)) != active_teammate:
            continue
''', "bot filters own two pieces")
rep('''    if candidates.is_empty():
        _evaluate_classic_position(current_team, false, false, false)
        return
''', '''    if candidates.is_empty():
        # No legal move for this teammate: pass the turn to the next player.
        _advance_team_turn()
        return
''', "bot skip no legal move")
rep('''    status_label.text = "Ходит " + ("Bot_9" if current_team == "black" else "Bot_1") + "…"
    _apply_classic_move(int(move.fc), int(move.fr), int(move.tc), int(move.tr), false)
''', '''    var bot_name := "Бот"
    for entry in local_bot_roster:
        if str(entry.get("team", "")) == current_team and int(entry.get("slot", -1)) + 1 == active_teammate:
            bot_name = str(entry.get("name", "Бот"))
            break
    status_label.text = "ХОДИТ " + bot_name + " • " + _role_name_for_slot(active_teammate)
    _apply_classic_move(int(move.fc), int(move.fr), int(move.tc), int(move.tr), false)
''', "bot move announcement")

# Pass-turn also hands the turn to the next player and triggers their bot action.
rep('''    _refresh_team_turn_label()
    status_label.text = "Очередь передана союзнику. Ход всё ещё за вашей командой."
''', '''    _refresh_team_turn_label()
    _update_turn_highlights()
    status_label.text = "Очередь передана союзнику."
    if developer_mode and active_teammate != local_user_slot:
        if bot_turn_timer == null:
            bot_turn_timer = Timer.new()
            bot_turn_timer.one_shot = true
            add_child(bot_turn_timer)
            bot_turn_timer.timeout.connect(_make_bot_move)
        bot_turn_timer.start(0.8)
''', "pass to teammate bot")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v53 gameplay ownership, bot turns, preview-only selector, board camera and HUD patch applied.")
