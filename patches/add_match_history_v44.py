from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "scripts" / "main.gd"
s = path.read_text(encoding="utf-8")

def once(old: str, new: str, label: str) -> None:
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one match, found {n}")
    s = s.replace(old, new, 1)

once(
'''var match_result_votes: Label
var prep_piece_buttons: Array[Button] = []''',
'''var match_result_votes: Label
var match_history_panel: Control
var match_history_text: Label
var history_return_to_menu := false
var prep_piece_buttons: Array[Button] = []''',
"history references")

once(
'''    _build_onboarding_screen()
    _build_match_result_screen()
    if not onboarding_completed:''',
'''    _build_onboarding_screen()
    _build_match_result_screen()
    _build_match_history_screen()
    if not onboarding_completed:''',
"history screen initialization")

once(
'''    var back := _ornate_button(frame, "ВЕРНУТЬСЯ В МЕНЮ", 0.34, 0.88, 0.66, 0.98, 16, "party")
    back.pressed.connect(_return_to_menu)

func _show_match_result_screen(data: Dictionary) -> void:''',
'''    var replay := _ornate_button(frame, "ЕЩЁ ПАРТИЮ", 0.035, 0.88, 0.32, 0.98, 13, "party")
    replay.pressed.connect(_play_again_from_results)
    var history := _ornate_button(frame, "ИСТОРИЯ", 0.36, 0.88, 0.64, 0.98, 13, "nav")
    history.pressed.connect(_open_match_history.bind(false))
    var back := _ornate_button(frame, "В МЕНЮ", 0.68, 0.88, 0.965, 0.98, 13, "card")
    back.pressed.connect(_return_to_menu)

func _build_match_history_screen() -> void:
    match_history_panel = Control.new()
    match_history_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    match_history_panel.visible = false
    ui.add_child(match_history_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.006, 0.005, 0.96)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    match_history_panel.add_child(shade)
    var frame := _panel(match_history_panel, 0.07, 0.06, 0.93, 0.94)
    _add_label(frame, "ИСТОРИЯ ПАРТИЙ", Vector2(24, 16), Vector2(620, 44), 27, PALE_GOLD)
    _add_label(frame, "ПОСЛЕДНИЕ 10 ЗАВЕРШЁННЫХ МАТЧЕЙ НА ЭТОМ УСТРОЙСТВЕ", Vector2(26, 62), Vector2(650, 26), 12, Color(0.82, 0.75, 0.63))
    match_history_text = _add_label(frame, "Здесь пока нет завершённых партий.", Vector2(28, 108), Vector2(700, 360), 15, Color(0.90, 0.85, 0.76))
    match_history_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var close := _ornate_button(frame, "НАЗАД", 0.36, 0.88, 0.64, 0.98, 15, "party")
    close.pressed.connect(_close_match_history)

func _open_match_history(from_menu: bool = false) -> void:
    history_return_to_menu = from_menu
    if menu_panel:
        menu_panel.visible = false
    if match_result_panel:
        match_result_panel.visible = false
    match_history_panel.visible = true
    _refresh_match_history()

func _close_match_history() -> void:
    match_history_panel.visible = false
    if history_return_to_menu:
        menu_panel.visible = true
    elif match_result_panel:
        match_result_panel.visible = true

func _refresh_match_history() -> void:
    var cfg := ConfigFile.new()
    var entries: Array = []
    if cfg.load("user://checkmate_match_history.cfg") == OK:
        entries = cfg.get_value("history", "matches", [])
    if entries.is_empty():
        match_history_text.text = "Здесь пока нет завершённых партий.\\nСыграй первую партию — её результат появится в этой истории."
        return
    var lines: Array[String] = []
    for i in range(entries.size()):
        var item: Dictionary = entries[i]
        var number := i + 1
        lines.append("%02d. %s  •  %s  •  %s\\n     +%d злотых  |  +%d XP  |  %s" % [number, str(item.get("date", "")), str(item.get("mode", "Классика")), str(item.get("result", "ЗАВЕРШЕНА")), int(item.get("zloty", 0)), int(item.get("xp", 0)), str(item.get("finish", ""))])
    match_history_text.text = "\\n\\n".join(lines)

func _record_match_history(data: Dictionary, headline: String, reward: Dictionary) -> void:
    var cfg := ConfigFile.new()
    var entries: Array = []
    if cfg.load("user://checkmate_match_history.cfg") == OK:
        entries = cfg.get_value("history", "matches", [])
    var finish := str(data.get("result", "finished"))
    var item := {
        "date": Time.get_datetime_string_from_system(false, true),
        "mode": selected_mode,
        "result": headline,
        "finish": finish,
        "zloty": int(reward.get("zloty", 0)),
        "xp": int(reward.get("xp", 0))
    }
    entries.push_front(item)
    if entries.size() > 10:
        entries.resize(10)
    cfg.set_value("history", "matches", entries)
    cfg.save("user://checkmate_match_history.cfg")

func _play_again_from_results() -> void:
    match_result_panel.visible = false
    selected_mode = "Классика"
    _open_preparation()

func _show_match_result_screen(data: Dictionary) -> void:''',
"history and replay UI")

once(
'''    if selected_mode != "Командное голосование":
        match_result_votes.text = "Обычная классическая партия — голосование в этом матче не использовалось."
    elif vote_count < 3 or vote_accuracy < 75:
        match_result_votes.text += "\\nУсловие бонуса: минимум 3 голоса и точность от 75%."
    game_panel.visible = false''',
'''    if selected_mode != "Командное голосование":
        match_result_votes.text = "Обычная классическая партия — голосование в этом матче не использовалось."
    elif vote_count < 3 or vote_accuracy < 75:
        match_result_votes.text += "\\nУсловие бонуса: минимум 3 голоса и точность от 75%."
    _record_match_history(data, headline, reward)
    game_panel.visible = false''',
"record result in history")

once(
'''    var quick_names := ["Уведомления", "Рейтинг", "Кланы", "Настройки"]
    var quick_icons := ["♟", "🏆", "♟", "⚙"]''',
'''    var quick_names := ["История", "Рейтинг", "Кланы", "Настройки"]
    var quick_icons := ["◷", "🏆", "♟", "⚙"]''',
"menu history shortcut")

once(
'''        if quick_names[i] == "Рейтинг":
            q.text = quick_icons[i] + "\\nРейтинг\\n%d • %s" % [competitive_rating, _rating_division()]
            q.pressed.connect(_show_rating_details)
        else:
            q.pressed.connect(_show_notice.bind(quick_names[i] + " — раздел в разработке"))''',
'''        if quick_names[i] == "Рейтинг":
            q.text = quick_icons[i] + "\\nРейтинг\\n%d • %s" % [competitive_rating, _rating_division()]
            q.pressed.connect(_show_rating_details)
        elif quick_names[i] == "История":
            q.pressed.connect(_open_match_history.bind(true))
        else:
            q.pressed.connect(_show_notice.bind(quick_names[i] + " — раздел в разработке"))''',
"connect menu history shortcut")

once(
'''    if match_result_panel:
        match_result_panel.visible = false
    menu_panel.visible = true''',
'''    if match_result_panel:
        match_result_panel.visible = false
    if match_history_panel:
        match_history_panel.visible = false
    menu_panel.visible = true''',
"hide history on menu return")

path.write_text(s, encoding="utf-8")
print("CHECKMATE v44 match history and replay flow applied")
