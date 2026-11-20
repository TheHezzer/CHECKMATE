from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

if "var local_self_play_active := false" not in s:
    anchor = "var local_offline_mode_active := false"
    if anchor not in s:
        raise SystemExit("Missing local offline flag")
    s = s.replace(anchor, anchor + "\nvar local_self_play_active := false", 1)

# Keep self-play isolated from all bot automation and clear it when leaving the match.
s = s.replace(
    "    local_bot_test_active = false\n    local_offline_mode_active = false\n    standard_chess_mode_active = false",
    "    local_bot_test_active = false\n    local_offline_mode_active = false\n    local_self_play_active = false\n    standard_chess_mode_active = false",
    1
)

# In self-play the local player controls whichever color has the move.
old = "    var local_team := _local_team()\n"
new = "    var local_team := current_team if local_self_play_active else _local_team()\n"
if old not in s:
    raise SystemExit("Missing local team click anchor")
s = s.replace(old, new, 1)

# Self-play must never start automated bot turns.
s = s.replace(
    'if (developer_mode or local_bot_test_active or local_offline_mode_active) and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):',
    'if not local_self_play_active and (developer_mode or local_bot_test_active or local_offline_mode_active) and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):',
    1
)
s = s.replace(
    'if not (developer_mode or local_bot_test_active or local_offline_mode_active) or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:',
    'if local_self_play_active or not (developer_mode or local_bot_test_active or local_offline_mode_active) or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:',
    1
)
s = s.replace(
    'if not (developer_mode or local_bot_test_active or local_offline_mode_active) or game_over or local_opening_vote_active:',
    'if local_self_play_active or not (developer_mode or local_bot_test_active or local_offline_mode_active) or game_over or local_opening_vote_active:',
    1
)

# Avoid timeouts during a manual testing session.
clock_anchor = "func _tick_local_game_clock() -> void:\n    if not game_panel or not game_panel.visible or game_over or online_active:"
if clock_anchor not in s:
    raise SystemExit("Missing local clock function")
s = s.replace(clock_anchor,
    "func _tick_local_game_clock() -> void:\n    if local_self_play_active:\n        return\n    if not game_panel or not game_panel.visible or game_over or online_active:", 1)

# Show a clear label while both sides are controlled by the same person.
label_anchor = '    var team_name := "БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ"\n    var active_name := "Игрок " + str(active_teammate)\n'
if label_anchor not in s:
    raise SystemExit("Missing turn label anchor")
s = s.replace(label_anchor,
    '    var team_name := "БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ"\n    var active_name := "ТЫ • ОБЕ СТОРОНЫ" if local_self_play_active else "Игрок " + str(active_teammate)\n', 1)

# Admin test panel: add the new self-play option alongside voting test.
button_anchor = '''    var voting := _ornate_button(frame, "ТЕСТ КОМАНДНОГО ГОЛОСОВАНИЯ", 0.05, 0.34, 0.48, 0.46, 13, "card")
    voting.pressed.connect(_developer_test_voting)
'''
if button_anchor not in s:
    raise SystemExit("Missing admin voting button anchor")
s = s.replace(button_anchor, button_anchor + '''    var self_play := _ornate_button(frame, "ИГРА С САМИМ СОБОЙ • ТЕСТ ШАХМАТ", 0.52, 0.34, 0.95, 0.46, 13, "party")
    self_play.pressed.connect(_developer_test_self_play)
''', 1)

# Randomize the player's assigned side in the local bot test (online server already randomizes colors).
s = s.replace('    local_user_team = "white"\n    var role_slots := _slots_for_role(selected_match_piece)',
              '    local_user_team = "white" if randi_range(0, 1) == 0 else "black"\n    var role_slots := _slots_for_role(selected_match_piece)', 1)
old_names = '''        var white_name := "TheHezzer" if slot + 1 == local_user_slot else "Bot_%d" % (slot + 1 if slot + 1 < local_user_slot else slot)
        var black_name := "Bot_%d" % (slot + 8)
'''
new_names = '''        var white_name := "TheHezzer" if local_user_team == "white" and slot + 1 == local_user_slot else "Bot_%d" % (slot + 1)
        var black_name := "TheHezzer" if local_user_team == "black" and slot + 1 == local_user_slot else "Bot_%d" % (slot + 8)
'''
if old_names not in s:
    raise SystemExit("Missing local roster name block")
s = s.replace(old_names, new_names, 1)
s = s.replace('''        local_bot_roster.append({"name": white_name, "team": "white", "slot": slot, "role": role, "bot": white_name != "TheHezzer"})
        local_bot_roster.append({"name": black_name, "team": "black", "slot": slot, "role": role, "bot": true})
''','''        local_bot_roster.append({"name": white_name, "team": "white", "slot": slot, "role": role, "bot": white_name != "TheHezzer"})
        local_bot_roster.append({"name": black_name, "team": "black", "slot": slot, "role": role, "bot": black_name != "TheHezzer"})
''',1)

# Do not overwrite the random color after the local queue completes.
s = s.replace('''    local_user_team = "white"
    _start_game(selected_mode)
    active_teammate = local_user_slot
    team_next_player["white"] = (local_user_slot % CLASSIC_TEAM_SIZE) + 1
''','''    _start_game(selected_mode)
    active_teammate = local_user_slot
    team_next_player["white"] = (local_user_slot % CLASSIC_TEAM_SIZE) + 1
    team_next_player["black"] = local_user_slot
''',1)

# If the test user was assigned black, let the white bot make the opening move.
launch_anchor = '''    _refresh_team_turn_label()
    _update_turn_highlights()
    status_label.text = "ТЫ ИГРАЕШЬ ЗА БЕЛЫХ. Твои фигуры отмечены голубыми кольцами."
'''
if launch_anchor not in s:
    raise SystemExit("Missing local match launch status")
s = s.replace(launch_anchor, '''    _refresh_team_turn_label()
    _update_turn_highlights()
    status_label.text = "ТЫ ИГРАЕШЬ ЗА " + ("БЕЛЫХ" if local_user_team == "white" else "ЧЁРНЫХ") + ". Цвет выбран случайно."
    if current_team != local_user_team:
        _schedule_local_bot_turn()
''',1)

# New single-player manual chess mode.
if "func _developer_test_self_play() -> void:" not in s:
    anchor = "func _developer_test_logout() -> void:"
    if anchor not in s:
        raise SystemExit("Missing admin logout insertion point")
    fn = '''func _developer_test_self_play() -> void:
    if not developer_mode:
        return
    local_self_play_active = true
    local_bot_test_active = false
    local_offline_mode_active = false
    local_bot_roster.clear()
    local_user_team = "white"
    local_user_slot = 1
    selected_mode = "Стандартные шахматы"
    if developer_test_menu:
        developer_test_menu.visible = false
    if menu_panel:
        menu_panel.visible = false
    if online_panel:
        online_panel.visible = false
    online_active = false
    online_match_id = ""
    _start_game(selected_mode)
    local_ready_active = false
    local_opening_vote_active = false
    local_self_play_active = true
    active_teammate = 1
    team_next_player = {"white": 1, "black": 1}
    if opening_vote_panel:
        opening_vote_panel.visible = false
    if player_clock_label:
        player_clock_label.visible = false
    if team_clock_label:
        team_clock_label.text = "ТЕСТ С САМИМ СОБОЙ • ХОД БЕЛЫХ"
    _refresh_team_turn_label()
    _update_turn_highlights()
    status_label.text = "РЕЖИМ ТЕСТА: ТЫ УПРАВЛЯЕШЬ БЕЛЫМИ И ЧЁРНЫМИ. После каждого хода выбирай фигуру стороны, чей сейчас ход. Шах и мат проверяются автоматически."

'''
    s = s.replace(anchor, fn + anchor, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v76: randomized local player color and added manual self-play test mode.")
