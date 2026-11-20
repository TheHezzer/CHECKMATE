from pathlib import Path
p=Path(__file__).resolve().parent.parent/"scripts"/"main.gd"
s=p.read_text(encoding="utf-8")
def rep(old,new,label):
    global s
    if old not in s: raise SystemExit("Missing: "+label)
    s=s.replace(old,new,1)

rep("var profile_state_label: Label\n","var profile_state_label: Label\nvar profile_vip_label: Label\nvar profile_login_button: Button\nvar admin_grant_name_input: LineEdit\nvar admin_grant_zloty_input: LineEdit\nvar admin_grant_xp_input: LineEdit\nvar admin_grant_gambits_input: LineEdit\n", "profile and admin fields")

rep('''    var profile := _panel(menu_panel, 0.015, 0.025, 0.225, 0.155)''','''    var profile := _panel(menu_panel, 0.015, 0.025, 0.225, 0.205)''',"profile panel height")
rep('''    profile_name_label = _add_label(profile, "ГОСТЬ", Vector2(92, 8), Vector2(180, 28), 21, PALE_GOLD)
    profile_state_label = _add_label(profile, "ПРОФИЛЬ", Vector2(92, 35), Vector2(180, 22), 15, Color(0.82, 0.82, 0.82))
    var profile_login := _ornate_button(profile, "ВОЙТИ", 0.37, 0.61, 0.96, 0.96, 13, "party")
    profile_login.pressed.connect(_open_account_panel)
    _add_label(profile, "ПРОГРЕСС НА ЭТОМ УСТРОЙСТВЕ", Vector2(92, 61), Vector2(185, 18), 11, Color(0.76, 0.72, 0.66))
    var xp := ProgressBar.new()
    xp.position = Vector2(92, 65)
    xp.size = Vector2(150, 10)
    xp.max_value = 1000
    xp.value = int(balances["xp"])
    xp.show_percentage = false
    profile.add_child(xp)
    _add_label(profile, "850 / 2000", Vector2(92, 77), Vector2(145, 18), 10, PALE_GOLD)''','''    profile_name_label = _add_label(profile, "ГОСТЬ", Vector2(94, 9), Vector2(190, 28), 19, PALE_GOLD)
    profile_state_label = _add_label(profile, "", Vector2(94, 39), Vector2(205, 24), 14, Color(0.86, 0.83, 0.76))
    profile_vip_label = _add_label(profile, "VIP  •  НЕ ПРИОБРЕТЁН", Vector2(94, 67), Vector2(205, 22), 13, Color(0.62, 0.59, 0.54))
    profile_login_button = _ornate_button(profile, "ВОЙТИ", 0.30, 0.72, 0.96, 0.96, 15, "party")
    profile_login_button.pressed.connect(_open_account_panel)''',"clean profile card")
rep('''    var tasks := _panel(menu_panel, 0.015, 0.215, 0.185, 0.365)''','''    var tasks := _panel(menu_panel, 0.015, 0.235, 0.185, 0.375)''',"move left task panel")
rep('''    _add_label(tasks, "Ежедневные\\nзадачи", Vector2(67, 12), Vector2(175, 42), 19, PALE_GOLD)
    _add_label(tasks, "Награды за победы и испытания", Vector2(67, 57), Vector2(175, 32), 12, Color(0.88, 0.82, 0.73))''','''    _add_label(tasks, "ЕЖЕДНЕВНЫЕ ЗАДАЧИ", Vector2(67, 12), Vector2(175, 28), 15, PALE_GOLD)
    _add_label(tasks, "Награды за победы и испытания", Vector2(67, 47), Vector2(175, 38), 10, Color(0.88, 0.82, 0.73))''',"fit daily card text")
rep('''    var pass_panel := _panel(menu_panel, 0.015, 0.385, 0.185, 0.535)''','''    var pass_panel := _panel(menu_panel, 0.015, 0.405, 0.185, 0.545)''',"move pass panel")
rep('''    _add_label(pass_panel, "Боевой\\nпропуск", Vector2(67, 12), Vector2(175, 42), 19, PALE_GOLD)
    _add_label(pass_panel, "Уровень 12  •  Награды сезона", Vector2(67, 57), Vector2(175, 32), 12, Color(0.88, 0.82, 0.73))''','''    _add_label(pass_panel, "БОЕВОЙ ПРОПУСК", Vector2(67, 12), Vector2(175, 28), 15, PALE_GOLD)
    _add_label(pass_panel, "Уровень 12 • Награды сезона", Vector2(67, 47), Vector2(175, 38), 10, Color(0.88, 0.82, 0.73))''',"fit battle pass text")
rep('''    var event_panel := _panel(menu_panel, 0.015, 0.555, 0.185, 0.705)''','''    var event_panel := _panel(menu_panel, 0.015, 0.575, 0.185, 0.735)''',"move event panel")
rep('''    _add_label(event_panel, "Событие\\n«Осенний турнир»", Vector2(67, 10), Vector2(180, 44), 18, PALE_GOLD)
    _add_label(event_panel, "До конца: 7 д. 14 ч.", Vector2(67, 59), Vector2(170, 24), 12, Color(0.88, 0.82, 0.73))''','''    _add_label(event_panel, "СОБЫТИЕ", Vector2(67, 10), Vector2(180, 26), 15, PALE_GOLD)
    _add_label(event_panel, "«Осенний турнир» • до конца 7 д. 14 ч.", Vector2(67, 40), Vector2(170, 42), 10, Color(0.88, 0.82, 0.73))''',"fit event text")

rep('''    for i in range(nav_names.size()):
        var x := 0.012 + float(i) * 0.163
        var b := _ornate_button(menu_panel, nav_icons[i] + "\\n" + nav_names[i], x, 0.905, x + 0.158, 0.998, 16, "nav")''','''    for i in range(nav_names.size()):
        var x := 0.012 + float(i) * 0.163
        var b := _ornate_button(menu_panel, nav_icons[i] + "\\n" + nav_names[i], x, 0.875, x + 0.158, 0.995, 12, "nav")''',"raise bottom navigation")
rep('''            b.text = "🔒\\n" + nav_names[i] + "\\nСКОРО"''','''            b.text = "🔒  " + nav_names[i].to_upper() + "\\nСКОРО"
            b.add_theme_font_size_override("font_size", 13)''',"fit locked nav labels")

rep('''    var party := _ornate_button(menu_panel, "⚔   П А Р Т И Я", 0.365, 0.145, 0.635, 0.255, 26, "party")
    party.pressed.connect(_open_mode_selection)''','''    var party := _ornate_button(menu_panel, "⚔   П А Р Т И Я", 0.365, 0.145, 0.635, 0.255, 26, "party")
    party.pressed.connect(_open_mode_selection)
    var bot_test := _ornate_button(menu_panel, "ИГРА С БОТАМИ • ПРОВЕРКА", 0.385, 0.265, 0.615, 0.325, 13, "nav")
    bot_test.name = "AdminBotTestButton"
    bot_test.visible = developer_mode
    bot_test.pressed.connect(_developer_test_local_game)
    var admin_tools := _ornate_button(menu_panel, "АДМИН-ПАНЕЛЬ", 0.385, 0.335, 0.615, 0.395, 13, "nav")
    admin_tools.name = "AdminToolsButton"
    admin_tools.visible = developer_mode
    admin_tools.pressed.connect(_open_admin_tools)''',"admin buttons on ordinary menu")

rep('''                if account_username.to_lower() == "thehezzer":
                    developer_mode = true
                    if developer_test_menu:
                        developer_test_menu.visible = true
                    if menu_panel:
                        menu_panel.visible = false
                    if developer_test_status:
                        developer_test_status.text = "ГЛАВНЫЙ АДМИНИСТРАТОР • TheHezzer"
                    _show_notice("Добро пожаловать, главный администратор TheHezzer!")''','''                developer_mode = bool(account.get("isAdmin", false))
                if menu_panel:
                    menu_panel.visible = true
                if developer_test_menu:
                    developer_test_menu.visible = false
                _refresh_profile_card()
                if developer_mode:
                    _show_notice("Добро пожаловать, главный администратор!")''',"server-confirmed admin mode")

rep('''func _refresh_profile_card() -> void:
    if profile_name_label:
        profile_name_label.text = account_username if not account_token.is_empty() and not account_username.is_empty() else ("АККАУНТ" if not account_token.is_empty() else "ГОСТЬ")
    if profile_state_label:
        profile_state_label.text = "ПРОГРЕСС СОХРАНЯЕТСЯ" if not account_token.is_empty() else "НАЖМИ НА АВАТАР • ВОЙТИ"
''','''func _refresh_profile_card() -> void:
    var signed_in := not account_token.is_empty() and not account_username.is_empty()
    if profile_name_label:
        profile_name_label.text = account_username if signed_in else "ГОСТЬ"
    if profile_state_label:
        profile_state_label.text = "РЕЙТИНГ  %d  •  %s" % [competitive_rating, _rating_division()] if signed_in else ""
    if profile_login_button:
        profile_login_button.visible = not signed_in
    if profile_vip_label:
        var vip_active := bool(city_profile_data.get("vipActive", false))
        profile_vip_label.text = "VIP  •  АКТИВЕН" if vip_active else "VIP  •  НЕ ПРИОБРЕТЁН"
        profile_vip_label.add_theme_color_override("font_color", PALE_GOLD if vip_active else Color(0.62, 0.59, 0.54))
''',"compact profile and VIP status")

rep('''            account_username = str(account.get("username", "Игрок"))
            if account_token.is_empty() or account_player_id.is_empty():''','''            account_username = str(account.get("username", "Игрок"))
            competitive_rating = int(account.get("rating", competitive_rating))
            if account_token.is_empty() or account_player_id.is_empty():''',"rating from account")
rep('''        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))''','''        "admin_grant":
            _show_notice("Награда начислена игроку " + str(payload.get("username", "")) + ".")
        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))
            _refresh_profile_card()''',"admin grant response")

rep('''func _build_developer_test_menu() -> void:
    developer_test_menu = Control.new()''','''func _build_developer_test_menu() -> void:
    developer_test_menu = Control.new()''',"admin tools builder start")
# Replace the full developer panel builder body up to next function.
start=s.index("func _build_developer_test_menu() -> void:")
end=s.index("func _developer_test_classic() -> void:", start)
new='''func _build_developer_test_menu() -> void:
    developer_test_menu = Control.new()
    developer_test_menu.name = "AdminToolsPanel"
    developer_test_menu.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    developer_test_menu.visible = false
    ui.add_child(developer_test_menu)
    var shade := ColorRect.new()
    shade.color = Color(0.012, 0.010, 0.009, 0.97)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    developer_test_menu.add_child(shade)
    var frame := _panel(developer_test_menu, 0.14, 0.08, 0.86, 0.92)
    _add_label(frame, "АДМИН-ПАНЕЛЬ CHECKMATE", Vector2(24, 16), Vector2(700, 48), 27, PALE_GOLD)
    _add_label(frame, "Играй обычным образом. Здесь доступны тесты и выдача ресурсов игрокам.", Vector2(26, 62), Vector2(760, 34), 14, Color(0.82,0.78,0.70))
    var bot := _ornate_button(frame, "ЗАПУСТИТЬ ИГРУ С БОТАМИ", 0.05, 0.19, 0.48, 0.31, 16, "party")
    bot.pressed.connect(_developer_test_local_game)
    var classic := _ornate_button(frame, "ОНЛАЙН-ТЕСТ КЛАССИКИ", 0.52, 0.19, 0.95, 0.31, 15, "card")
    classic.pressed.connect(_developer_test_classic)
    var voting := _ornate_button(frame, "ТЕСТ КОМАНДНОГО ГОЛОСОВАНИЯ", 0.05, 0.34, 0.48, 0.46, 13, "card")
    voting.pressed.connect(_developer_test_voting)
    _add_label(frame, "НАЧИСЛИТЬ РЕСУРСЫ ИГРОКУ", Vector2(26, 225), Vector2(600, 30), 18, PALE_GOLD)
    admin_grant_name_input = LineEdit.new()
    admin_grant_name_input.position = Vector2(26, 265)
    admin_grant_name_input.size = Vector2(680, 48)
    admin_grant_name_input.placeholder_text = "Точный ник игрока"
    admin_grant_name_input.add_theme_font_size_override("font_size", 20)
    frame.add_child(admin_grant_name_input)
    admin_grant_zloty_input = LineEdit.new()
    admin_grant_zloty_input.position = Vector2(26, 325)
    admin_grant_zloty_input.size = Vector2(205, 48)
    admin_grant_zloty_input.placeholder_text = "Злотые"
    admin_grant_zloty_input.text = "0"
    admin_grant_zloty_input.add_theme_font_size_override("font_size", 19)
    frame.add_child(admin_grant_zloty_input)
    admin_grant_xp_input = LineEdit.new()
    admin_grant_xp_input.position = Vector2(250, 325)
    admin_grant_xp_input.size = Vector2(205, 48)
    admin_grant_xp_input.placeholder_text = "XP"
    admin_grant_xp_input.text = "0"
    admin_grant_xp_input.add_theme_font_size_override("font_size", 19)
    frame.add_child(admin_grant_xp_input)
    admin_grant_gambits_input = LineEdit.new()
    admin_grant_gambits_input.position = Vector2(474, 325)
    admin_grant_gambits_input.size = Vector2(205, 48)
    admin_grant_gambits_input.placeholder_text = "Гамбиты"
    admin_grant_gambits_input.text = "0"
    admin_grant_gambits_input.add_theme_font_size_override("font_size", 19)
    frame.add_child(admin_grant_gambits_input)
    var grant := _ornate_button(frame, "НАЧИСЛИТЬ", 0.05, 0.64, 0.48, 0.76, 17, "party")
    grant.pressed.connect(_admin_grant_resources)
    var close := _ornate_button(frame, "ЗАКРЫТЬ", 0.52, 0.64, 0.95, 0.76, 17, "nav")
    close.pressed.connect(func(): developer_test_menu.visible = false)
    developer_test_status = _add_label(frame, "Выдача ресурсов доступна только серверному администратору.", Vector2(26, 425), Vector2(760, 34), 13, PALE_GOLD)

func _open_admin_tools() -> void:
    if not developer_mode or developer_test_menu == null:
        return
    developer_test_menu.visible = true

func _admin_grant_resources() -> void:
    if not developer_mode:
        return
    var player_name := admin_grant_name_input.text.strip_edges()
    if player_name.is_empty():
        developer_test_status.text = "Укажи точный ник игрока."
        return
    var zloty := int(admin_grant_zloty_input.text) if admin_grant_zloty_input.text.is_valid_int() else 0
    var xp := int(admin_grant_xp_input.text) if admin_grant_xp_input.text.is_valid_int() else 0
    var gambits := int(admin_grant_gambits_input.text) if admin_grant_gambits_input.text.is_valid_int() else 0
    if zloty < 0 or xp < 0 or gambits < 0 or (zloty == 0 and xp == 0 and gambits == 0):
        developer_test_status.text = "Введи положительное количество хотя бы одного ресурса."
        return
    _send_matchmaking_request("admin_grant", "/admin/grant", HTTPClient.METHOD_POST, {"username": player_name, "zloty": zloty, "xp": xp, "gambits": gambits})

'''
s=s[:start]+new+s[end:]
rep('''    developer_test_menu.visible = false
    _start_game(selected_mode)
    status_label.text = "ТЕСТОВЫЙ РЕЖИМ • ЛОКАЛЬНАЯ ПАРТИЯ"''','''    developer_test_menu.visible = false
    if menu_panel: menu_panel.visible = false
    _start_game(selected_mode)
    status_label.text = "ПРОВЕРКА • ЛОКАЛЬНАЯ ПАРТИЯ С БОТАМИ"''',"bot test button action")
rep('''    if menu_panel:
        menu_panel.visible = true
    _show_notice("Вы вышли из тестового режима.")''','''    if menu_panel:
        menu_panel.visible = true
    _refresh_profile_card()
    _show_notice("Админ-панель закрыта.")''',"admin logout returns menu")

p.write_text(s,encoding="utf-8")
print("CHECKMATE v58 UI/admin tools patch applied")
