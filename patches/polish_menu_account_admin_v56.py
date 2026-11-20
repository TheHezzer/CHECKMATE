from pathlib import Path
p=Path(__file__).resolve().parent.parent/"scripts"/"main.gd"
s=p.read_text(encoding="utf-8")
def rep(old,new,label):
 global s
 if old not in s: raise SystemExit("Missing: "+label)
 s=s.replace(old,new,1)

# Main collection: all six pieces are immediately selectable; remove lock/availability language.
rep('''    # Rotatable 3D collectible preview: pawn owned, other chess pieces locked.
    _build_piece_preview()
''','''    # All chess pieces are available from the beginning.
    unlocked_pieces = PIECES.duplicate()
    _build_piece_preview()
''',"piece preview")
rep('''    var piece_name := _add_label(menu_panel, "ПЕШКА  •  ДОСТУПНА",''','''    var piece_name := _add_label(menu_panel, "ПЕШКА",''',"piece title")
rep('''        b.add_theme_font_size_override("font_size", 112)''','''        b.add_theme_font_size_override("font_size", 148)''',"silhouette size")
rep('''        b.tooltip_text = piece_title + (" • доступна" if unlocked_pieces.has(piece_title) else " • закрыта")''','''        b.tooltip_text = piece_title''',"silhouette tooltip")
rep('''        title.text = name.to_upper() + ("  •  🔒" if not unlocked_pieces.has(name) else "")''','''        title.text = name.to_upper()''',"remove lock title")
rep('''        main_piece_buttons[i].tooltip_text = name + (" • доступна" if unlocked else " • закрыта")''','''        main_piece_buttons[i].tooltip_text = name''',"remove availability tooltip")
rep('''        if not unlocked:
            shade = Color(0.37, 0.37, 0.35)
''','''        shade = Color(0.88, 0.86, 0.80) if i == selected_piece else Color(0.68, 0.67, 0.63)
''',"all figures same availability")
# Enlarge central 3D preview via root scale where it is built.
rep('''    preview_container.anchor_left = 0.345
    preview_container.anchor_top = 0.255
    preview_container.anchor_right = 0.655
    preview_container.anchor_bottom = 0.715
''','''    preview_container.anchor_left = 0.315
    preview_container.anchor_top = 0.225
    preview_container.anchor_right = 0.685
    preview_container.anchor_bottom = 0.735
''',"central figure preview size")

# Make portrait clickable and add a distinct enter button on profile card.
rep('''    profile_hit.size = Vector2(245, 94)''','''    profile_hit.size = Vector2(84, 94)''',"portrait hitbox")
rep('''    profile_state_label = _add_label(profile, "НАЖМИ НА АВАТАР • ВОЙТИ", Vector2(92, 38), Vector2(180, 23), 14, Color(0.82, 0.82, 0.82))
''','''    profile_state_label = _add_label(profile, "ПРОФИЛЬ", Vector2(92, 35), Vector2(180, 22), 15, Color(0.82, 0.82, 0.82))
    var profile_login := _ornate_button(profile, "ВОЙТИ", 0.37, 0.61, 0.96, 0.96, 13, "party")
    profile_login.pressed.connect(_open_account_panel)
''',"separate profile login button")

# Centered and larger login/register dialog; larger fields and font.
rep('''    var frame := _panel(account_panel, 0.24, 0.16, 0.76, 0.84)''','''    var frame := _panel(account_panel, 0.17, 0.12, 0.83, 0.88)''',"center account form")
rep('''    _add_label(frame, "АККАУНТ CHECKMATE", Vector2(28, 18), Vector2(590, 44), 26, PALE_GOLD)''','''    var account_title := _add_label(frame, "ДОБРО ПОЖАЛОВАТЬ В CHECKMATE", Vector2(28, 18), Vector2(760, 52), 31, PALE_GOLD)
    account_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER''',"welcome title")
rep('''    account_username_input.position = Vector2(32, 116)
    account_username_input.size = Vector2(540, 46)''','''    account_username_input.position = Vector2(48, 126)
    account_username_input.size = Vector2(700, 64)''',"larger username field")
rep('''    account_username_input.add_theme_font_size_override("font_size", 18)''','''    account_username_input.add_theme_font_size_override("font_size", 27)''',"username font")
rep('''    account_password_input.position = Vector2(32, 176)
    account_password_input.size = Vector2(540, 46)''','''    account_password_input.position = Vector2(48, 210)
    account_password_input.size = Vector2(700, 64)''',"larger password field")
rep('''    account_password_input.add_theme_font_size_override("font_size", 18)''','''    account_password_input.add_theme_font_size_override("font_size", 27)''',"password font")
rep('''    var login := _ornate_button(frame, "ВОЙТИ", 0.045, 0.49, 0.48, 0.61, 15, "party")
    login.pressed.connect(_account_login)
    var register := _ornate_button(frame, "СОЗДАТЬ АККАУНТ", 0.52, 0.49, 0.955, 0.61, 14, "nav")
    register.pressed.connect(_account_register)
    account_status_label = _add_label(frame, "Гостевой режим активен. Прогресс хранится на этом устройстве.", Vector2(32, 278), Vector2(650, 44), 13, PALE_GOLD)
    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.045, 0.70, 0.955, 0.83, 16, "nav")
    guest.pressed.connect(_account_guest)
    var developer := _ornate_button(frame, "ТЕСТ РАЗРАБОТЧИКА", 0.045, 0.86, 0.48, 0.96, 11, "nav")
    developer.pressed.connect(_open_developer_login_from_account)
    var close := _ornate_button(frame, "ЗАКРЫТЬ", 0.52, 0.86, 0.955, 0.96, 11, "nav")
    close.pressed.connect(_close_account_panel)''','''    var login := _ornate_button(frame, "ВОЙТИ", 0.045, 0.43, 0.48, 0.56, 20, "party")
    login.pressed.connect(_account_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.52, 0.43, 0.955, 0.56, 20, "nav")
    register.pressed.connect(_account_register)
    account_status_label = _add_label(frame, "Войди или создай аккаунт, чтобы сохранить прогресс.", Vector2(42, 330), Vector2(740, 58), 18, PALE_GOLD)
    account_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.045, 0.72, 0.955, 0.84, 19, "nav")
    guest.pressed.connect(_account_guest)
    var close := _ornate_button(frame, "ЗАКРЫТЬ", 0.30, 0.88, 0.70, 0.98, 15, "nav")
    close.pressed.connect(_close_account_panel)''',"remove test login button and resize account buttons")

# Make account success greeting central; elevate TheHezzer to master admin after normal account login.
rep('''                var welcome := "Добро пожаловать, " + account_username + "!"
                _set_account_status(welcome + " Загружаем твой прогресс…")
                _show_notice(welcome)
                _close_account_panel()
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
''','''                var welcome := "Добро пожаловать, " + account_username + "!"
                _set_account_status(welcome)
                _show_notice(welcome)
                _close_account_panel()
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
                if account_username.to_lower() == "thehezzer":
                    developer_mode = true
                    if developer_test_menu:
                        developer_test_menu.visible = true
                    if menu_panel:
                        menu_panel.visible = false
                    if developer_test_status:
                        developer_test_status.text = "ГЛАВНЫЙ АДМИНИСТРАТОР • TheHezzer"
                    _show_notice("Добро пожаловать, главный администратор TheHezzer!")
''',"admin account login and greeting")

# Make every menu label and button text globally larger, including splash and in-game UI helpers.
rep('''button.add_theme_font_size_override("font_size", font_size + 8)''','''button.add_theme_font_size_override("font_size", font_size + 13)''',"global button font")
rep('''label.add_theme_font_size_override("font_size", font_size + 7)''','''label.add_theme_font_size_override("font_size", font_size + 11)''',"global label font")

# Remove stale "locked" notice branch in main carousel and always allow all pieces.
rep('''    if selected_piece != 0 and unlocked_pieces.has(piece_name):
        selected_match_piece = piece_name
        _show_notice(piece_name + " выбрана. Нажми «ПАРТИЯ», чтобы продолжить.")
    elif selected_piece != 0:
        _show_notice("🔒 " + piece_name + " пока заблокирована. Открой её в магазине.")
''','''    if selected_piece >= 0:
        selected_match_piece = piece_name
''',"remove selection/locked notices")

p.write_text(s,encoding="utf-8")
print("CHECKMATE v56 menu/account/admin polish applied")
