from pathlib import Path

p = Path(__file__).resolve().parents[1] / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("CHECKMATE v114 missing anchor: " + label)
    s = s.replace(old, new, 1)

rep('''    var intro := _add_label(frame, "Заходи каждый день подряд и забирай всё более ценные награды. Пропуск дня сбрасывает серию.", Vector2(22, 70), Vector2(850, 48), 15, Color(0.84,0.81,0.74))
    intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    login_streak_status_label = _add_label(frame, "", Vector2(22, 128), Vector2(850, 34), 17, Color(0.78,0.88,0.72))
''','''    var intro := _add_label(frame, "Заходи каждый день подряд и забирай всё более ценные награды. Пропуск дня сбрасывает серию.", Vector2(22, 66), Vector2(1120, 56), 13, Color(0.84,0.81,0.74))
    intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    login_streak_status_label = _add_label(frame, "", Vector2(22, 132), Vector2(1050, 30), 15, Color(0.78,0.88,0.72))
''', "login streak header spacing")
rep('''        var y1 := 0.235 + float(row) * 0.245
        var y2 := y1 + 0.205
''','''        var y1 := 0.255 + float(row) * 0.225
        var y2 := y1 + 0.19
''', "login streak card grid spacing")
rep('''        var day_title := _add_label(card, "ДЕНЬ " + str(i + 1), Vector2(8, 8), Vector2(180, 30), 15, PALE_GOLD)
        day_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
''','''        var day_title := _add_label(card, "ДЕНЬ " + str(i + 1), Vector2(8, 7), Vector2(250, 27), 13, PALE_GOLD)
        day_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
''', "login streak day title")
rep('''        var reward_label := _add_label(card, reward_text, Vector2(8, 44), Vector2(180, 48), 15, Color(0.90,0.86,0.78))
        reward_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        reward_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
        var state_label := _add_label(card, "ОЖИДАНИЕ", Vector2(8, 98), Vector2(180, 26), 12, Color(0.70,0.68,0.62))
        state_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
''','''        var reward_label := _add_label(card, reward_text, Vector2(8, 37), Vector2(250, 54), 13, Color(0.90,0.86,0.78))
        reward_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        reward_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
        reward_label.autowrap_mode = TextServer.AUTOWRAP_OFF
        var state_label := _add_label(card, "ОЖИДАНИЕ", Vector2(8, 99), Vector2(250, 23), 10, Color(0.70,0.68,0.62))
        state_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
''', "login streak reward and state label spacing")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v114: repaired login streak header and reward-card text spacing")
