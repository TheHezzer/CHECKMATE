from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v102 anchor: " + label)
    s = s.replace(old, new, 1)

# Matchmaking queue: _add_label adds +17 px globally, so explicitly set real font sizes.
rep('    _add_label(frame, "ПОИСК СОПЕРНИКОВ", Vector2(20, 10), Vector2(620, 42), 28, PALE_GOLD)',
    '    var queue_title := _add_label(frame, "ПОИСК СОПЕРНИКОВ", Vector2(20, 10), Vector2(620, 42), 28, PALE_GOLD)\n    queue_title.add_theme_font_size_override("font_size", 28)',
    "queue title font")
rep('    _add_label(frame, "КЛАССИКА  •  8 НА 8  •  ПОДБОР ПО РЕЙТИНГУ", Vector2(22, 52), Vector2(850, 28), 14, Color(0.82, 0.76, 0.66))',
    '    var queue_subtitle := _add_label(frame, "КЛАССИКА  •  8 НА 8  •  ПОДБОР ПО РЕЙТИНГУ", Vector2(22, 54), Vector2(850, 26), 14, Color(0.82, 0.76, 0.66))\n    queue_subtitle.add_theme_font_size_override("font_size", 17)',
    "queue subtitle")
rep('    queue_rating_label = _add_label(frame, "ВАШ РЕЙТИНГ: %d  •  %s" % [competitive_rating, _rating_division()], Vector2(22, 92), Vector2(390, 28), 13, PALE_GOLD)',
    '    queue_rating_label = _add_label(frame, "ВАШ РЕЙТИНГ: %d  •  %s" % [competitive_rating, _rating_division()], Vector2(22, 96), Vector2(470, 28), 13, PALE_GOLD)\n    queue_rating_label.add_theme_font_size_override("font_size", 17)',
    "queue rating")
rep('    queue_timer_label = _add_label(frame, "ПОИСК: 00:00", Vector2(500, 92), Vector2(360, 28), 13, PALE_GOLD)',
    '    queue_timer_label = _add_label(frame, "ПОИСК: 00:00", Vector2(1060, 96), Vector2(340, 28), 13, PALE_GOLD)\n    queue_timer_label.add_theme_font_size_override("font_size", 17)',
    "queue timer")
rep('    var server_url_label := _add_label(frame, "АДРЕС ОНЛАЙН-СЕРВЕРА", Vector2(22, 128), Vector2(300, 20), 10, PALE_GOLD)',
    '    var server_url_label := _add_label(frame, "АДРЕС ОНЛАЙН-СЕРВЕРА", Vector2(22, 132), Vector2(320, 22), 10, PALE_GOLD)\n    server_url_label.add_theme_font_size_override("font_size", 14)',
    "server label font")
rep('    server_url_input.position = Vector2(22, 150)\n    server_url_input.size = Vector2(700, 32)',
    '    server_url_input.position = Vector2(22, 158)\n    server_url_input.size = Vector2(700, 32)',
    "server input position")
rep('    _add_label(white_panel, "БЕЛАЯ КОМАНДА", Vector2(12, 8), Vector2(330, 30), 18, PALE_GOLD)\n    _add_label(black_panel, "ЧЁРНАЯ КОМАНДА", Vector2(12, 8), Vector2(330, 30), 18, PALE_GOLD)',
    '    var white_title := _add_label(white_panel, "БЕЛАЯ КОМАНДА", Vector2(12, 8), Vector2(360, 30), 18, PALE_GOLD)\n    var black_title := _add_label(black_panel, "ЧЁРНАЯ КОМАНДА", Vector2(12, 8), Vector2(360, 30), 18, PALE_GOLD)\n    white_title.add_theme_font_size_override("font_size", 21)\n    black_title.add_theme_font_size_override("font_size", 21)',
    "team titles")
rep('    queue_white_roster_label = _add_label(white_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 245), 11, Color(0.88, 0.85, 0.78))\n    queue_black_roster_label = _add_label(black_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 245), 11, Color(0.88, 0.85, 0.78))',
    '    queue_white_roster_label = _add_label(white_panel, "Ожидаем игроков…", Vector2(14, 48), Vector2(350, 280), 11, Color(0.88, 0.85, 0.78))\n    queue_black_roster_label = _add_label(black_panel, "Ожидаем игроков…", Vector2(14, 48), Vector2(350, 280), 11, Color(0.88, 0.85, 0.78))\n    queue_white_roster_label.add_theme_font_size_override("font_size", 15)\n    queue_black_roster_label.add_theme_font_size_override("font_size", 15)',
    "roster fonts")
rep('    var white_panel := _panel(frame, 0.025, 0.255, 0.485, 0.825)\n    var black_panel := _panel(frame, 0.515, 0.255, 0.975, 0.825)',
    '    var white_panel := _panel(frame, 0.025, 0.285, 0.485, 0.805)\n    var black_panel := _panel(frame, 0.515, 0.285, 0.975, 0.805)',
    "roster panel bounds")
rep('    queue_status_label = _add_label(frame, "Подключаемся к рейтинговой очереди…", Vector2(24, 448), Vector2(620, 30), 11, PALE_GOLD)',
    '    queue_status_label = _add_label(frame, "Подключаемся к рейтинговой очереди…", Vector2(24, 820), Vector2(620, 28), 11, PALE_GOLD)\n    queue_status_label.add_theme_font_size_override("font_size", 15)',
    "queue status placement")

# Standard chess: set the mode BEFORE pieces are created; otherwise the board is populated as team chess.
rep('    if local_clock_timer:\n        local_clock_timer.start()',
    '    standard_chess_mode_active = mode_name == "Стандартные шахматы"\n    if local_clock_timer:\n        local_clock_timer.start()',
    "standard mode before piece construction")
rep('    standard_chess_mode_active = mode_name == "Стандартные шахматы"\n    var team_chat := game_panel.find_child("TeamChatPanel", true, false)',
    '    var team_chat := game_panel.find_child("TeamChatPanel", true, false)',
    "remove late standard mode assignment")
rep('    if team_chat:\n        team_chat.visible = not standard_chess_mode_active',
    '    if team_chat:\n        team_chat.visible = not standard_chess_mode_active\n    if team_chat_label:\n        team_chat_label.visible = not standard_chess_mode_active\n    if team_chat_input:\n        team_chat_input.visible = not standard_chess_mode_active\n    for chat_button in game_panel.find_children("*", "Button", true, false):\n        if chat_button is Button and str(chat_button.text).contains("ОТПРАВИТЬ"):\n            chat_button.visible = not standard_chess_mode_active',
    "hide standalone team chat controls in standard chess")

# Compact match header and keep the turn label away from the large title panel.
rep('    _add_label(header, "ПАРТИЯ  •  " + selected_mode, Vector2(12, 8), Vector2(480, 28), 18, PALE_GOLD)',
    '    var game_header_label := _add_label(header, "ПАРТИЯ  •  " + selected_mode, Vector2(12, 8), Vector2(480, 28), 18, PALE_GOLD)\n    game_header_label.add_theme_font_size_override("font_size", 23)',
    "game header font")
rep('    team_turn_label.anchor_left = 0.5\n    team_turn_label.anchor_right = 0.5',
    '    team_turn_label.anchor_left = 0.46\n    team_turn_label.anchor_right = 0.80',
    "turn label anchor")
rep('    team_turn_label.offset_left = -210\n    team_turn_label.offset_right = 210',
    '    team_turn_label.offset_left = 0\n    team_turn_label.offset_right = 0',
    "turn label bounds")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v102: fixed queue typography/overlap, standard chess piece initialization and hidden team chat; compacted match HUD.")
