from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def replace_func(name, next_name, body):
    global s
    start = s.index("func " + name + "(")
    end = s.index("func " + next_name + "(", start)
    s = s[:start] + body.rstrip() + "\n\n" + s[end:]

# Remove any standalone chess-piece name caption below the central 3D preview.
hide_caption = '''
func _hide_center_piece_caption(node: Node) -> void:
    for child in node.get_children():
        if child is Label:
            var caption := str(child.text).strip_edges().to_upper()
            if caption in ["ПЕШКА", "КОНЬ", "СЛОН", "ЛАДЬЯ", "ФЕРЗЬ", "КОРОЛЬ"]:
                child.visible = false
        _hide_center_piece_caption(child)
'''
if "func _hide_center_piece_caption(node: Node)" not in s:
    s += "\n" + hide_caption
# Call it after each preview shelf refresh.
needle = "func _refresh_main_piece_shelf() -> void:"
if needle in s:
    i = s.index(needle)
    next_i = s.find("\nfunc ", i + len(needle))
    if next_i < 0: next_i = len(s)
    block = s[i:next_i]
    if "_hide_center_piece_caption(ui)" not in block:
        block = block.rstrip() + "\n    _hide_center_piece_caption(ui)\n"
        s = s[:i] + block + s[next_i:]

# Replace account form with normalized anchors so inputs/buttons are truly centered at every aspect ratio.
account_body = '''func _build_account_panel() -> void:
    account_panel = Control.new()
    account_panel.name = "AccountDialog"
    account_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    account_panel.visible = false
    ui.add_child(account_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.0, 0.0, 0.0, 0.88)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    account_panel.add_child(shade)

    var frame := _panel(account_panel, 0.14, 0.08, 0.86, 0.92)
    var title := Label.new()
    title.text = "ДОБРО ПОЖАЛОВАТЬ"
    title.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    title.anchor_left = 0.05
    title.anchor_right = 0.95
    title.anchor_top = 0.035
    title.anchor_bottom = 0.145
    title.offset_left = 0
    title.offset_right = 0
    title.offset_top = 0
    title.offset_bottom = 0
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 29)
    title.add_theme_color_override("font_color", PALE_GOLD)
    frame.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "Войди или создай аккаунт, чтобы сохранять прогресс"
    subtitle.anchor_left = 0.08
    subtitle.anchor_right = 0.92
    subtitle.anchor_top = 0.15
    subtitle.anchor_bottom = 0.22
    subtitle.offset_left = 0
    subtitle.offset_right = 0
    subtitle.offset_top = 0
    subtitle.offset_bottom = 0
    subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    subtitle.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    subtitle.add_theme_font_size_override("font_size", 16)
    subtitle.add_theme_color_override("font_color", Color(0.84, 0.82, 0.77))
    frame.add_child(subtitle)

    account_username_input = LineEdit.new()
    account_username_input.anchor_left = 0.15
    account_username_input.anchor_right = 0.85
    account_username_input.anchor_top = 0.27
    account_username_input.anchor_bottom = 0.39
    account_username_input.offset_left = 0
    account_username_input.offset_right = 0
    account_username_input.offset_top = 0
    account_username_input.offset_bottom = 0
    account_username_input.placeholder_text = "ЛОГИН  •  3–20 СИМВОЛОВ"
    account_username_input.add_theme_font_size_override("font_size", 25)
    account_username_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
    frame.add_child(account_username_input)

    account_password_input = LineEdit.new()
    account_password_input.anchor_left = 0.15
    account_password_input.anchor_right = 0.85
    account_password_input.anchor_top = 0.42
    account_password_input.anchor_bottom = 0.54
    account_password_input.offset_left = 0
    account_password_input.offset_right = 0
    account_password_input.offset_top = 0
    account_password_input.offset_bottom = 0
    account_password_input.placeholder_text = "ПАРОЛЬ  •  ОТ 8 СИМВОЛОВ"
    account_password_input.secret = true
    account_password_input.add_theme_font_size_override("font_size", 25)
    account_password_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
    frame.add_child(account_password_input)

    var login := _ornate_button(frame, "ВОЙТИ ОНЛАЙН", 0.035, 0.60, 0.325, 0.715, 15, "party")
    login.pressed.connect(_account_login)
    var offline := _ornate_button(frame, "ОФЛАЙН • БОТЫ", 0.345, 0.60, 0.655, 0.715, 15, "nav")
    offline.pressed.connect(_account_offline_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.675, 0.60, 0.965, 0.715, 15, "nav")
    register.pressed.connect(_account_register)

    account_status_label = Label.new()
    account_status_label.anchor_left = 0.06
    account_status_label.anchor_right = 0.94
    account_status_label.anchor_top = 0.735
    account_status_label.anchor_bottom = 0.825
    account_status_label.offset_left = 0
    account_status_label.offset_right = 0
    account_status_label.offset_top = 0
    account_status_label.offset_bottom = 0
    account_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    account_status_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    account_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    account_status_label.add_theme_font_size_override("font_size", 15)
    account_status_label.add_theme_color_override("font_color", PALE_GOLD)
    frame.add_child(account_status_label)

    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.22, 0.85, 0.78, 0.94, 14, "nav")
    guest.pressed.connect(_account_guest)
    var close := _ornate_button(frame, "×", 0.91, 0.015, 0.975, 0.105, 19, "nav")
    close.pressed.connect(_close_account_panel)
    _refresh_profile_card()
'''
replace_func("_build_account_panel", "_open_account_panel", account_body)

# Give the mode screen a full-width description area and shorten the card headings.
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
    var heading := _add_label(frame, "ВЫБОР ИГРОВОГО РЕЖИМА", Vector2(24, 18), Vector2(700, 42), 23, PALE_GOLD)
    var subheading := _add_label(frame, "Выбери правила командной партии", Vector2(26, 62), Vector2(650, 30), 14, Color(0.78, 0.72, 0.63))
    var back := _ornate_button(frame, "← НАЗАД", 0.80, 0.035, 0.97, 0.135, 14, "nav")
    back.pressed.connect(_close_mode_selection)

    var names := ["Классика", "Командное голосование", "Несколько фигур"]
    var captions := [
        "Каждый участник управляет своей фигурой. В свой ход игрок может сделать допустимый ход или передать очередь союзнику. Команда играет против другой команды.",
        "Игрок предлагает ход, а союзники обсуждают и голосуют. За правильное командное решение предусмотрен бонус к наградам. Голосование ограничено временем.",
        "У каждого участника может быть несколько фигур. Игрок выбирает, какой фигурой ходить, или передаёт очередь союзнику. Система подсказывает, кому лучше передать ход."
    ]
    mode_choice_buttons.clear()
    for i in range(names.size()):
        var left := 0.035 + float(i) * 0.315
        var card := _ornate_button(frame, "%02d  |  %s" % [i + 1, names[i]], left, 0.235, left + 0.285, 0.535, 17, "card")
        card.pressed.connect(_select_mode_card.bind(names[i]))
        mode_choice_buttons.append(card)

    var details := _panel(frame, 0.035, 0.585, 0.965, 0.945)
    var details_title := _add_label(details, "КАК ПРОХОДИТ РЕЖИМ", Vector2(20, 12), Vector2(900, 32), 18, PALE_GOLD)
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

# Replace mode refresh to use concise button titles and full-width description.
refresh_body = '''func _refresh_mode_selection() -> void:
    var names := ["Классика", "Командное голосование", "Несколько фигур"]
    var captions := [
        "Каждый участник управляет своей фигурой. В свой ход игрок может сделать допустимый ход или передать очередь союзнику. Команда играет против другой команды.",
        "Игрок предлагает ход, а союзники обсуждают и голосуют. За правильное командное решение предусмотрен бонус к наградам. Голосование ограничено временем.",
        "У каждого участника может быть несколько фигур. Игрок выбирает, какой фигурой ходить, или передаёт очередь союзнику. Система подсказывает, кому лучше передать ход."
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

# Remove stale helper copy that sat over the mode cards in earlier layouts.
for stale in [
    '"НАЖМИ НА РЕЖИМ, ЧТОБЫ СРАЗУ ПЕРЕЙТИ К ПОДГОТОВКЕ"',
    '"НАЖМИ НА РЕЖИМ, ЧТОБЫ СРАЗУ ПЕРЕЙТИ К\\nПОДГОТОВКЕ"',
]:
    s = s.replace(stale, '""')

# Enlarge left menu card text without letting it overflow.
s = s.replace('task_title.add_theme_font_size_override("font_size", 19)', 'task_title.add_theme_font_size_override("font_size", 21)')
s = s.replace('task_desc.add_theme_font_size_override("font_size", 15)', 'task_desc.add_theme_font_size_override("font_size", 17)')
s = s.replace('pass_title.add_theme_font_size_override("font_size", 19)', 'pass_title.add_theme_font_size_override("font_size", 21)')
s = s.replace('pass_desc.add_theme_font_size_override("font_size", 15)', 'pass_desc.add_theme_font_size_override("font_size", 17)')
s = s.replace('event_title.add_theme_font_size_override("font_size", 19)', 'event_title.add_theme_font_size_override("font_size", 21)')
s = s.replace('event_desc.add_theme_font_size_override("font_size", 15)', 'event_desc.add_theme_font_size_override("font_size", 17)')

# Restore the mode-card selection callback that sits between the builder and refresh functions.
s = s.replace("func _refresh_mode_selection() -> void:", "func _select_mode_card(mode_name: String) -> void:\\n    selected_mode = mode_name\\n    _refresh_mode_selection()\\n\\nfunc _refresh_mode_selection() -> void:", 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v63 layout and typography patch applied")
