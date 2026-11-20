from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

rep('var developer_pass_input: LineEdit\n',
'''var developer_pass_input: LineEdit
var developer_test_menu: Control
var developer_test_status: Label
''', "developer vars")

rep('''    _build_developer_login()
    _build_account_panel()
    _build_startup_sequence()
''', '''    _build_developer_login()
    _build_account_panel()
    _build_developer_test_menu()
    _build_startup_sequence()
''', "ready test menu")

rep('''            else:
                _save_economy()
                _refresh_profile_card()
                _set_account_status("Вход выполнен: " + account_username + ". Загружаем прогресс…")
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
''', '''            else:
                _save_economy()
                _refresh_profile_card()
                var welcome := "Добро пожаловать, " + account_username + "!"
                _set_account_status(welcome + " Загружаем твой прогресс…")
                _show_notice(welcome)
                _close_account_panel()
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
''', "welcome after auth")

rep('''        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))
            if not account_token.is_empty():
                _set_account_status("Аккаунт подключён. Прогресс синхронизирован с сервером.")
''', '''        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))
            if not account_token.is_empty():
                _set_account_status("Аккаунт подключён. Прогресс синхронизирован с сервером.")
                _refresh_profile_card()
''', "refresh profile on sync")

rep('''        "playerName": "Игрок-" + online_player_id.substr(0, 5).to_upper(),
''', '''        "playerName": account_username if not account_token.is_empty() and not account_username.is_empty() else "Игрок-" + online_player_id.substr(0, 5).to_upper(),
''', "queue uses nickname")

rep('''    var developer := _ornate_button(frame, "ТЕСТ РАЗРАБОТЧИКА", 0.045, 0.86, 0.48, 0.96, 11, "nav")
    developer.pressed.connect(func(): account_panel.visible = false; _open_developer_login())
''', '''    var developer := _ornate_button(frame, "ТЕСТ РАЗРАБОТЧИКА", 0.045, 0.86, 0.48, 0.96, 11, "nav")
    developer.pressed.connect(_open_developer_login_from_account)
''', "developer button signal")

rep('''func _open_developer_login() -> void:
    if developer_login_panel:
        developer_login_panel.visible = true
        developer_user_input.text = ""
        developer_pass_input.text = ""

func _submit_developer_login() -> void:
    if developer_user_input.text.strip_edges() == "TheHezzer" and developer_pass_input.text == "admin":
        developer_mode = true
        developer_login_panel.visible = false
        _show_notice("ТЕСТОВЫЙ РЕЖИМ ВКЛЮЧЁН • доступны тестовые боты и локальная проверка режимов")
    else:
        _show_notice("Неверный тестовый логин или пароль.")
''', '''func _open_developer_login_from_account() -> void:
    if account_panel:
        account_panel.visible = false
    _open_developer_login()

func _open_developer_login() -> void:
    if developer_login_panel:
        developer_login_panel.visible = true
        developer_user_input.text = ""
        developer_pass_input.text = ""

func _submit_developer_login() -> void:
    var login_name := developer_user_input.text.strip_edges()
    var login_password := developer_pass_input.text
    if login_name == "TheHezzer" and login_password == "admin":
        developer_mode = true
        developer_login_panel.visible = false
        if developer_test_menu:
            developer_test_menu.visible = true
        if menu_panel:
            menu_panel.visible = false
        _show_notice("Вы вошли в тестовый режим, TheHezzer!")
    else:
        developer_pass_input.text = ""
        _show_notice("Неверный тестовый логин или пароль.")
''', "developer login behavior")

# Insert the developer-only test menu before bot queue logic.
marker = "func _start_local_bot_queue() -> void:\n"
menu_code = '''func _build_developer_test_menu() -> void:
    developer_test_menu = Control.new()
    developer_test_menu.name = "DeveloperOnlyTestMenu"
    developer_test_menu.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    developer_test_menu.visible = false
    ui.add_child(developer_test_menu)
    var shade := ColorRect.new()
    shade.color = Color(0.012, 0.010, 0.009, 0.97)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    developer_test_menu.add_child(shade)
    var frame := _panel(developer_test_menu, 0.18, 0.12, 0.82, 0.88)
    _add_label(frame, "ПАНЕЛЬ ТЕСТИРОВАНИЯ", Vector2(24, 18), Vector2(620, 48), 28, PALE_GOLD)
    _add_label(frame, "ДОСТУП РАЗРАБОТЧИКА • TheHezzer", Vector2(26, 68), Vector2(620, 28), 15, Color(0.82, 0.76, 0.66))
    developer_test_status = _add_label(frame, "Тестовый режим активен. Эти инструменты видны только тестовому аккаунту.", Vector2(26, 112), Vector2(650, 44), 14, PALE_GOLD)
    var classic := _ornate_button(frame, "ТЕСТ КЛАССИКИ С БОТАМИ", 0.06, 0.29, 0.94, 0.43, 17, "party")
    classic.pressed.connect(_developer_test_classic)
    var voting := _ornate_button(frame, "ТЕСТ КОМАНДНОГО ГОЛОСОВАНИЯ", 0.06, 0.48, 0.94, 0.62, 16, "card")
    voting.pressed.connect(_developer_test_voting)
    var local_game := _ornate_button(frame, "ЗАПУСТИТЬ ЛОКАЛЬНУЮ ПАРТИЮ", 0.06, 0.67, 0.94, 0.81, 16, "card")
    local_game.pressed.connect(_developer_test_local_game)
    var exit := _ornate_button(frame, "ВЫЙТИ ИЗ ТЕСТОВОГО РЕЖИМА", 0.20, 0.85, 0.80, 0.96, 14, "nav")
    exit.pressed.connect(_developer_test_logout)

func _developer_test_classic() -> void:
    if not developer_mode:
        return
    selected_mode = "Классика"
    developer_test_menu.visible = false
    _open_matchmaking_queue()

func _developer_test_voting() -> void:
    if not developer_mode:
        return
    selected_mode = "Командное голосование"
    developer_test_menu.visible = false
    _open_matchmaking_queue()

func _developer_test_local_game() -> void:
    if not developer_mode:
        return
    selected_mode = "Классика"
    developer_test_menu.visible = false
    _start_game(selected_mode)
    status_label.text = "ТЕСТОВЫЙ РЕЖИМ • ЛОКАЛЬНАЯ ПАРТИЯ"

func _developer_test_logout() -> void:
    developer_mode = false
    if developer_test_menu:
        developer_test_menu.visible = false
    if menu_panel:
        menu_panel.visible = true
    _show_notice("Вы вышли из тестового режима.")

'''
if marker not in s:
    raise SystemExit("Missing bot queue insertion point")
s = s.replace(marker, menu_code + marker, 1)

p.write_text(s, encoding="utf-8")
print("Developer test menu and account welcome patch applied.")
