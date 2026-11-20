from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# Persistent seven-day login streak state.
if "var login_streak_state: Dictionary = {}" not in s:
    anchor = "var daily_challenges: Dictionary = {}"
    if anchor not in s:
        raise SystemExit("Daily challenge state anchor missing")
    s = s.replace(anchor, anchor + """
var login_streak_state: Dictionary = {}
var login_streak_panel: Control
var login_streak_day_cards: Array = []
var login_streak_claim_button: Button
var login_streak_status_label: Label
""", 1)

# Save and restore the streak with the existing economy profile.
anchor = '    cfg.set_value("daily", "state", daily_challenges)\n'
if anchor not in s:
    raise SystemExit("Daily state save anchor missing")
s = s.replace(anchor, anchor + '    cfg.set_value("daily", "login_streak", login_streak_state)\n', 1)
anchor = '        daily_challenges = cfg.get_value("daily", "state", daily_challenges)\n'
if anchor not in s:
    raise SystemExit("Daily state load anchor missing")
s = s.replace(anchor, anchor + '        login_streak_state = cfg.get_value("daily", "login_streak", login_streak_state)\n', 1)

# Create the login bonus panel with the daily challenges screen.
anchor = "    _build_daily_tasks_screen()\n    _build_onboarding_screen()"
if anchor not in s:
    raise SystemExit("Daily screen build anchor missing")
s = s.replace(anchor, "    _build_daily_tasks_screen()\n    _build_login_streak_screen()\n    _build_onboarding_screen()", 1)

# Add a clear entry point in the daily tasks screen.
anchor = "    back.pressed.connect(_close_daily_tasks_screen)\n"
if anchor not in s:
    raise SystemExit("Daily screen back button anchor missing")
s = s.replace(anchor, anchor + '''    var streak_button := _ornate_button(frame, "БОНУС ЗА ВХОД", 0.57, 0.025, 0.79, 0.12, 12, "party")
    streak_button.pressed.connect(_open_login_streak_screen)
''', 1)

streak_ui = r"""
func _login_streak_rewards() -> Array:
    return [
        {"gold":100,"xp":0},
        {"gold":150,"xp":0},
        {"gold":200,"xp":50},
        {"gold":250,"xp":75},
        {"gold":350,"xp":100},
        {"gold":450,"xp":150},
        {"gold":700,"xp":250}
    ]

func _login_streak_register_today() -> void:
    var today := Time.get_date_string_from_system()
    var last_login := str(login_streak_state.get("last_login", ""))
    var streak := clampi(int(login_streak_state.get("streak", 0)), 0, 7)
    if last_login == today:
        return
    var yesterday := Time.get_date_string_from_unix_time(int(Time.get_unix_time_from_system()) - 86400)
    if last_login == yesterday and streak > 0 and streak < 7:
        streak += 1
    else:
        streak = 1
    login_streak_state["last_login"] = today
    login_streak_state["streak"] = streak
    _save_economy()

func _build_login_streak_screen() -> void:
    login_streak_panel = Control.new()
    login_streak_panel.name = "LoginStreakScreen"
    login_streak_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    login_streak_panel.visible = false
    ui.add_child(login_streak_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.975)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    login_streak_panel.add_child(shade)

    var frame := _panel(login_streak_panel, 0.035, 0.075, 0.965, 0.925)
    _add_label(frame, "ЕЖЕДНЕВНЫЙ БОНУС", Vector2(20, 16), Vector2(620, 44), 26, PALE_GOLD)
    var back := _ornate_button(frame, "← К ЗАДАНИЯМ", 0.78, 0.025, 0.97, 0.12, 12, "nav")
    back.pressed.connect(_close_login_streak_screen)

    var intro := _add_label(frame, "Заходи каждый день подряд и забирай всё более ценные награды. Пропуск дня сбрасывает серию.", Vector2(22, 70), Vector2(850, 48), 15, Color(0.84,0.81,0.74))
    intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    login_streak_status_label = _add_label(frame, "", Vector2(22, 128), Vector2(850, 34), 17, Color(0.78,0.88,0.72))
    login_streak_day_cards.clear()
    var rewards := _login_streak_rewards()
    for i in range(7):
        var col := i % 4
        var row := int(i / 4)
        var x1 := 0.025 + float(col) * 0.245
        var x2 := x1 + 0.225
        var y1 := 0.235 + float(row) * 0.245
        var y2 := y1 + 0.205
        var card := _panel(frame, x1, y1, x2, y2)
        card.name = "LoginDayCard" + str(i + 1)
        var day_title := _add_label(card, "ДЕНЬ " + str(i + 1), Vector2(8, 8), Vector2(180, 30), 15, PALE_GOLD)
        day_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        var reward: Dictionary = rewards[i]
        var reward_text := "%d ЗЛОТЫХ" % int(reward["gold"])
        if int(reward["xp"]) > 0:
            reward_text += "\n%d XP" % int(reward["xp"])
        var reward_label := _add_label(card, reward_text, Vector2(8, 44), Vector2(180, 48), 15, Color(0.90,0.86,0.78))
        reward_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        reward_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
        var state_label := _add_label(card, "ОЖИДАНИЕ", Vector2(8, 98), Vector2(180, 26), 12, Color(0.70,0.68,0.62))
        state_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        login_streak_day_cards.append({"card":card,"state":state_label})

    login_streak_claim_button = _ornate_button(frame, "ЗАБРАТЬ НАГРАДУ", 0.30, 0.79, 0.70, 0.93, 16, "party")
    login_streak_claim_button.pressed.connect(_claim_login_streak_reward)

func _open_login_streak_screen() -> void:
    _login_streak_register_today()
    if daily_tasks_panel:
        daily_tasks_panel.visible = false
    if shop_panel:
        shop_panel.visible = false
    if login_streak_panel:
        login_streak_panel.visible = true
    _refresh_login_streak_screen()

func _close_login_streak_screen() -> void:
    if login_streak_panel:
        login_streak_panel.visible = false
    if daily_tasks_panel:
        daily_tasks_panel.visible = true
        _refresh_daily_tasks_screen()
    elif shop_panel:
        shop_panel.visible = true

func _refresh_login_streak_screen() -> void:
    if login_streak_panel == null:
        return
    _login_streak_register_today()
    var streak := clampi(int(login_streak_state.get("streak", 1)), 1, 7)
    var today := Time.get_date_string_from_system()
    var claimed := str(login_streak_state.get("claimed_date", "")) == today
    if login_streak_status_label:
        login_streak_status_label.text = "ТЕКУЩАЯ СЕРИЯ: %d ИЗ 7 ДНЕЙ" % streak
    for i in range(login_streak_day_cards.size()):
        var item: Dictionary = login_streak_day_cards[i]
        var state_label: Label = item["state"]
        if i + 1 < streak:
            state_label.text = "ПОЛУЧЕНО"
            state_label.add_theme_color_override("font_color", Color(0.65,0.88,0.62))
        elif i + 1 == streak:
            state_label.text = "ЗАБРАТЬ" if not claimed else "ПОЛУЧЕНО"
            state_label.add_theme_color_override("font_color", PALE_GOLD)
        else:
            state_label.text = "ОЖИДАНИЕ"
            state_label.add_theme_color_override("font_color", Color(0.70,0.68,0.62))
    if login_streak_claim_button:
        login_streak_claim_button.text = "ПОЛУЧЕНО СЕГОДНЯ" if claimed else "ЗАБРАТЬ НАГРАДУ"
        login_streak_claim_button.disabled = claimed

func _claim_login_streak_reward() -> void:
    _login_streak_register_today()
    var today := Time.get_date_string_from_system()
    if str(login_streak_state.get("claimed_date", "")) == today:
        return
    var streak := clampi(int(login_streak_state.get("streak", 1)), 1, 7)
    var rewards := _login_streak_rewards()
    var reward: Dictionary = rewards[streak - 1]
    balances["zloty"] = int(balances["zloty"]) + int(reward["gold"])
    balances["xp"] = int(balances["xp"]) + int(reward["xp"])
    login_streak_state["claimed_date"] = today
    _save_economy()
    _refresh_wallet_labels()
    _refresh_login_streak_screen()
    var message := "Награда за день %d: %d злотых" % [streak, int(reward["gold"])]
    if int(reward["xp"]) > 0:
        message += " и %d XP" % int(reward["xp"])
    _show_notice(message)

"""
if "func _build_login_streak_screen() -> void:" not in s:
    anchor = "\nfunc _open_city_screen() -> void:"
    if anchor not in s:
        raise SystemExit("Login streak functions insertion point missing")
    s = s.replace(anchor, "\n" + streak_ui + anchor, 1)

# Register a login whenever the player opens the daily rewards area.
anchor = "func _open_daily_tasks_screen() -> void:\n"
if anchor not in s:
    raise SystemExit("Daily tasks open function missing")
s = s.replace(anchor, anchor + "    _login_streak_register_today()\n", 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v83: persistent seven-day login streak, daily claim protection and escalating zloty/XP rewards.")
