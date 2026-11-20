from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def replace_func(source: str, name: str, replacement: str) -> str:
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        raise SystemExit("Function not found: " + name)
    next_func = source.find("\nfunc ", start + len(marker))
    if next_func < 0:
        return source[:start] + replacement.rstrip() + "\n"
    return source[:start] + replacement.rstrip() + "\n" + source[next_func + 1:]

# Persistent daily challenge state.
if "var daily_challenges: Dictionary = {}" not in s:
    anchor = "var shop_panel: Control"
    if anchor not in s:
        raise SystemExit("Shop panel variable anchor missing")
    s = s.replace(anchor, anchor + """
var daily_tasks_panel: Control
var daily_challenges: Dictionary = {}
var daily_task_buttons: Dictionary = {}
var daily_task_progress_labels: Dictionary = {}
""", 1)

# Build the daily screen with the rest of the UI.
anchor = "    _build_shop_screen()\n    _build_onboarding_screen()"
if anchor not in s:
    raise SystemExit("Daily screen build anchor missing")
s = s.replace(anchor, "    _build_shop_screen()\n    _build_daily_tasks_screen()\n    _build_onboarding_screen()", 1)

# Persist and restore challenge progress with the existing economy profile.
anchor = '    cfg.set_value("progress", "piece_progression", piece_progression)\n'
if anchor not in s:
    raise SystemExit("Daily save insertion anchor missing")
s = s.replace(anchor, anchor + '    cfg.set_value("daily", "state", daily_challenges)\n', 1)
anchor = '        piece_progression = cfg.get_value("progress", "piece_progression", piece_progression)\n'
if anchor not in s:
    raise SystemExit("Daily load insertion anchor missing")
s = s.replace(anchor, anchor + '        daily_challenges = cfg.get_value("daily", "state", daily_challenges)\n', 1)

# Turn the shop's daily chest card into the entry point for tasks and rewards.
anchor = '        action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))'
if anchor not in s:
    raise SystemExit("Shop daily chest action anchor missing")
s = s.replace(anchor, '''        if str(item["kind"]) == "chest":
            action.text = "ЗАДАНИЯ И СУНДУК"
            action.pressed.connect(_open_daily_tasks_screen)
        else:
            action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))''', 1)

daily_ui = r"""
func _daily_task_definitions() -> Array:
    return [
        {"id":"city_match","title":"ПЕРВАЯ СХВАТКА","description":"Заверши одну партию в режиме «Шахматный город».","target":1,"xp":100,"gold":200},
        {"id":"city_win","title":"ПОБЕДНЫЙ ХОД","description":"Одержи победу в партии «Шахматный город».","target":1,"xp":150,"gold":300},
        {"id":"research","title":"РАЗВИТИЕ АРМИИ","description":"Купи три улучшения характеристик своих фигур.","target":3,"xp":120,"gold":250}
    ]

func _daily_ensure_state() -> void:
    var today := Time.get_date_string_from_system()
    if str(daily_challenges.get("date", "")) != today:
        daily_challenges = {
            "date":today,
            "progress":{"city_match":0,"city_win":0,"research":0},
            "claimed":[],
            "chest_claimed":false
        }
    var progress: Dictionary = daily_challenges.get("progress", {})
    for task in _daily_task_definitions():
        var task_id := str(task["id"])
        progress[task_id] = maxi(0, int(progress.get(task_id, 0)))
    daily_challenges["progress"] = progress
    if not (daily_challenges.get("claimed", []) is Array):
        daily_challenges["claimed"] = []
    daily_challenges["chest_claimed"] = bool(daily_challenges.get("chest_claimed", false))

func _build_daily_tasks_screen() -> void:
    daily_tasks_panel = Control.new()
    daily_tasks_panel.name = "DailyChallengesScreen"
    daily_tasks_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    daily_tasks_panel.visible = false
    ui.add_child(daily_tasks_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.97)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    daily_tasks_panel.add_child(shade)
    var frame := _panel(daily_tasks_panel, 0.035, 0.055, 0.965, 0.945)
    _add_label(frame, "ЕЖЕДНЕВНЫЕ ЗАДАНИЯ", Vector2(20, 12), Vector2(620, 42), 25, PALE_GOLD)
    var back := _ornate_button(frame, "← В МАГАЗИН", 0.80, 0.025, 0.97, 0.12, 13, "nav")
    back.pressed.connect(_close_daily_tasks_screen)
    var wallet := _add_label(frame, "", Vector2(22, 62), Vector2(760, 30), 16, PALE_GOLD)
    wallet.name = "DailyWalletSummary"
    var subtitle := _add_label(frame, "Выполняй задания в Шахматном городе. Прогресс и награды обновляются каждый день.", Vector2(22, 98), Vector2(850, 34), 14, Color(0.82,0.79,0.72))
    subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    daily_task_buttons.clear()
    daily_task_progress_labels.clear()
    var tasks := _daily_task_definitions()
    for i in range(tasks.size()):
        var task: Dictionary = tasks[i]
        var y := 0.205 + float(i) * 0.175
        var row := _panel(frame, 0.025, y, 0.975, y + 0.155)
        _add_label(row, str(task["title"]), Vector2(14, 8), Vector2(430, 28), 16, PALE_GOLD)
        var desc := _add_label(row, str(task["description"]), Vector2(14, 38), Vector2(520, 30), 13, Color(0.84,0.81,0.74))
        desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        var progress := _add_label(row, "", Vector2(14, 72), Vector2(500, 28), 13, Color(0.78,0.88,0.72))
        progress.name = "DailyProgress_" + str(task["id"])
        var claim := _ornate_button(row, "ЗАБРАТЬ", 0.72, 0.22, 0.97, 0.82, 12, "party")
        claim.pressed.connect(_claim_daily_task.bind(str(task["id"])))
        daily_task_buttons[str(task["id"])] = claim
        daily_task_progress_labels[str(task["id"])] = progress
    var chest := _panel(frame, 0.025, 0.755, 0.975, 0.965)
    _add_label(chest, "ЕЖЕДНЕВНЫЙ СУНДУК", Vector2(14, 8), Vector2(420, 30), 18, PALE_GOLD)
    var chest_desc := _add_label(chest, "Открой после получения наград за все три задания. Внутри — злотые, опыт и шанс 2% на редкий постоянный скин.", Vector2(14, 42), Vector2(560, 48), 13, Color(0.84,0.81,0.74))
    chest_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var chest_status := _add_label(chest, "", Vector2(14, 94), Vector2(500, 25), 13, Color(0.78,0.88,0.72))
    chest_status.name = "DailyChestStatus"
    var chest_button := _ornate_button(chest, "ОТКРЫТЬ СУНДУК", 0.70, 0.28, 0.97, 0.82, 13, "party")
    chest_button.name = "DailyChestClaimButton"
    chest_button.pressed.connect(_claim_daily_chest)

func _open_daily_tasks_screen() -> void:
    if daily_tasks_panel == null:
        _build_daily_tasks_screen()
    if shop_panel:
        shop_panel.visible = false
    daily_tasks_panel.visible = true
    _refresh_daily_tasks_screen()

func _close_daily_tasks_screen() -> void:
    if daily_tasks_panel:
        daily_tasks_panel.visible = false
    if shop_panel:
        shop_panel.visible = true

func _refresh_daily_tasks_screen() -> void:
    if daily_tasks_panel == null:
        return
    _daily_ensure_state()
    var wallet := daily_tasks_panel.find_child("DailyWalletSummary", true, false) as Label
    if wallet:
        wallet.text = "ЗЛОТЫЕ  %d       ОПЫТ  %d       ГАМБИТЫ  %d" % [int(balances["zloty"]), int(balances["xp"]), int(balances["chessmatites"])]
    var progress: Dictionary = daily_challenges.get("progress", {})
    var claimed: Array = daily_challenges.get("claimed", [])
    var all_claimed := true
    for task in _daily_task_definitions():
        var task_id := str(task["id"])
        var current := mini(int(progress.get(task_id, 0)), int(task["target"]))
        var target := int(task["target"])
        var is_claimed := claimed.has(task_id)
        var ready := current >= target
        all_claimed = all_claimed and is_claimed
        var progress_label: Label = daily_task_progress_labels[task_id]
        progress_label.text = "ПРОГРЕСС  %d/%d   •   НАГРАДА  %d XP + %d ЗЛОТЫХ" % [current, target, int(task["xp"]), int(task["gold"])]
        var button: Button = daily_task_buttons[task_id]
        button.text = "ПОЛУЧЕНО" if is_claimed else ("ЗАБРАТЬ" if ready else "В ПРОЦЕССЕ")
        button.disabled = is_claimed or not ready
    var chest_status := daily_tasks_panel.find_child("DailyChestStatus", true, false) as Label
    var chest_button := daily_tasks_panel.find_child("DailyChestClaimButton", true, false) as Button
    var chest_claimed := bool(daily_challenges.get("chest_claimed", false))
    if chest_status:
        chest_status.text = "СУНДУК ОТКРЫТ" if chest_claimed else ("ВСЕ ЗАДАНИЯ ВЫПОЛНЕНЫ — СУНДУК ДОСТУПЕН" if all_claimed else "ЗАБЕРИ НАГРАДЫ ЗА ВСЕ 3 ЗАДАНИЯ")
    if chest_button:
        chest_button.text = "ПОЛУЧЕНО" if chest_claimed else "ОТКРЫТЬ СУНДУК"
        chest_button.disabled = chest_claimed or not all_claimed

func _claim_daily_task(task_id: String) -> void:
    _daily_ensure_state()
    var progress: Dictionary = daily_challenges.get("progress", {})
    var claimed: Array = daily_challenges.get("claimed", [])
    for task in _daily_task_definitions():
        if str(task["id"]) != task_id:
            continue
        if claimed.has(task_id) or int(progress.get(task_id, 0)) < int(task["target"]):
            return
        balances["xp"] = int(balances["xp"]) + int(task["xp"])
        balances["zloty"] = int(balances["zloty"]) + int(task["gold"])
        claimed.append(task_id)
        daily_challenges["claimed"] = claimed
        _save_economy()
        _refresh_daily_tasks_screen()
        _show_notice("Задание выполнено! Получено %d XP и %d злотых." % [int(task["xp"]), int(task["gold"])])
        return

func _claim_daily_chest() -> void:
    _daily_ensure_state()
    var claimed: Array = daily_challenges.get("claimed", [])
    if claimed.size() < _daily_task_definitions().size() or bool(daily_challenges.get("chest_claimed", false)):
        return
    balances["zloty"] = int(balances["zloty"]) + 500
    balances["xp"] = int(balances["xp"]) + 250
    var message := "В сундуке: 500 злотых и 250 XP."
    var rng := RandomNumberGenerator.new()
    rng.randomize()
    if rng.randi_range(1, 100) <= 2:
        var rare_skin := "Лунное серебро"
        if owned_skins.has(rare_skin):
            balances["zloty"] = int(balances["zloty"]) + 900
            message += "\nРедкий скин уже есть — вместо него начислено 900 злотых."
        else:
            owned_skins.append(rare_skin)
            message += "\nРЕДКАЯ НАГРАДА: навсегда открыт скин «Лунное серебро»!"
    daily_challenges["chest_claimed"] = true
    _save_economy()
    _refresh_daily_tasks_screen()
    _show_notice(message)

func _daily_record_city_match(won: bool) -> void:
    _daily_ensure_state()
    var progress: Dictionary = daily_challenges.get("progress", {})
    progress["city_match"] = mini(1, int(progress.get("city_match", 0)) + 1)
    if won:
        progress["city_win"] = mini(1, int(progress.get("city_win", 0)) + 1)
    daily_challenges["progress"] = progress
    _save_economy()
    _refresh_daily_tasks_screen()

func _daily_record_research_upgrade() -> void:
    _daily_ensure_state()
    var progress: Dictionary = daily_challenges.get("progress", {})
    progress["research"] = mini(3, int(progress.get("research", 0)) + 1)
    daily_challenges["progress"] = progress
    _save_economy()
    _refresh_daily_tasks_screen()

"""
if "func _build_daily_tasks_screen() -> void:" not in s:
    anchor = "\nfunc _open_city_screen() -> void:"
    if anchor not in s:
        raise SystemExit("Daily screen insertion point missing")
    s = s.replace(anchor, "\n" + daily_ui + anchor, 1)

# Record completed matches only in Chess City; ordinary classic chess stays separate.
result_anchor = '    var winner := str(data.get("winnerTeam", ""))\n'
if result_anchor not in s:
    raise SystemExit("Match result winner anchor missing")
s = s.replace(result_anchor, result_anchor + '''    var active_mode := str(selected_mode).to_lower()
    if active_mode.contains("город") or active_mode.contains("city"):
        _daily_record_city_match(winner == local_player_team)
''', 1)

# Count only successful research purchases.
upgrade_start = s.find("func _upgrade_piece_stat(")
if upgrade_start < 0:
    raise SystemExit("Research upgrade function missing")
upgrade_end = s.find("\nfunc ", upgrade_start + 1)
if upgrade_end < 0:
    upgrade_end = len(s)
upgrade_func = s[upgrade_start:upgrade_end]
save_anchor = "    _save_economy()\n    progression_status_label.text"
if save_anchor not in upgrade_func:
    raise SystemExit("Research upgrade completion anchor missing")
upgrade_func = upgrade_func.replace(save_anchor, "    _save_economy()\n    _daily_record_research_upgrade()\n    progression_status_label.text", 1)
s = s[:upgrade_start] + upgrade_func + s[upgrade_end:]

p.write_text(s, encoding="utf-8")
print("CHECKMATE v82: daily Chess City tasks, persistent progress, claimable rewards and once-a-day chest with rare skin chance.")
