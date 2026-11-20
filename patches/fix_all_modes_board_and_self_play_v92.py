from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v92 anchor: " + label)
    s = s.replace(old, new, 1)

# Board framing is shared by every chess mode: fit the full board and leave room around pieces.
rep("camera.fov = 42.0", "camera.fov = 49.0", "shared board camera zoom")
rep("camera.position = Vector3(0, 11.6, 7.0)", "camera.position = Vector3(0, 14.0, 9.5)", "white-side board framing")
rep("camera.position = Vector3(0, 11.6, -7.0)", "camera.position = Vector3(0, 14.0, -9.5)", "black-side board framing")

# Reduce the oversized pieces and harsh lighting visible in the supplied screenshot.
rep("root.scale = Vector3(1.62, 1.62, 1.62)", "root.scale = Vector3(1.28, 1.28, 1.28)", "piece scale")
rep("env.ambient_light_energy = 1.0", "env.ambient_light_energy = 0.72", "ambient light")
rep("sun.light_energy = 1.35", "sun.light_energy = 0.92", "directional light")

# Separate HUD lines so turn, instructions and test status never overlap the board.
rep('''    team_turn_label.anchor_top = 0.105
    team_turn_label.anchor_bottom = 0.105''', '''    team_turn_label.anchor_top = 0.035
    team_turn_label.anchor_bottom = 0.035
    team_turn_label.offset_top = 0
    team_turn_label.offset_bottom = 32''', "turn HUD lane")
rep('''    game_hint_label.anchor_top = 0.145
    game_hint_label.anchor_bottom = 0.145''', '''    game_hint_label.anchor_top = 0.085
    game_hint_label.anchor_bottom = 0.085
    game_hint_label.offset_top = 0
    game_hint_label.offset_bottom = 28''', "hint HUD lane")
rep('''    team_clock_label.anchor_top = 0.185
    team_clock_label.anchor_bottom = 0.185''', '''    team_clock_label.anchor_top = 0.135
    team_clock_label.anchor_bottom = 0.135
    team_clock_label.offset_top = 0
    team_clock_label.offset_bottom = 26''', "team clock HUD lane")
rep('''    player_clock_label.anchor_top = 0.225
    player_clock_label.anchor_bottom = 0.225''', '''    player_clock_label.anchor_top = 0.18
    player_clock_label.anchor_bottom = 0.18
    player_clock_label.offset_top = 0
    player_clock_label.offset_bottom = 26''', "player clock HUD lane")

# Standard 1v1 and self-play are not team matches: remove the team chat panel from the screen.
rep('''    standard_chess_mode_active = mode_name == "Стандартные шахматы"
    _refresh_team_turn_label()''', '''    standard_chess_mode_active = mode_name == "Стандартные шахматы"
    var team_chat := game_panel.find_child("TeamChatPanel", true, false)
    if team_chat:
        team_chat.visible = not standard_chess_mode_active
    _refresh_team_turn_label()''', "hide team chat in 1v1")

# Replace the self-play launcher with a clean local two-sided chess session.
start = s.find("func _developer_test_self_play() -> void:")
if start < 0:
    raise SystemExit("Missing v92 self-play launcher")
end = s.find("\nfunc _developer_test_logout() -> void:", start)
if end < 0:
    raise SystemExit("Missing function after self-play launcher")
body = '''func _developer_test_self_play() -> void:
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
    # Reassert the test flags after match initialization.
    standard_chess_mode_active = true
    local_self_play_active = true
    local_ready_active = false
    local_opening_vote_active = false
    local_user_team = "white"
    local_user_slot = 1
    active_teammate = 1
    team_next_player = {"white": 1, "black": 1}
    if opening_vote_panel:
        opening_vote_panel.visible = false
    if player_clock_label:
        player_clock_label.visible = false
    if team_clock_label:
        team_clock_label.visible = true
        team_clock_label.text = "ТЕСТ • ТЫ УПРАВЛЯЕШЬ ОБЕИМИ СТОРОНАМИ"
    if game_hint_label:
        game_hint_label.text = "ВЫБИРАЙ ФИГУРУ СТОРОНЫ, ЧЕЙ СЕЙЧАС ХОД • ПОДСВЕТКА ПОКАЖЕТ ДОПУСТИМЫЕ КЛЕТКИ"
    var team_chat := game_panel.find_child("TeamChatPanel", true, false)
    if team_chat:
        team_chat.visible = false
    _refresh_team_turn_label()
    _update_turn_highlights()
    status_label.text = "ТЕСТОВАЯ ПАРТИЯ: ходи белыми и чёрными по очереди. Боты отключены; шах и мат проверяются автоматически."
'''
s = s[:start] + body + s[end:]

p.write_text(s, encoding="utf-8")
print("CHECKMATE v92: shared board framing, softer lighting, smaller pieces, separated HUD and repaired self-play setup.")
