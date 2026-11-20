from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

# Remember-me persistence: store the account token only after explicit opt-in.
rep("var account_status_label: Label\n", "var account_status_label: Label\nvar remember_me_checkbox: CheckBox\nvar remember_me := false\n", "remember state")
rep('''        account_token = str(cfg.get_value("account", "token", ""))
        account_player_id = str(cfg.get_value("account", "player_id", ""))
        account_username = str(cfg.get_value("account", "username", ""))''', '''        remember_me = bool(cfg.get_value("account", "remember_me", false))
        account_token = str(cfg.get_value("account", "token", "")) if remember_me else ""
        account_player_id = str(cfg.get_value("account", "player_id", "")) if remember_me else ""
        account_username = str(cfg.get_value("account", "username", "")) if remember_me else ""''', "load remembered account")
rep('''    cfg.set_value("account", "token", account_token)
    cfg.set_value("account", "player_id", account_player_id)
    cfg.set_value("account", "username", account_username)''', '''    cfg.set_value("account", "remember_me", remember_me)
    cfg.set_value("account", "token", account_token if remember_me else "")
    cfg.set_value("account", "player_id", account_player_id if remember_me else "")
    cfg.set_value("account", "username", account_username if remember_me else "")''', "save remembered account")

# Remove the stuck central 3D display figure; keep the row of selectable silhouettes.
rep('''    preview_container.mouse_filter = Control.MOUSE_FILTER_STOP
    preview_container.stretch = true''', '''    preview_container.mouse_filter = Control.MOUSE_FILTER_IGNORE
    preview_container.stretch = true
    preview_container.visible = false''', "hide central stuck piece")
rep('''    piece_name.anchor_top = 0.615
    piece_name.anchor_bottom = 0.615''', '''    piece_name.anchor_top = 0.535
    piece_name.anchor_bottom = 0.535''', "move piece title")
rep('''    silhouette_row.anchor_top = 0.715
    silhouette_row.anchor_bottom = 0.905''', '''    silhouette_row.anchor_top = 0.585
    silhouette_row.anchor_bottom = 0.805''', "move piece selector")

# Increase the board's vertical viewing angle.
rep('''    camera.position = Vector3(0, 12.4, 12.4)
    camera.look_at(Vector3(0, 0.50, -0.4), Vector3.UP)''', '''    camera.position = Vector3(0, 14.8, 10.8)
    camera.look_at(Vector3(0, 0.50, -0.4), Vector3.UP)''', "higher board camera")

# Reduce interface text so it stays within its own areas and doesn't cover squares.
for old, new, label in [
    ('team_turn_label.add_theme_font_size_override("font_size", 22)', 'team_turn_label.add_theme_font_size_override("font_size", 16)', "turn label"),
    ('team_clock_label = _add_label(game_panel, "БЕЛЫЕ 10:00     ЧЁРНЫЕ 10:00", Vector2.ZERO, Vector2(620, 32), 20, PALE_GOLD)', 'team_clock_label = _add_label(game_panel, "БЕЛЫЕ 10:00     ЧЁРНЫЕ 10:00", Vector2.ZERO, Vector2(620, 28), 16, PALE_GOLD)', "team clock"),
    ('player_clock_label = _add_label(game_panel, "ХОД ИГРОКА: 20 СЕК.", Vector2.ZERO, Vector2(420, 26), 17, Color(0.55, 0.92, 0.98))', 'player_clock_label = _add_label(game_panel, "ХОД ИГРОКА: 20 СЕК.", Vector2.ZERO, Vector2(420, 24), 15, Color(0.55, 0.92, 0.98))', "player clock"),
    ('team_vote_side_label.add_theme_font_size_override("font_size", 17)', 'team_vote_side_label.add_theme_font_size_override("font_size", 14)', "vote text"),
    ('task_title.add_theme_font_size_override("font_size", 17)', 'task_title.add_theme_font_size_override("font_size", 14)', "task title"),
    ('task_desc.add_theme_font_size_override("font_size", 17)', 'task_desc.add_theme_font_size_override("font_size", 12)', "task description"),
    ('pass_title.add_theme_font_size_override("font_size", 17)', 'pass_title.add_theme_font_size_override("font_size", 14)', "pass title"),
    ('pass_desc.add_theme_font_size_override("font_size", 17)', 'pass_desc.add_theme_font_size_override("font_size", 12)', "pass description"),
    ('event_title.add_theme_font_size_override("font_size", 17)', 'event_title.add_theme_font_size_override("font_size", 14)', "event title"),
    ('event_desc.add_theme_font_size_override("font_size", 17)', 'event_desc.add_theme_font_size_override("font_size", 12)', "event description"),
]:
    rep(old, new, label)

# Remove the persistent top wallet strip; the individual currency buttons in the main menu remain.
start = s.index("func _build_wallet_hud() -> void:")
end = s.index("func _refresh_wallet_hud() -> void:", start)
s = s[:start] + '''func _build_wallet_hud() -> void:
    wallet_hud = Control.new()
    wallet_hud.name = "PersistentWalletHUD"
    wallet_hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    wallet_hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
    wallet_hud.visible = false
    ui.add_child(wallet_hud)

''' + s[end:]

# Add the checkbox between password and the three account actions.
rep('''    var login := _ornate_button(frame, "ВОЙТИ ОНЛАЙН", 0.045, 0.565, 0.345, 0.685, 14, "party")
    login.pressed.connect(_account_login)
    var offline := _ornate_button(frame, "ОФЛАЙН • БОТЫ", 0.355, 0.565, 0.645, 0.685, 14, "nav")
    offline.pressed.connect(_account_offline_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.655, 0.565, 0.955, 0.685, 14, "nav")
    register.pressed.connect(_account_register)''', '''    remember_me_checkbox = CheckBox.new()
    remember_me_checkbox.text = "ЗАПОМНИТЬ МЕНЯ"
    remember_me_checkbox.anchor_left = 0.15
    remember_me_checkbox.anchor_right = 0.85
    remember_me_checkbox.anchor_top = 0.525
    remember_me_checkbox.anchor_bottom = 0.575
    remember_me_checkbox.offset_left = 0
    remember_me_checkbox.offset_right = 0
    remember_me_checkbox.offset_top = 0
    remember_me_checkbox.offset_bottom = 0
    remember_me_checkbox.button_pressed = remember_me
    remember_me_checkbox.add_theme_font_override("font", UI_FONT)
    remember_me_checkbox.add_theme_font_size_override("font_size", 16)
    remember_me_checkbox.add_theme_color_override("font_color", PALE_GOLD)
    remember_me_checkbox.toggled.connect(_on_remember_me_toggled)
    frame.add_child(remember_me_checkbox)

    var login := _ornate_button(frame, "ВОЙТИ ОНЛАЙН", 0.045, 0.59, 0.345, 0.705, 14, "party")
    login.pressed.connect(_account_login)
    var offline := _ornate_button(frame, "ОФЛАЙН • БОТЫ", 0.355, 0.59, 0.645, 0.705, 14, "nav")
    offline.pressed.connect(_account_offline_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.655, 0.59, 0.955, 0.705, 14, "nav")
    register.pressed.connect(_account_register)''', "remember me checkbox")
rep('''    account_status_label.anchor_top = 0.705
    account_status_label.anchor_bottom = 0.79''', '''    account_status_label.anchor_top = 0.72
    account_status_label.anchor_bottom = 0.81''', "status label position")
rep('''    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.20, 0.815, 0.80, 0.92, 14, "nav")''', '''    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.20, 0.835, 0.80, 0.935, 14, "nav")''', "guest button position")
rep('''    account_panel.visible = true
    if account_status_label:''', '''    account_panel.visible = true
    if remember_me_checkbox:
        remember_me_checkbox.button_pressed = remember_me
    if account_status_label:''', "restore checkbox state")
rep('''func _account_guest() -> void:
    if account_token.is_empty():''', '''func _on_remember_me_toggled(pressed: bool) -> void:
    remember_me = pressed
    _save_economy()

func _account_guest() -> void:
    if account_token.is_empty():''', "remember checkbox handler")
rep('''        "account_register", "account_login":
            account_token = str(payload.get("token", ""))''', '''        "account_register", "account_login":
            remember_me = remember_me_checkbox.button_pressed if remember_me_checkbox else remember_me
            account_token = str(payload.get("token", ""))''', "apply remember choice")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v72 board, UI spacing, wallet strip and remember-me patch applied")
