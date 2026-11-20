from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

# Preview: move it down, enlarge the piece and give the camera a subtle top-down angle.
rep('''    preview_container.anchor_left = 0.315
    preview_container.anchor_top = 0.225
    preview_container.anchor_right = 0.685
    preview_container.anchor_bottom = 0.735''','''    preview_container.anchor_left = 0.285
    preview_container.anchor_top = 0.245
    preview_container.anchor_right = 0.715
    preview_container.anchor_bottom = 0.775''', "larger lower preview viewport")
rep('''    preview_camera.position = Vector3(0, 0, 6.6)
    preview_camera.fov = 32
    preview_camera_pivot.add_child(preview_camera)
    preview_camera.look_at(Vector3(0, 1.05, 0), Vector3.UP)''','''    preview_camera.position = Vector3(0, 1.25, 5.45)
    preview_camera.fov = 30
    preview_camera_pivot.add_child(preview_camera)
    preview_camera.look_at(Vector3(0, 1.05, 0), Vector3.UP)''', "top down zoom camera")
rep('''    preview_pawn.position.y = 0.43
    preview_pawn.position.z = 0.0''','''    preview_pawn.position.y = 0.30
    preview_pawn.position.z = 0.0
    preview_pawn.scale = Vector3(1.22, 1.22, 1.22)''', "lower larger figure")
# Remove side arrow buttons altogether.
rep('''    var left_arrow := _ornate_button(menu_panel, "❮", 0.335, 0.445, 0.405, 0.565, 38, "arrow")
    left_arrow.pressed.connect(func(): _change_piece(-1))
    var right_arrow := _ornate_button(menu_panel, "❯", 0.595, 0.445, 0.665, 0.565, 38, "arrow")
    right_arrow.pressed.connect(func(): _change_piece(1))
''','', "remove piece arrows")
# Lower the main party plaque and remove any instructional helper copy from the button itself.
rep('''    var party := _ornate_button(menu_panel, "⚔   П А Р Т И Я", 0.365, 0.145, 0.635, 0.255, 26, "party")''','''    var party := _ornate_button(menu_panel, "П А Р Т И Я", 0.365, 0.185, 0.635, 0.295, 26, "party")''', "lower clean party button")
# Currency counters: slightly smaller type.
rep('''var gambits := _ornate_button(menu_panel, "◈  ЗЛОТЫЕ\\n%d" % int(balances["zloty"]), 0.275, 0.035, 0.425, 0.125, 17, "nav")''','''var gambits := _ornate_button(menu_panel, "◈  ЗЛОТЫЕ\\n%d" % int(balances["zloty"]), 0.275, 0.035, 0.425, 0.125, 12, "nav")''', "smaller zloty counter")
rep('''var chessmatites := _ornate_button(menu_panel, "◆  ШАХМАТИТЫ\\n%d   +" % int(balances["chessmatites"]), 0.432, 0.035, 0.575, 0.125, 17, "nav")''','''var chessmatites := _ornate_button(menu_panel, "◆  ШАХМАТИТЫ\\n%d   +" % int(balances["chessmatites"]), 0.432, 0.035, 0.575, 0.125, 12, "nav")''', "smaller gambits counter")
rep('''var experience := _ornate_button(menu_panel, "★  XP\\n%d" % int(balances["xp"]), 0.582, 0.035, 0.722, 0.125, 17, "nav")''','''var experience := _ornate_button(menu_panel, "★  XP\\n%d" % int(balances["xp"]), 0.582, 0.035, 0.722, 0.125, 12, "nav")''', "smaller xp counter")
# Left information cards: larger but fitted text.
for old,new,label in [
('task_title.add_theme_font_size_override("font_size", 19)','task_title.add_theme_font_size_override("font_size", 20)',"daily title"),
('task_desc.add_theme_font_size_override("font_size", 15)','task_desc.add_theme_font_size_override("font_size", 16)',"daily body"),
('pass_title.add_theme_font_size_override("font_size", 19)','pass_title.add_theme_font_size_override("font_size", 20)',"pass title"),
('pass_desc.add_theme_font_size_override("font_size", 15)','pass_desc.add_theme_font_size_override("font_size", 16)',"pass body"),
('event_title.add_theme_font_size_override("font_size", 19)','event_title.add_theme_font_size_override("font_size", 20)',"event title"),
('event_desc.add_theme_font_size_override("font_size", 15)','event_desc.add_theme_font_size_override("font_size", 16)',"event body"),
]:
    rep(old,new,label)

# Remove the dark opaque center from all decorative button frames while retaining their ornamental edges.
rep('''    normal.draw_center = true''','''    normal.draw_center = false''', "transparent button centers")

# Rebuild the account form with centered, larger fields and no overlapping labels/buttons.
start = s.index("func _build_account_panel() -> void:")
end = s.index("func _open_account_panel() -> void:", start)
new_form = '''func _build_account_panel() -> void:
    account_panel = Control.new()
    account_panel.name = "AccountDialog"
    account_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    account_panel.visible = false
    ui.add_child(account_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.0, 0.0, 0.0, 0.86)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    account_panel.add_child(shade)
    var frame := _panel(account_panel, 0.20, 0.08, 0.80, 0.92)
    var account_title := _add_label(frame, "ДОБРО ПОЖАЛОВАТЬ", Vector2(34, 18), Vector2(820, 58), 27, PALE_GOLD)
    account_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    account_title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    var subtitle := _add_label(frame, "Войди или создай аккаунт, чтобы сохранять прогресс.", Vector2(42, 78), Vector2(800, 34), 12, Color(0.84, 0.82, 0.77))
    subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

    account_username_input = LineEdit.new()
    account_username_input.position = Vector2(110, 142)
    account_username_input.size = Vector2(700, 72)
    account_username_input.placeholder_text = "ЛОГИН  •  3–20 символов"
    account_username_input.add_theme_font_size_override("font_size", 28)
    account_username_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
    frame.add_child(account_username_input)

    account_password_input = LineEdit.new()
    account_password_input.position = Vector2(110, 238)
    account_password_input.size = Vector2(700, 72)
    account_password_input.placeholder_text = "ПАРОЛЬ  •  от 8 символов"
    account_password_input.secret = true
    account_password_input.add_theme_font_size_override("font_size", 28)
    account_password_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
    frame.add_child(account_password_input)

    var login := _ornate_button(frame, "ВОЙТИ", 0.075, 0.49, 0.475, 0.605, 18, "party")
    login.pressed.connect(_account_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.525, 0.49, 0.925, 0.605, 18, "nav")
    register.pressed.connect(_account_register)

    account_status_label = _add_label(frame, "", Vector2(42, 448), Vector2(800, 68), 13, PALE_GOLD)
    account_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    account_status_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    account_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.075, 0.755, 0.925, 0.855, 15, "nav")
    guest.pressed.connect(_account_guest)
    var close := _ornate_button(frame, "ЗАКРЫТЬ", 0.30, 0.88, 0.70, 0.97, 13, "nav")
    close.pressed.connect(_close_account_panel)
    _refresh_profile_card()

'''
s = s[:start] + new_form + s[end:]

# Account status helpers with red server-validation feedback.
rep('''func _set_account_status(message: String) -> void:
    if account_status_label:
        account_status_label.text = message''','''func _set_account_status(message: String) -> void:
    if account_status_label:
        account_status_label.text = message
        account_status_label.add_theme_color_override("font_color", PALE_GOLD)

func _set_account_error(message: String) -> void:
    if account_status_label:
        account_status_label.text = message
        account_status_label.add_theme_color_override("font_color", Color(1.0, 0.24, 0.20))''', "account error label helper")

# Client-side validation mirrors the account server's rules.
rep('''    if username.is_empty() or password.is_empty():
        _set_account_status("Введи логин и пароль.")
        return
    _set_account_status("Подключаем аккаунт…")''','''    var login_pattern := RegEx.new()
    login_pattern.compile("^[A-Za-z0-9_]{3,20}$")
    if login_pattern.search(username) == null:
        _set_account_error("Логин: 3–20 символов, латинские буквы, цифры и _.")
        return
    if password.length() < 8 or password.length() > 128:
        _set_account_error("Пароль должен содержать от 8 до 128 символов.")
        return
    _set_account_status("Проверяем логин и пароль на сервере…")''', "validate login")
rep('''    if username.length() < 3 or username.length() > 20:
        _set_account_status("Логин должен содержать от 3 до 20 символов.")
        return
    if password.length() < 8:
        _set_account_status("Пароль должен содержать минимум 8 символов.")
        return
    _set_account_status("Создаём аккаунт…")''','''    var login_pattern := RegEx.new()
    login_pattern.compile("^[A-Za-z0-9_]{3,20}$")
    if login_pattern.search(username) == null:
        _set_account_error("Логин: 3–20 символов, латинские буквы, цифры и _.")
        return
    if password.length() < 8 or password.length() > 128:
        _set_account_error("Пароль должен содержать от 8 до 128 символов.")
        return
    _set_account_status("Отправляем данные регистрации на сервер…")''', "validate registration")

# Localized red server errors for invalid credentials and registration conflicts.
rep('''        if action.begins_with("city_") or action.begins_with("account_"):
            _set_account_status(error_text)
            if city_status_label: city_status_label.text = error_text
        else:''','''        if action == "account_login" and response_code == 401:
            _set_account_error("Неверный логин и/или пароль.")
        elif action == "account_register" and payload is Dictionary:
            var server_error := str(payload.get("error", ""))
            var register_message := "Не удалось зарегистрироваться. Попробуй ещё раз."
            if server_error == "USERNAME_TAKEN":
                register_message = "Этот логин уже занят. Выбери другой."
            elif server_error == "USERNAME_INVALID":
                register_message = "Логин: 3–20 символов, латинские буквы, цифры и _."
            elif server_error == "PASSWORD_INVALID":
                register_message = "Пароль должен содержать от 8 до 128 символов."
            elif server_error == "ADMIN_USERNAME_RESERVED":
                register_message = "Этот логин зарезервирован."
            _set_account_error(register_message)
        elif action.begins_with("city_") or action.begins_with("account_"):
            _set_account_error(error_text)
            if city_status_label: city_status_label.text = error_text
        else:''', "localized server errors")

# Ensure account panel opens with a clean centered status, not a stale error.
rep('''    account_panel.visible = true
    if account_token.is_empty():''','''    account_panel.visible = true
    if account_status_label:
        account_status_label.text = ""
        account_status_label.add_theme_color_override("font_color", PALE_GOLD)
    if account_token.is_empty():''', "clear account status on open")

# Remove instructional text from the tutorial copy which previously described the party button.
rep('''        "Нажми большую кнопку ПАРТИЯ. Откроется выбор режима. Нажатие на карточку режима сразу ведёт к подготовке, отдельной кнопки «Продолжить» больше нет.",''','''        "Открой раздел партии и выбери подходящий режим. Нажатие на карточку режима сразу ведёт к подготовке.",''', "simplify party tutorial text")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v61 visual and account form patch applied")
