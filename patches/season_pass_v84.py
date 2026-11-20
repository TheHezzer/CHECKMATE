from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# Persistent season-pass state.
if "var season_pass_state: Dictionary = {}" not in s:
    anchor = "var login_streak_state: Dictionary = {}"
    if anchor not in s:
        raise SystemExit("Login streak state anchor missing")
    s = s.replace(anchor, anchor + """
var season_pass_state: Dictionary = {}
var season_pass_panel: Control
var season_pass_progress_label: Label
var season_pass_level_labels: Array = []
var season_pass_free_buttons: Array = []
var season_pass_premium_buttons: Array = []
var season_pass_premium_status: Label
""", 1)

# Save/load the season state with the wallet.
anchor = '    cfg.set_value("daily", "login_streak", login_streak_state)\n'
if anchor not in s:
    raise SystemExit("Season pass save anchor missing")
s = s.replace(anchor, anchor + '    cfg.set_value("season", "pass_state", season_pass_state)\n', 1)
anchor = '        login_streak_state = cfg.get_value("daily", "login_streak", login_streak_state)\n'
if anchor not in s:
    raise SystemExit("Season pass load anchor missing")
s = s.replace(anchor, anchor + '        season_pass_state = cfg.get_value("season", "pass_state", season_pass_state)\n', 1)

# Initialize the season as soon as the profile is loaded.
anchor = '    _login_streak_register_today()\n'
if anchor not in s:
    raise SystemExit("Login streak startup anchor missing")
s = s.replace(anchor, anchor + '    _season_pass_ensure_state()\n', 1)

# Build the pass panel after the daily login panel exists.
anchor = "    _build_login_streak_screen()\n    _build_onboarding_screen()"
if anchor not in s:
    raise SystemExit("Season pass UI build anchor missing")
s = s.replace(anchor, "    _build_login_streak_screen()\n    _build_season_pass_screen()\n    _build_onboarding_screen()", 1)

# Replace the placeholder shop action with a working pass entry.
anchor = '        action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))'
if anchor not in s:
    raise SystemExit("Shop action anchor missing")
s = s.replace(anchor, '''        if str(item["kind"]) == "pass":
            action.text = "ОТКРЫТЬ ПРОПУСК"
            action.pressed.connect(_open_season_pass_screen)
        else:
            action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))''', 1)

pass_ui = r"""
func _season_pass_rewards() -> Array:
    return [
        {"free_gold":100,"free_xp":0,"premium_gold":0,"premium_xp":0,"premium_gambits":0,"skin":""},
        {"free_gold":150,"free_xp":25,"premium_gold":0,"premium_xp":0,"premium_gambits":0,"skin":""},
        {"free_gold":200,"free_xp":0,"premium_gold":0,"premium_xp":50,"premium_gambits":0,"skin":""},
        {"free_gold":150,"free_xp":50,"premium_gold":250,"premium_xp":0,"premium_gambits":0,"skin":""},
        {"free_gold":250,"free_xp":0,"premium_gold":0,"premium_xp":0,"premium_gambits":40,"skin":"Стальной турнир"},
        {"free_gold":200,"free_xp":75,"premium_gold":0,"premium_xp":100,"premium_gambits":0,"skin":""},
        {"free_gold":300,"free_xp":0,"premium_gold":350,"premium_xp":0,"premium_gambits":0,"skin":""},
        {"free_gold":250,"free_xp":100,"premium_gold":0,"premium_xp":0,"premium_gambits":60,"skin":""},
        {"free_gold":350,"free_xp":0,"premium_gold":0,"premium_xp":150,"premium_gambits":0,"skin":""},
        {"free_gold":300,"free_xp":125,"premium_gold":0,"premium_xp":0,"premium_gambits":0,"skin":"Чёрный мрамор"},
        {"free_gold":400,"free_xp":0,"premium_gold":450,"premium_xp":0,"premium_gambits":0,"skin":""},
        {"free_gold":350,"free_xp":150,"premium_gold":0,"premium_xp":200,"premium_gambits":0,"skin":""},
        {"free_gold":450,"free_xp":0,"premium_gold":0,"premium_xp":0,"premium_gambits":80,"skin":""},
        {"free_gold":400,"free_xp":175,"premium_gold":550,"premium_xp":0,"premium_gambits":0,"skin":""},
        {"free_gold":600,"free_xp":250,"premium_gold":0,"premium_xp":0,"premium_gambits":120,"skin":"Королевский обсидиан"}
    ]

func _season_pass_ensure_state() -> void:
    var now := int(Time.get_unix_time_from_system())
    var started := int(season_pass_state.get("started_at", 0))
    if started <= 0 or now - started >= 30 * 86400:
        season_pass_state = {
            "started_at":now,
            "points":0,
            "premium_unlocked":false,
            "claimed_free":[],
            "claimed_premium":[]
        }
    if not (season_pass_state.get("claimed_free", []) is Array):
        season_pass_state["claimed_free"] = []
    if not (season_pass_state.get("claimed_premium", []) is Array):
        season_pass_state["claimed_premium"] = []
    season_pass_state["points"] = clampi(int(season_pass_state.get("points", 0)), 0, 3000)

func _season_pass_add_points(amount: int) -> void:
    _season_pass_ensure_state()
    if amount <= 0:
        return
    season_pass_state["points"] = mini(3000, int(season_pass_state.get("points", 0)) + amount)
    _save_economy()
    _refresh_season_pass_screen()

func _build_season_pass_screen() -> void:
    season_pass_panel = Control.new()
    season_pass_panel.name = "SeasonPassScreen"
    season_pass_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    season_pass_panel.visible = false
    ui.add_child(season_pass_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.98)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    season_pass_panel.add_child(shade)

    var frame := _panel(season_pass_panel, 0.025, 0.035, 0.975, 0.965)
    _add_label(frame, "СЕЗОННЫЙ БОЕВОЙ ПРОПУСК", Vector2(18, 10), Vector2(680, 40), 24, PALE_GOLD)
    var back := _ornate_button(frame, "← В МАГАЗИН", 0.82, 0.02, 0.98, 0.105, 12, "nav")
    back.pressed.connect(_close_season_pass_screen)

    season_pass_progress_label = _add_label(frame, "", Vector2(20, 58), Vector2(720, 30), 16, PALE_GOLD)
    season_pass_premium_status = _add_label(frame, "", Vector2(20, 90), Vector2(720, 28), 13, Color(0.82,0.79,0.72))
    var unlock := _ornate_button(frame, "ОТКРЫТЬ ПРЕМИУМ • 350 ГАМБИТОВ", 0.68, 0.12, 0.98, 0.19, 11, "party")
    unlock.name = "SeasonPassUnlockButton"
    unlock.pressed.connect(_unlock_season_pass_premium)

    season_pass_level_labels.clear()
    season_pass_free_buttons.clear()
    season_pass_premium_buttons.clear()
    var rewards := _season_pass_rewards()
    for i in range(15):
        var col := i % 3
        var row := int(i / 3)
        var x1 := 0.02 + float(col) * 0.325
        var x2 := x1 + 0.305
        var y1 := 0.215 + float(row) * 0.145
        var y2 := y1 + 0.132
        var card := _panel(frame, x1, y1, x2, y2)
        var level := _add_label(card, "УРОВЕНЬ " + str(i + 1), Vector2(8, 4), Vector2(220, 22), 13, PALE_GOLD)
        var reward: Dictionary = rewards[i]
        var free_text := "БЕСПЛАТНО: %d злотых" % int(reward["free_gold"])
        if int(reward["free_xp"]) > 0:
            free_text += " + %d XP" % int(reward["free_xp"])
        var free_label := _add_label(card, free_text, Vector2(8, 28), Vector2(220, 22), 10, Color(0.84,0.87,0.78))
        free_label.clip_text = true
        var premium_text := "ПРЕМИУМ: "
        if str(reward["skin"]) != "":
            premium_text += str(reward["skin"])
        elif int(reward["premium_gambits"]) > 0:
            premium_text += "%d гамбитов" % int(reward["premium_gambits"])
        elif int(reward["premium_gold"]) > 0:
            premium_text += "%d злотых" % int(reward["premium_gold"])
        else:
            premium_text += "%d XP" % int(reward["premium_xp"])
        var premium_label := _add_label(card, premium_text, Vector2(8, 51), Vector2(220, 22), 10, Color(0.85,0.77,0.58))
        premium_label.clip_text = true
        var free_button := _ornate_button(card, "ЗАБРАТЬ", 0.04, 0.69, 0.47, 0.97, 9, "nav")
        free_button.pressed.connect(_claim_season_pass_reward.bind(i + 1, false))
        var premium_button := _ornate_button(card, "ПРЕМИУМ", 0.53, 0.69, 0.96, 0.97, 9, "party")
        premium_button.pressed.connect(_claim_season_pass_reward.bind(i + 1, true))
        season_pass_level_labels.append(level)
        season_pass_free_buttons.append(free_button)
        season_pass_premium_buttons.append(premium_button)

func _open_season_pass_screen() -> void:
    _season_pass_ensure_state()
    if shop_panel:
        shop_panel.visible = false
    if daily_tasks_panel:
        daily_tasks_panel.visible = false
    if login_streak_panel:
        login_streak_panel.visible = false
    if season_pass_panel:
        season_pass_panel.visible = true
    _refresh_season_pass_screen()

func _close_season_pass_screen() -> void:
    if season_pass_panel:
        season_pass_panel.visible = false
    if shop_panel:
        shop_panel.visible = true

func _refresh_season_pass_screen() -> void:
    if season_pass_panel == null:
        return
    _season_pass_ensure_state()
    var points := int(season_pass_state.get("points", 0))
    var level := mini(15, int(points / 200))
    var premium := bool(season_pass_state.get("premium_unlocked", false))
    var claimed_free: Array = season_pass_state.get("claimed_free", [])
    var claimed_premium: Array = season_pass_state.get("claimed_premium", [])
    if season_pass_progress_label:
        season_pass_progress_label.text = "СЕЗОННЫЕ ОЧКИ: %d / 3000     •     УРОВЕНЬ: %d / 15" % [points, level]
    if season_pass_premium_status:
        season_pass_premium_status.text = "ПРЕМИАЛЬНАЯ ДОРОЖКА ОТКРЫТА" if premium else "БЕСПЛАТНАЯ ДОРОЖКА ДОСТУПНА ВСЕМ • ПРЕМИУМ ОТКРЫВАЕТСЯ ЗА 350 ГАМБИТОВ"
    var unlock := season_pass_panel.find_child("SeasonPassUnlockButton", true, false) as Button
    if unlock:
        unlock.text = "ПРЕМИУМ ОТКРЫТ" if premium else "ОТКРЫТЬ ПРЕМИУМ • 350 ГАМБИТОВ"
        unlock.disabled = premium or int(balances["chessmatites"]) < 350
    for i in range(15):
        var required := (i + 1) * 200
        var free_button: Button = season_pass_free_buttons[i]
        var premium_button: Button = season_pass_premium_buttons[i]
        var free_claimed := claimed_free.has(i + 1)
        var premium_claimed := claimed_premium.has(i + 1)
        free_button.text = "ПОЛУЧЕНО" if free_claimed else ("ЗАБРАТЬ" if points >= required else str(required) + " ОЧКОВ")
        free_button.disabled = free_claimed or points < required
        premium_button.text = "ПОЛУЧЕНО" if premium_claimed else ("ЗАБРАТЬ" if points >= required and premium else ("ЗАКРЫТО" if not premium else str(required) + " ОЧКОВ"))
        premium_button.disabled = premium_claimed or not premium or points < required

func _unlock_season_pass_premium() -> void:
    _season_pass_ensure_state()
    if bool(season_pass_state.get("premium_unlocked", false)):
        return
    if int(balances["chessmatites"]) < 350:
        _show_notice("Недостаточно гамбитов. Для премиальной дорожки нужно 350.")
        return
    balances["chessmatites"] = int(balances["chessmatites"]) - 350
    season_pass_state["premium_unlocked"] = true
    _save_economy()
    _refresh_wallet_labels()
    _refresh_season_pass_screen()
    _show_notice("Премиальная дорожка открыта до конца сезона!")

func _claim_season_pass_reward(level: int, premium: bool) -> void:
    _season_pass_ensure_state()
    if level < 1 or level > 15 or int(season_pass_state.get("points", 0)) < level * 200:
        return
    var key := "claimed_premium" if premium else "claimed_free"
    var claimed: Array = season_pass_state.get(key, [])
    if claimed.has(level):
        return
    if premium and not bool(season_pass_state.get("premium_unlocked", false)):
        return
    var rewards := _season_pass_rewards()
    var reward: Dictionary = rewards[level - 1]
    if premium:
        balances["zloty"] = int(balances["zloty"]) + int(reward["premium_gold"])
        balances["xp"] = int(balances["xp"]) + int(reward["premium_xp"])
        balances["chessmatites"] = int(balances["chessmatites"]) + int(reward["premium_gambits"])
        var skin := str(reward["skin"])
        if skin != "":
            if owned_skins.has(skin):
                balances["zloty"] = int(balances["zloty"]) + 900
            else:
                owned_skins.append(skin)
    else:
        balances["zloty"] = int(balances["zloty"]) + int(reward["free_gold"])
        balances["xp"] = int(balances["xp"]) + int(reward["free_xp"])
    claimed.append(level)
    season_pass_state[key] = claimed
    _save_economy()
    _refresh_wallet_labels()
    _refresh_season_pass_screen()
    _show_notice("Награда %s дорожки за уровень %d получена!" % ["премиальной" if premium else "бесплатной", level])

"""
if "func _build_season_pass_screen() -> void:" not in s:
    anchor = "\nfunc _open_city_screen() -> void:"
    if anchor not in s:
        raise SystemExit("Season pass insertion point missing")
    s = s.replace(anchor, "\n" + pass_ui + anchor, 1)

# Award 100 season points for each completed City match, plus 50 for a win.
anchor = '    _daily_record_city_match(winner == local_player_team)\n'
if anchor not in s:
    raise SystemExit("City match reward hook missing")
s = s.replace(anchor, anchor + '        _season_pass_add_points(150 if winner == local_player_team else 100)\n', 1)

# Daily task claims also contribute to season progression.
anchor = '        claimed.append(task_id)\n'
if anchor not in s:
    raise SystemExit("Daily task claim hook missing")
s = s.replace(anchor, anchor + '        _season_pass_add_points(40)\n', 1)

p.write_text(s, encoding="utf-8")
for line_no in range(3008, 3028):
    if line_no <= len(s.splitlines()):
        print("DEBUG %d: %s" % (line_no, s.splitlines()[line_no - 1]))
print("CHECKMATE v84: 30-day season pass, 15 levels, free and premium reward tracks, persistent claims and City match progression.")
