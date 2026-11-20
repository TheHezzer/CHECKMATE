from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

rep('var local_bot_test_active := false\n','var local_bot_test_active := false\nvar local_offline_mode_active := false\n', 'offline mode flag')

# The old visible debug shortcut is replaced by the offline option inside the account dialog.
rep('''    var bot_test := _ornate_button(menu_panel, "ИГРА С БОТАМИ • ПРОВЕРКА", 0.385, 0.265, 0.615, 0.325, 13, "nav")
    bot_test.name = "AdminBotTestButton"
    bot_test.text = "ПАРТИЯ С БОТАМИ • ВРЕМЕННО"
    bot_test.visible = true
    bot_test.pressed.connect(_developer_test_local_game)''','''    var bot_test := _ornate_button(menu_panel, "ИГРА С БОТАМИ • ПРОВЕРКА", 0.385, 0.265, 0.615, 0.325, 13, "nav")
    bot_test.name = "AdminBotTestButton"
    bot_test.visible = false''', 'hide temporary main menu bot shortcut')

# Split login/register row into online login, offline test and registration buttons.
rep('''    var login := _ornate_button(frame, "ВОЙТИ", 0.075, 0.49, 0.475, 0.605, 18, "party")
    login.pressed.connect(_account_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.525, 0.49, 0.925, 0.605, 18, "nav")
    register.pressed.connect(_account_register)''','''    var login := _ornate_button(frame, "ВОЙТИ ОНЛАЙН", 0.055, 0.49, 0.345, 0.605, 15, "party")
    login.pressed.connect(_account_login)
    var offline := _ornate_button(frame, "ОФЛАЙН • БОТЫ", 0.365, 0.49, 0.635, 0.605, 15, "nav")
    offline.pressed.connect(_account_offline_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.655, 0.49, 0.945, 0.605, 15, "nav")
    register.pressed.connect(_account_register)''', 'add offline button to account dialog')

# Local-only administrator login; no server request is made and no online account token is fabricated.
rep('''func _account_register() -> void:
    var username := account_username_input.text.strip_edges()''','''func _account_offline_login() -> void:
    var username := account_username_input.text.strip_edges()
    var password := account_password_input.text
    if username != "TheHezzer" or password != "admin":
        _set_account_error("Неверные офлайн-данные администратора.")
        return
    local_offline_mode_active = true
    local_bot_test_active = true
    developer_mode = true
    account_username = "TheHezzer"
    if developer_test_menu:
        developer_test_menu.visible = false
    _close_account_panel()
    if menu_panel:
        menu_panel.visible = true
    _refresh_profile_card()
    _show_notice("ОФЛАЙН-РЕЖИМ ВКЛЮЧЁН. Партии будут проходить только с ботами.")
    
func _account_register() -> void:
    var username := account_username_input.text.strip_edges()''', 'offline admin credentials action')

# When the user chooses a mode and reaches matchmaking, never contact the online server.
rep('''func _open_matchmaking_queue() -> void:
    if online_panel == null:''','''func _open_matchmaking_queue() -> void:
    if local_offline_mode_active:
        if online_panel == null:
            _build_online_panel_screen()
        online_panel.visible = true
        if queue_rating_label:
            queue_rating_label.text = "ОФЛАЙН • ИГРА С БОТАМИ"
        if queue_status_label:
            queue_status_label.text = "Собираем локальную партию против ботов…"
        if queue_timer_label:
            queue_timer_label.text = "ОФЛАЙН"
        _start_local_bot_queue()
        return
    if online_panel == null:''', 'route every selected mode into offline bot queue')

# Offline test sessions use the bot controller regardless of whether admin features are enabled.
rep('''    if not (developer_mode or local_bot_test_active) or not online_panel or not online_panel.visible:''','''    if not (developer_mode or local_bot_test_active or local_offline_mode_active) or not online_panel or not online_panel.visible:''', 'offline match launch')
rep('''    if not (developer_mode or local_bot_test_active) or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:''','''    if not (developer_mode or local_bot_test_active or local_offline_mode_active) or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:''', 'offline bot move')
rep('''    if not (developer_mode or local_bot_test_active) or game_over or local_opening_vote_active:''','''    if not (developer_mode or local_bot_test_active or local_offline_mode_active) or game_over or local_opening_vote_active:''', 'offline bot scheduler')
rep('''    local_bot_test_active = false
    local_bot_roster.clear()''','''    local_bot_test_active = false
    local_offline_mode_active = false
    developer_mode = false
    local_bot_roster.clear()''', 'clear offline admin mode when returning to menu')

# Keep the old explicit developer-only launch button disabled even if its function remains for compatibility.
p.write_text(s, encoding="utf-8")
print("CHECKMATE v62 offline admin login and bots-only mode patch applied")
