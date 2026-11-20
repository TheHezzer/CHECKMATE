from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def replace_func(name, next_name, body):
    global s
    start = s.index("func " + name + "(")
    end = s.index("func " + next_name + "(", start)
    s = s[:start] + body.rstrip() + "\n\n" + s[end:]

# Third mode is now standard one-versus-one chess, not multi-piece team play.
mode_body = '''func _build_mode_selection_screen() -> void:
    mode_selection_panel = Control.new()
    mode_selection_panel.name = "ModeSelectionScreen"
    mode_selection_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mode_selection_panel.visible = false
    ui.add_child(mode_selection_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.012, 0.010, 0.009, 0.97)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    mode_selection_panel.add_child(shade)

    var frame := _panel(mode_selection_panel, 0.045, 0.055, 0.955, 0.945)
    _add_label(frame, "ВЫБОР ИГРОВОГО РЕЖИМА", Vector2(24, 18), Vector2(700, 42), 23, PALE_GOLD)
    _add_label(frame, "Выбери формат шахматной партии", Vector2(26, 62), Vector2(650, 30), 14, Color(0.78, 0.72, 0.63))
    var back := _ornate_button(frame, "← НАЗАД", 0.80, 0.035, 0.97, 0.135, 14, "nav")
    back.pressed.connect(_close_mode_selection)

    var names := ["Классика", "Командное голосование", "Стандартные шахматы"]
    var descriptions := [
        "Командная партия: каждый участник отвечает за свои фигуры и может передать очередь союзнику. Команда играет против другой команды.",
        "Командная партия с обсуждением: игрок предлагает ход, союзники голосуют, а за правильное решение команда получает бонус к наградам.",
        "Обычные шахматы 1 на 1. Каждый игрок управляет всеми 16 фигурами своей стороны. Стандартные правила, шах и мат, выбор оформления фигур и доски. В офлайн-режиме против тебя играет бот."
    ]
    mode_choice_buttons.clear()
    for i in range(names.size()):
        var left := 0.035 + float(i) * 0.315
        var card := _ornate_button(frame, "%02d  |  %s" % [i + 1, names[i]], left, 0.235, left + 0.285, 0.535, 17, "card")
        card.pressed.connect(_select_mode_card.bind(names[i]))
        mode_choice_buttons.append(card)

    var details := _panel(frame, 0.035, 0.585, 0.965, 0.945)
    _add_label(details, "КАК ПРОХОДИТ РЕЖИМ", Vector2(20, 12), Vector2(900, 32), 18, PALE_GOLD)
    mode_description_label = Label.new()
    mode_description_label.anchor_left = 0.025
    mode_description_label.anchor_right = 0.975
    mode_description_label.anchor_top = 0.22
    mode_description_label.anchor_bottom = 0.94
    mode_description_label.offset_left = 0
    mode_description_label.offset_right = 0
    mode_description_label.offset_top = 0
    mode_description_label.offset_bottom = 0
    mode_description_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    mode_description_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
    mode_description_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    mode_description_label.add_theme_font_size_override("font_size", 18)
    mode_description_label.add_theme_color_override("font_color", Color(0.88, 0.84, 0.77))
    details.add_child(mode_description_label)
    _refresh_mode_selection()
'''
replace_func("_build_mode_selection_screen", "_refresh_mode_selection", mode_body)

refresh_body = '''func _refresh_mode_selection() -> void:
    var names := ["Классика", "Командное голосование", "Стандартные шахматы"]
    var captions := [
        "Командная партия: каждый участник отвечает за свои фигуры и может передать очередь союзнику. Команда играет против другой команды.",
        "Командная партия с обсуждением: игрок предлагает ход, союзники голосуют, а за правильное решение команда получает бонус к наградам.",
        "Обычные шахматы 1 на 1. Каждый игрок управляет всеми 16 фигурами своей стороны. Стандартные правила, шах и мат, выбор оформления фигур и доски. В офлайн-режиме против тебя играет бот."
    ]
    for i in range(min(mode_choice_buttons.size(), names.size())):
        mode_choice_buttons[i].text = ("◆  " if selected_mode == names[i] else "") + "%02d  |  %s" % [i + 1, names[i]]
        mode_choice_buttons[i].add_theme_font_size_override("font_size", 19)
    if mode_description_label:
        var index := names.find(selected_mode)
        if index < 0:
            index = 0
            selected_mode = names[0]
        mode_description_label.text = captions[index]
'''
replace_func("_refresh_mode_selection", "_continue_to_preparation", refresh_body)

# Mark standard chess as a separate local play style before the board is created.
if "var standard_chess_mode_active := false" not in s:
    s = s.replace("var local_offline_mode_active := false\n", "var local_offline_mode_active := false\nvar standard_chess_mode_active := false\n", 1)

# In standard chess all white pieces belong to the human and all black pieces to the bot.
anchor = 'root.set_meta("owner_slot", col + 1)'
if anchor not in s:
    raise SystemExit("owner_slot metadata anchor missing")
s = s.replace(anchor, 'root.set_meta("owner_slot", 1 if standard_chess_mode_active else col + 1)', 1)

# Standard mode accepts normal board moves; the team-only modes keep their ownership restrictions.
s = s.replace('''    if selected_mode != "Классика":
        status_label.text = "Этот режим пока в разработке. Сейчас тестируем механику классической партии."
        return
''', '''    if selected_mode != "Классика" and not standard_chess_mode_active:
        status_label.text = "Для этого режима пока не подключена доска."
        return
''', 1)

# In standard chess, don't show teammate passing or opening vote, and don't enforce team-member piece ownership.
s = s.replace('''    if (developer_mode or local_bot_test_active) and (current_team != local_user_team or active_teammate != local_user_slot or int(target_piece.get_meta("owner_slot", 0)) != local_user_slot):''', '''    if not standard_chess_mode_active and (developer_mode or local_bot_test_active) and (current_team != local_user_team or active_teammate != local_user_slot or int(target_piece.get_meta("owner_slot", 0)) != local_user_slot):''')
s = s.replace('''        if (developer_mode or local_bot_test_active) and int(target_piece.get_meta("owner_slot", 0)) != local_user_slot:''', '''        if not standard_chess_mode_active and (developer_mode or local_bot_test_active) and int(target_piece.get_meta("owner_slot", 0)) != local_user_slot:''')

# The offline bot roster still fills the team list for team modes; standard chess assigns every side's piece to one player.
s = s.replace('''    local_user_slot = role_slots[randi_range(0, role_slots.size() - 1)] + 1 if not role_slots.is_empty() else randi_range(1, CLASSIC_TEAM_SIZE)
''', '''    local_user_slot = 1 if standard_chess_mode_active else (role_slots[randi_range(0, role_slots.size() - 1)] + 1 if not role_slots.is_empty() else randi_range(1, CLASSIC_TEAM_SIZE))
''', 1)

# Configure 1v1 mode before starting the local board. The human is white; one bot controls all black pieces.
marker = "func _launch_local_bot_match() -> void:"
if marker not in s:
    raise SystemExit("local bot match launch function missing")
helper = '''func _launch_local_bot_match() -> void:'''
s = s.replace(marker, helper, 1)
s = s.replace('''    _start_game(selected_mode)
    local_user_team = "white"
''', '''    standard_chess_mode_active = selected_mode == "Стандартные шахматы"
    local_user_team = "white"
    if standard_chess_mode_active:
        local_user_slot = 1
    _start_game(selected_mode)
    local_user_team = "white"
''', 1)

# For standard chess, the bot controls all black pieces (all tagged slot 1); team modes retain per-player control.
s = s.replace('''        if int(piece.get_meta("owner_slot", 0)) != active_teammate:
            continue
''', '''        if not standard_chess_mode_active and int(piece.get_meta("owner_slot", 0)) != active_teammate:
            continue
''', 1)

# Hide team-only UI for 1v1 and display standard chess labels.
s = s.replace('''    _refresh_team_turn_label()
    if team_clock_label:
''', '''    standard_chess_mode_active = mode_name == "Стандартные шахматы"
    _refresh_team_turn_label()
    if standard_chess_mode_active:
        if player_clock_label:
            player_clock_label.visible = false
        if opening_vote_panel:
            opening_vote_panel.visible = false
        var pass_button := game_panel.find_child("*", true, false)
        for node in game_panel.find_children("*", "Button", true, false):
            if node is Button and (str(node.text).contains("ПЕРЕДАТЬ ХОД") or str(node.text).contains("ЗАВЕРШИТЬ ХОД")):
                node.visible = false
    else:
        if player_clock_label:
            player_clock_label.visible = true
    if team_clock_label:
''', 1)

# Clear standard mode when leaving the board.
s = s.replace('''    local_offline_mode_active = false
    developer_mode = false
''', '''    local_offline_mode_active = false
    standard_chess_mode_active = false
    developer_mode = false
''', 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v64: removed multi-piece mode and added standard 1v1 chess mode with offline bot support.")
