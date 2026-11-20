from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")
def rep(old, new, name):
    global s
    if old not in s: raise SystemExit("Missing source block: " + name)
    s = s.replace(old, new, 1)

rep('var account_token := ""\nvar account_player_id := ""\n', '''var account_token := ""
var account_player_id := ""
var account_username := ""
var account_panel: Control
var account_username_input: LineEdit
var account_password_input: LineEdit
var account_status_label: Label
var profile_name_label: Label
var profile_state_label: Label
''', "account variables")
rep('    _build_developer_login()\n    _build_startup_sequence()\n', '    _build_developer_login()\n    _build_account_panel()\n    _build_startup_sequence()\n', "ready")
rep('''    var dev_access := Button.new()
    dev_access.flat = true
    dev_access.position = Vector2(7, 5)
    dev_access.size = Vector2(78, 92)
    dev_access.modulate = Color(1,1,1,0.01)
    dev_access.pressed.connect(_open_developer_login)
    profile.add_child(dev_access)
    _add_label(profile, "ГОСТЬ", Vector2(92, 10), Vector2(175, 25), 18, PALE_GOLD)
    _add_label(profile, "ВХОД — СКОРО", Vector2(92, 39), Vector2(150, 20), 13, Color(0.55, 0.55, 0.55))
    _add_label(profile, "ТЕСТОВЫЙ ДОСТУП: нажми портрет", Vector2(92, 58), Vector2(185, 18), 9, Color(0.66, 0.62, 0.56))
''', '''    var profile_hit := Button.new()
    profile_hit.flat = true
    profile_hit.position = Vector2(3, 3)
    profile_hit.size = Vector2(245, 94)
    profile_hit.modulate = Color(1,1,1,0.01)
    profile_hit.pressed.connect(_open_account_panel)
    profile.add_child(profile_hit)
    profile_name_label = _add_label(profile, "ГОСТЬ", Vector2(92, 10), Vector2(175, 25), 18, PALE_GOLD)
    profile_state_label = _add_label(profile, "НАЖМИ НА АВАТАР • ВОЙТИ", Vector2(92, 39), Vector2(150, 20), 12, Color(0.72, 0.72, 0.72))
    _add_label(profile, "ПРОГРЕСС НА ЭТОМ УСТРОЙСТВЕ", Vector2(92, 58), Vector2(185, 18), 9, Color(0.66, 0.62, 0.56))
''', "profile avatar")
rep('''        account_token = str(cfg.get_value("account", "token", ""))
        account_player_id = str(cfg.get_value("account", "player_id", ""))
''', '''        account_token = str(cfg.get_value("account", "token", ""))
        account_player_id = str(cfg.get_value("account", "player_id", ""))
        account_username = str(cfg.get_value("account", "username", ""))
''', "load username")
rep('''    cfg.set_value("account", "token", account_token)
    cfg.set_value("account", "player_id", account_player_id)
''', '''    cfg.set_value("account", "token", account_token)
    cfg.set_value("account", "player_id", account_player_id)
    cfg.set_value("account", "username", account_username)
''', "save username")
rep('''        "account_register", "account_login":
            account_token = str(payload.get("token", ""))
            var account: Dictionary = payload.get("account", {})
            account_player_id = str(account.get("playerId", ""))
            if account_token.is_empty() or account_player_id.is_empty():
                if city_status_label: city_status_label.text = "Сервер не вернул профиль."
            else:
                _save_economy()
                if city_status_label: city_status_label.text = "Вход выполнен: " + str(account.get("username", "Игрок"))
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
''', '''        "account_register", "account_login":
            account_token = str(payload.get("token", ""))
            var account: Dictionary = payload.get("account", {})
            account_player_id = str(account.get("playerId", ""))
            account_username = str(account.get("username", "Игрок"))
            if account_token.is_empty() or account_player_id.is_empty():
                _set_account_status("Сервер не вернул профиль.")
            else:
                _save_economy()
                _refresh_profile_card()
                _set_account_status("Вход выполнен: " + account_username + ". Загружаем прогресс…")
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
''', "account response")
rep('''        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))
            if city_status_label: city_status_label.text = "Прогресс Шахматного города сохранён на сервере."
''', '''        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))
            if not account_token.is_empty():
                _set_account_status("Аккаунт подключён. Прогресс синхронизирован с сервером.")
            if city_status_label: city_status_label.text = "Прогресс Шахматного города сохранён на сервере."
''', "profile response")
rep('''        if action.begins_with("city_") or action.begins_with("account_"):
            if city_status_label: city_status_label.text = error_text
''', '''        if action.begins_with("city_") or action.begins_with("account_"):
            _set_account_status(error_text)
            if city_status_label: city_status_label.text = error_text
''', "account errors")
rep('''        if city_status_label and (action.begins_with("city_") or action.begins_with("account_")): city_status_label.text = message
''', '''        if action.begins_with("city_") or action.begins_with("account_"):
            _set_account_status(message)
            if city_status_label: city_status_label.text = message
''', "server url errors")
rep('''    if result != OK:
        if city_status_label and (action.begins_with("city_") or action.begins_with("account_")): city_status_label.text = "Не удалось отправить запрос: " + str(result)
        elif queue_status_label: queue_status_label.text = "Не удалось отправить запрос: " + str(result)
''', '''    if result != OK:
        if action.begins_with("city_") or action.begins_with("account_"):
            _set_account_status("Не удалось отправить запрос: " + str(result))
            if city_status_label: city_status_label.text = "Не удалось отправить запрос: " + str(result)
        elif queue_status_label: queue_status_label.text = "Не удалось отправить запрос: " + str(result)
''', "request errors")
modal = r'''func _build_account_panel() -> void:
    account_panel = Control.new()
    account_panel.name = "AccountDialog"
    account_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    account_panel.visible = false
    ui.add_child(account_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.0, 0.0, 0.0, 0.84)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    account_panel.add_child(shade)
    var frame := _panel(account_panel, 0.24, 0.16, 0.76, 0.84)
    _add_label(frame, "АККАУНТ CHECKMATE", Vector2(28, 18), Vector2(590, 44), 26, PALE_GOLD)
    _add_label(frame, "Играй гостем или войди, чтобы сохранить прогресс в аккаунте.", Vector2(30, 66), Vector2(640, 30), 14, Color(0.84, 0.82, 0.77))
    account_username_input = LineEdit.new()
    account_username_input.position = Vector2(32, 116)
    account_username_input.size = Vector2(540, 46)
    account_username_input.placeholder_text = "Логин (3–20 символов)"
    account_username_input.add_theme_font_size_override("font_size", 18)
    frame.add_child(account_username_input)
    account_password_input = LineEdit.new()
    account_password_input.position = Vector2(32, 176)
    account_password_input.size = Vector2(540, 46)
    account_password_input.placeholder_text = "Пароль (от 8 символов)"
    account_password_input.secret = true
    account_password_input.add_theme_font_size_override("font_size", 18)
    frame.add_child(account_password_input)
    var login := _ornate_button(frame, "ВОЙТИ", 0.045, 0.49, 0.48, 0.61, 15, "party")
    login.pressed.connect(_account_login)
    var register := _ornate_button(frame, "СОЗДАТЬ АККАУНТ", 0.52, 0.49, 0.955, 0.61, 14, "nav")
    register.pressed.connect(_account_register)
    account_status_label = _add_label(frame, "Гостевой режим активен. Прогресс хранится на этом устройстве.", Vector2(32, 278), Vector2(650, 44), 13, PALE_GOLD)
    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.045, 0.70, 0.955, 0.83, 16, "nav")
    guest.pressed.connect(_account_guest)
    var developer := _ornate_button(frame, "ТЕСТ РАЗРАБОТЧИКА", 0.045, 0.86, 0.48, 0.96, 11, "nav")
    developer.pressed.connect(func(): account_panel.visible = false; _open_developer_login())
    var close := _ornate_button(frame, "ЗАКРЫТЬ", 0.52, 0.86, 0.955, 0.96, 11, "nav")
    close.pressed.connect(_close_account_panel)
    _refresh_profile_card()

func _open_account_panel() -> void:
    if account_panel == null:
        _build_account_panel()
    account_panel.visible = true
    if account_token.is_empty():
        _set_account_status("Гостевой режим: сохранение только на этом устройстве. После удаления игры данные могут пропасть.")
    else:
        _set_account_status("Аккаунт подключён: " + (account_username if not account_username.is_empty() else "Игрок") + ".")

func _close_account_panel() -> void:
    if account_panel:
        account_panel.visible = false

func _account_guest() -> void:
    if account_token.is_empty():
        _set_account_status("Ты играешь гостем. Прогресс хранится локально и не восстановится после удаления данных игры.")
    _close_account_panel()

func _account_login() -> void:
    var username := account_username_input.text.strip_edges()
    var password := account_password_input.text
    if username.is_empty() or password.is_empty():
        _set_account_status("Введи логин и пароль.")
        return
    _set_account_status("Подключаем аккаунт…")
    _send_matchmaking_request("account_login", "/accounts/login", HTTPClient.METHOD_POST, {"username": username, "password": password})

func _account_register() -> void:
    var username := account_username_input.text.strip_edges()
    var password := account_password_input.text
    if username.length() < 3 or username.length() > 20:
        _set_account_status("Логин должен содержать от 3 до 20 символов.")
        return
    if password.length() < 8:
        _set_account_status("Пароль должен содержать минимум 8 символов.")
        return
    _set_account_status("Создаём аккаунт…")
    _send_matchmaking_request("account_register", "/accounts/register", HTTPClient.METHOD_POST, {"username": username, "password": password})

func _set_account_status(message: String) -> void:
    if account_status_label:
        account_status_label.text = message

func _refresh_profile_card() -> void:
    if profile_name_label:
        profile_name_label.text = account_username if not account_token.is_empty() and not account_username.is_empty() else ("АККАУНТ" if not account_token.is_empty() else "ГОСТЬ")
    if profile_state_label:
        profile_state_label.text = "ПРОГРЕСС СОХРАНЯЕТСЯ" if not account_token.is_empty() else "НАЖМИ НА АВАТАР • ВОЙТИ"

'''
marker = "func _build_developer_login() -> void:\n"
if marker not in s: raise SystemExit("Missing modal insertion point")
s = s.replace(marker, modal + marker, 1)
p.write_text(s, encoding="utf-8")
print("Account dialog v46 added")
