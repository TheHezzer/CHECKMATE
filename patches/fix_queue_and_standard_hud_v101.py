from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v101 anchor: " + label)
    s = s.replace(old, new, 1)

# Matchmaking queue: fit all headings and keep roster/status inside their panels.
rep('queue_rating_label = _add_label(frame, "ВАШ РЕЙТИНГ: %d  •  %s" % [competitive_rating, _rating_division()], Vector2(22, 92), Vector2(420, 30), 17, PALE_GOLD)',
    'queue_rating_label = _add_label(frame, "ВАШ РЕЙТИНГ: %d  •  %s" % [competitive_rating, _rating_division()], Vector2(22, 92), Vector2(390, 28), 13, PALE_GOLD)',
    "queue rating label")
rep('queue_timer_label = _add_label(frame, "ВРЕМЯ ПОИСКА  00:00", Vector2(500, 92), Vector2(300, 30), 19, PALE_GOLD)',
    'queue_timer_label = _add_label(frame, "ПОИСК: 00:00", Vector2(500, 92), Vector2(360, 28), 13, PALE_GOLD)',
    "queue timer label")
rep('var server_url_label := _add_label(frame, "АДРЕС ОНЛАЙН-СЕРВЕРА", Vector2(22, 132), Vector2(260, 20), 11, PALE_GOLD)',
    'var server_url_label := _add_label(frame, "АДРЕС ОНЛАЙН-СЕРВЕРА", Vector2(22, 128), Vector2(300, 20), 10, PALE_GOLD)',
    "server label")
rep('server_url_input.position = Vector2(22, 154)\n    server_url_input.size = Vector2(540, 34)',
    'server_url_input.position = Vector2(22, 150)\n    server_url_input.size = Vector2(700, 32)',
    "server address input")
rep('var white_panel := _panel(frame, 0.025, 0.235, 0.485, 0.835)\n    var black_panel := _panel(frame, 0.515, 0.235, 0.975, 0.835)',
    'var white_panel := _panel(frame, 0.025, 0.255, 0.485, 0.825)\n    var black_panel := _panel(frame, 0.515, 0.255, 0.975, 0.825)',
    "team panels")
rep('queue_white_roster_label = _add_label(white_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 430), 15, Color(0.88, 0.85, 0.78))',
    'queue_white_roster_label = _add_label(white_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 245), 11, Color(0.88, 0.85, 0.78))',
    "white roster")
rep('queue_black_roster_label = _add_label(black_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 430), 15, Color(0.88, 0.85, 0.78))',
    'queue_black_roster_label = _add_label(black_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 245), 11, Color(0.88, 0.85, 0.78))',
    "black roster")
rep('queue_status_label = _add_label(frame, "Подключаемся к рейтинговой очереди…", Vector2(24, 520), Vector2(650, 42), 15, PALE_GOLD)',
    'queue_status_label = _add_label(frame, "Подключаемся к рейтинговой очереди…", Vector2(24, 448), Vector2(620, 30), 11, PALE_GOLD)',
    "queue status")
# Standard chess: compact, single-line instruction and clearly separated turn/timer HUD.
rep('team_turn_label.offset_top = 0\n    team_turn_label.offset_bottom = 34\n    team_turn_label.add_theme_font_size_override("font_size", 16)',
    'team_turn_label.offset_top = 0\n    team_turn_label.offset_bottom = 30\n    team_turn_label.add_theme_font_size_override("font_size", 13)',
    "turn label font")
rep('game_hint_label.anchor_top = 0.085\n    game_hint_label.anchor_bottom = 0.085\n    game_hint_label.offset_top = 0\n    game_hint_label.offset_bottom = 28\n    game_hint_label.offset_left = -340\n    game_hint_label.offset_right = 340',
    'game_hint_label.anchor_top = 0.095\n    game_hint_label.anchor_bottom = 0.095\n    game_hint_label.offset_top = 0\n    game_hint_label.offset_bottom = 24\n    game_hint_label.offset_left = -470\n    game_hint_label.offset_right = 470',
    "hint label bounds")
rep('game_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER',
    'game_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER\n    game_hint_label.autowrap_mode = TextServer.AUTOWRAP_OFF\n    game_hint_label.add_theme_font_size_override("font_size", 11)',
    "hint single line")
rep('team_clock_label.anchor_top = 0.135\n    team_clock_label.anchor_bottom = 0.135',
    'team_clock_label.anchor_top = 0.155\n    team_clock_label.anchor_bottom = 0.155',
    "clock vertical position")
rep('team_clock_label.offset_top = 0\n    team_clock_label.offset_bottom = 32',
    'team_clock_label.offset_top = 0\n    team_clock_label.offset_bottom = 28',
    "clock bounds")
rep('team_clock_label.offset_left = -310\n    team_clock_label.offset_right = 310',
    'team_clock_label.offset_left = -360\n    team_clock_label.offset_right = 360',
    "clock width")
rep('team_clock_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER',
    'team_clock_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER\n    team_clock_label.add_theme_font_size_override("font_size", 12)',
    "clock font")
rep('game_hint_label.text = "СТАНДАРТНЫЕ ШАХМАТЫ • ВЫБИРАЙ ФИГУРУ И ДОПУСТИМУЮ КЛЕТКУ"',
    'game_hint_label.text = "СТАНДАРТНЫЕ ШАХМАТЫ • ВЫБЕРИ ФИГУРУ И КЛЕТКУ ХОДА"',
    "standard mode hint")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v101: matchmaking queue labels and roster fit; Standard Chess HUD separated.")
