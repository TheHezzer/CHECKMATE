from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

def replace_func(name, next_name, body):
    global s
    start = s.index("func " + name + "(")
    end = s.index("func " + next_name + "(", start)
    s = s[:start] + body.rstrip() + "\n\n" + s[end:]

# Lower the central model in its viewport and make the camera look down more clearly.
rep('''    preview_container.anchor_left = 0.285
    preview_container.anchor_top = 0.245
    preview_container.anchor_right = 0.715
    preview_container.anchor_bottom = 0.775''','''    preview_container.anchor_left = 0.285
    preview_container.anchor_top = 0.265
    preview_container.anchor_right = 0.715
    preview_container.anchor_bottom = 0.805''', "preview viewport lower")
rep('''    preview_camera.position = Vector3(0, 1.25, 5.45)''','''    preview_camera.position = Vector3(0, 1.72, 5.45)''', "camera elevated")
rep('''    preview_camera.look_at(Vector3(0, 1.05, 0), Vector3.UP)''','''    preview_camera.look_at(Vector3(0, 0.95, 0), Vector3.UP)''', "camera target")
rep('''    preview_pawn.position.y = 0.30
    preview_pawn.position.z = 0.0''','''    preview_pawn.position.y = 0.16
    preview_pawn.position.z = 0.0''', "model lowered")

# Never display the text label underneath the central collectible, regardless of selected piece.
shelf_body = '''func _refresh_main_piece_shelf() -> void:
    for i in range(main_piece_buttons.size()):
        var name: String = PIECES[i]
        var shade := Color(0.88, 0.86, 0.80) if i == selected_piece else Color(0.68, 0.67, 0.63)
        main_piece_buttons[i].add_theme_color_override("font_color", shade)
        main_piece_buttons[i].tooltip_text = name
    var center_title := menu_panel.find_child("PieceName", true, false) as Label
    if center_title:
        center_title.visible = false
    var center_hint := menu_panel.find_child("PieceLockHint", true, false) as Label
    if center_hint:
        center_hint.visible = false
    _hide_center_piece_caption(ui)
'''
replace_func("_refresh_main_piece_shelf", "_build_onboarding_screen", shelf_body)

# Re-space left feature cards. Wider cards and controlled font sizes prevent wrapped headings colliding with descriptions.
rep('''var tasks := _panel(menu_panel, 0.015, 0.235, 0.205, 0.375)''','''var tasks := _panel(menu_panel, 0.015, 0.235, 0.235, 0.395)''', "daily card width")
rep('''var pass_panel := _panel(menu_panel, 0.015, 0.405, 0.205, 0.545)''','''var pass_panel := _panel(menu_panel, 0.015, 0.415, 0.235, 0.575)''', "pass card width")
rep('''var event_panel := _panel(menu_panel, 0.015, 0.575, 0.205, 0.735)''','''var event_panel := _panel(menu_panel, 0.015, 0.595, 0.235, 0.785)''', "event card width")
for old, new, label in [
('''Vector2(60, 8), Vector2(245, 34), 7, PALE_GOLD''','''Vector2(58, 7), Vector2(285, 34), 7, PALE_GOLD''',"daily title bounds"),
('''Vector2(60, 43), Vector2(245, 42), 4, Color(0.88, 0.82, 0.73)''','''Vector2(58, 43), Vector2(285, 48), 4, Color(0.88, 0.82, 0.73)''',"daily description bounds"),
('''Vector2(60, 8), Vector2(245, 34), 7, PALE_GOLD''','''Vector2(58, 7), Vector2(285, 34), 7, PALE_GOLD''',"pass title bounds"),
('''Vector2(60, 43), Vector2(245, 42), 4, Color(0.88, 0.82, 0.73)''','''Vector2(58, 43), Vector2(285, 48), 4, Color(0.88, 0.82, 0.73)''',"pass description bounds"),
('''Vector2(60, 8), Vector2(245, 34), 7, PALE_GOLD''','''Vector2(58, 7), Vector2(285, 34), 7, PALE_GOLD''',"event title bounds"),
('''Vector2(60, 40), Vector2(245, 48), 4, Color(0.88, 0.82, 0.73)''','''Vector2(58, 42), Vector2(285, 52), 4, Color(0.88, 0.82, 0.73)''',"event description bounds"),
]:
    if old in s:
        s = s.replace(old, new, 1)
# Assign readable sizes that fit the widened cards.
for old, new in [
('''task_title.add_theme_font_size_override("font_size", 20)''','''task_title.add_theme_font_size_override("font_size", 23)'''),
('''task_desc.add_theme_font_size_override("font_size", 16)''','''task_desc.add_theme_font_size_override("font_size", 20)'''),
('''pass_title.add_theme_font_size_override("font_size", 20)''','''pass_title.add_theme_font_size_override("font_size", 23)'''),
('''pass_desc.add_theme_font_size_override("font_size", 16)''','''pass_desc.add_theme_font_size_override("font_size", 20)'''),
('''event_title.add_theme_font_size_override("font_size", 20)''','''event_title.add_theme_font_size_override("font_size", 23)'''),
('''event_desc.add_theme_font_size_override("font_size", 16)''','''event_desc.add_theme_font_size_override("font_size", 20)'''),
]:
    rep(old, new, old)

# Centered account form: use one consistent vertical grid, with non-overlapping input, action, status and guest rows.
account_body = '''func _build_account_panel() -> void:
    account_panel = Control.new()
    account_panel.name = "AccountDialog"
    account_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    account_panel.visible = false
    ui.add_child(account_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.0, 0.0, 0.0, 0.90)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    account_panel.add_child(shade)

    var frame := _panel(account_panel, 0.17, 0.10, 0.83, 0.90)

    var title := Label.new()
    title.text = "ДОБРО ПОЖАЛОВАТЬ"
    title.anchor_left = 0.05
    title.anchor_right = 0.95
    title.anchor_top = 0.035
    title.anchor_bottom = 0.14
    title.offset_left = 0
    title.offset_right = 0
    title.offset_top = 0
    title.offset_bottom = 0
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    title.add_theme_font_override("font", UI_FONT)
    title.add_theme_font_size_override("font_size", 30)
    title.add_theme_color_override("font_color", PALE_GOLD)
    frame.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "Войди или создай аккаунт, чтобы сохранять прогресс"
    subtitle.anchor_left = 0.08
    subtitle.anchor_right = 0.92
    subtitle.anchor_top = 0.145
    subtitle.anchor_bottom = 0.215
    subtitle.offset_left = 0
    subtitle.offset_right = 0
    subtitle.offset_top = 0
    subtitle.offset_bottom = 0
    subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    subtitle.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    subtitle.add_theme_font_override("font", UI_FONT)
    subtitle.add_theme_font_size_override("font_size", 17)
    subtitle.add_theme_color_override("font_color", Color(0.84, 0.82, 0.77))
    frame.add_child(subtitle)

    account_username_input = LineEdit.new()
    account_username_input.anchor_left = 0.15
    account_username_input.anchor_right = 0.85
    account_username_input.anchor_top = 0.255
    account_username_input.anchor_bottom = 0.365
    account_username_input.offset_left = 0
    account_username_input.offset_right = 0
    account_username_input.offset_top = 0
    account_username_input.offset_bottom = 0
    account_username_input.placeholder_text = "ЛОГИН  •  3–20 СИМВОЛОВ"
    account_username_input.add_theme_font_override("font", UI_FONT)
    account_username_input.add_theme_font_size_override("font_size", 25)
    account_username_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
    frame.add_child(account_username_input)

    account_password_input = LineEdit.new()
    account_password_input.anchor_left = 0.15
    account_password_input.anchor_right = 0.85
    account_password_input.anchor_top = 0.405
    account_password_input.anchor_bottom = 0.515
    account_password_input.offset_left = 0
    account_password_input.offset_right = 0
    account_password_input.offset_top = 0
    account_password_input.offset_bottom = 0
    account_password_input.placeholder_text = "ПАРОЛЬ  •  ОТ 8 СИМВОЛОВ"
    account_password_input.secret = true
    account_password_input.add_theme_font_override("font", UI_FONT)
    account_password_input.add_theme_font_size_override("font_size", 25)
    account_password_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
    frame.add_child(account_password_input)

    var login := _ornate_button(frame, "ВОЙТИ ОНЛАЙН", 0.045, 0.565, 0.345, 0.685, 14, "party")
    login.pressed.connect(_account_login)
    var offline := _ornate_button(frame, "ОФЛАЙН • БОТЫ", 0.355, 0.565, 0.645, 0.685, 14, "nav")
    offline.pressed.connect(_account_offline_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.655, 0.565, 0.955, 0.685, 14, "nav")
    register.pressed.connect(_account_register)

    account_status_label = Label.new()
    account_status_label.anchor_left = 0.06
    account_status_label.anchor_right = 0.94
    account_status_label.anchor_top = 0.705
    account_status_label.anchor_bottom = 0.79
    account_status_label.offset_left = 0
    account_status_label.offset_right = 0
    account_status_label.offset_top = 0
    account_status_label.offset_bottom = 0
    account_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    account_status_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    account_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    account_status_label.add_theme_font_override("font", UI_FONT)
    account_status_label.add_theme_font_size_override("font_size", 16)
    account_status_label.add_theme_color_override("font_color", PALE_GOLD)
    frame.add_child(account_status_label)

    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.20, 0.815, 0.80, 0.92, 14, "nav")
    guest.pressed.connect(_account_guest)
    var close := _ornate_button(frame, "×", 0.91, 0.015, 0.975, 0.11, 18, "nav")
    close.pressed.connect(_close_account_panel)
    _refresh_profile_card()
'''
replace_func("_build_account_panel", "_open_account_panel", account_body)

# Full-width mode description block with a reserved heading row and a large text area below it.
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

    var frame := _panel(mode_selection_panel, 0.035, 0.045, 0.965, 0.955)
    var heading := Label.new()
    heading.text = "ВЫБОР ИГРОВОГО РЕЖИМА"
    heading.position = Vector2(24, 16)
    heading.size = Vector2(760, 42)
    heading.add_theme_font_override("font", UI_FONT)
    heading.add_theme_font_size_override("font_size", 29)
    heading.add_theme_color_override("font_color", PALE_GOLD)
    frame.add_child(heading)

    var subheading := Label.new()
    subheading.text = "Выбери формат шахматной партии"
    subheading.position = Vector2(26, 58)
    subheading.size = Vector2(650, 28)
    subheading.add_theme_font_override("font", UI_FONT)
    subheading.add_theme_font_size_override("font_size", 19)
    subheading.add_theme_color_override("font_color", Color(0.78, 0.72, 0.63))
    frame.add_child(subheading)

    var back := _ornate_button(frame, "← НАЗАД", 0.80, 0.025, 0.97, 0.125, 13, "nav")
    back.pressed.connect(_close_mode_selection)

    var names := ["Классика", "Командное голосование", "Стандартные шахматы"]
    mode_choice_buttons.clear()
    for i in range(names.size()):
        var left := 0.035 + float(i) * 0.315
        var card := _ornate_button(frame, "%02d  |  %s" % [i + 1, names[i]], left, 0.205, left + 0.285, 0.505, 16, "card")
        card.pressed.connect(_select_mode_card.bind(names[i]))
        mode_choice_buttons.append(card)

    var details := _panel(frame, 0.025, 0.545, 0.975, 0.965)
    var details_title := Label.new()
    details_title.text = "КАК ПРОХОДИТ РЕЖИМ"
    details_title.position = Vector2(22, 12)
    details_title.size = Vector2(800, 34)
    details_title.add_theme_font_override("font", UI_FONT)
    details_title.add_theme_font_size_override("font_size", 25)
    details_title.add_theme_color_override("font_color", PALE_GOLD)
    details.add_child(details_title)

    mode_description_label = Label.new()
    mode_description_label.anchor_left = 0.02
    mode_description_label.anchor_right = 0.98
    mode_description_label.anchor_top = 0.19
    mode_description_label.anchor_bottom = 0.97
    mode_description_label.offset_left = 12
    mode_description_label.offset_right = -12
    mode_description_label.offset_top = 0
    mode_description_label.offset_bottom = -4
    mode_description_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    mode_description_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
    mode_description_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    mode_description_label.add_theme_font_override("font", UI_FONT)
    mode_description_label.add_theme_font_size_override("font_size", 19)
    mode_description_label.add_theme_color_override("font_color", Color(0.90, 0.86, 0.79))
    details.add_child(mode_description_label)
    _refresh_mode_selection()
'''
replace_func("_build_mode_selection_screen", "_select_mode_card", mode_body)

refresh_body = '''func _refresh_mode_selection() -> void:
    var names := ["Классика", "Командное голосование", "Стандартные шахматы"]
    var captions := [
        "Командная партия: каждый участник отвечает за свои фигуры и может передать очередь союзнику. Команда играет против другой команды.",
        "Игрок предлагает ход, команда обсуждает его 5 секунд и голосует 15 секунд. Если время вышло, побеждает вариант с большим числом голосов. За верное командное решение предусмотрен бонус.",
        "Обычные шахматы 1 на 1. Каждый игрок управляет всеми 16 фигурами своей стороны. Стандартные правила, шах и мат. Можно выбирать оформление фигур и доски. В офлайн-режиме против тебя играет бот."
    ]
    for i in range(min(mode_choice_buttons.size(), names.size())):
        mode_choice_buttons[i].text = ("◆  " if selected_mode == names[i] else "") + "%02d  |  %s" % [i + 1, names[i]]
        mode_choice_buttons[i].add_theme_font_size_override("font_size", 18)
    if mode_description_label:
        var index := names.find(selected_mode)
        if index < 0:
            index = 0
            selected_mode = names[0]
        mode_description_label.text = captions[index]
'''
replace_func("_refresh_mode_selection", "_continue_to_preparation", refresh_body)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v65: lowered center model, removed center labels, resized left cards, centered account form, expanded mode description.")
