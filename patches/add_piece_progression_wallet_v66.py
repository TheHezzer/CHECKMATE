from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# Persistent per-piece upgrade data.
if 'var piece_progression: Dictionary = {}' not in s:
    s = s.replace('var owned_skins := ["Дерево"]', 'var owned_skins := ["Дерево"]\nvar piece_progression: Dictionary = {}\nvar progression_panel: Control\nvar progression_piece_label: Label\nvar progression_stats_label: Label\nvar progression_status_label: Label\nvar progression_skin_label: Label\nvar wallet_hud: Control\nvar wallet_hud_labels: Dictionary = {}', 1)

# Add an always-visible wallet overlay after all menu/screen controls have been built.
anchor = '''    _build_match_history_screen()
    if not onboarding_completed:
        _open_onboarding()
'''
replacement = '''    _build_match_history_screen()
    _build_wallet_hud()
    _build_piece_progression_panel()
    if not onboarding_completed:
        _open_onboarding()
'''
if anchor not in s:
    raise SystemExit("Could not locate end of _build_ui")
s = s.replace(anchor, replacement, 1)

# Click/tap on the 3D figure opens its progression workshop.
anchor = '''    preview_container.mouse_filter = Control.MOUSE_FILTER_STOP
    preview_container.stretch = true
'''
replacement = '''    preview_container.mouse_filter = Control.MOUSE_FILTER_STOP
    preview_container.stretch = true
    preview_container.gui_input.connect(_on_piece_preview_gui_input)
'''
if anchor not in s:
    raise SystemExit("Could not locate preview input setup")
s = s.replace(anchor, replacement, 1)

# Persist and refresh all wallet displays whenever economy is saved.
anchor = '''    cfg.set_value("progress", "owned_skins", owned_skins)
    cfg.set_value("ranked", "rating", competitive_rating)
'''
replacement = '''    cfg.set_value("progress", "owned_skins", owned_skins)
    cfg.set_value("progress", "piece_progression", piece_progression)
    cfg.set_value("ranked", "rating", competitive_rating)
'''
if anchor not in s:
    raise SystemExit("Could not locate economy save fields")
s = s.replace(anchor, replacement, 1)
anchor = '''    cfg.save("user://checkmate_economy.cfg")
'''
replacement = '''    cfg.save("user://checkmate_economy.cfg")
    _refresh_wallet_hud()
'''
if anchor not in s:
    raise SystemExit("Could not locate economy save end")
s = s.replace(anchor, replacement, 1)
anchor = '''        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)
'''
replacement = '''        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)
        piece_progression = cfg.get_value("progress", "piece_progression", piece_progression)
'''
if anchor not in s:
    raise SystemExit("Could not locate economy load skins")
s = s.replace(anchor, replacement, 1)

addition = r'''

func _build_wallet_hud() -> void:
    wallet_hud = Control.new()
    wallet_hud.name = "PersistentWalletHUD"
    wallet_hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    wallet_hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
    ui.add_child(wallet_hud)
    var strip := PanelContainer.new()
    strip.anchor_left = 0.27
    strip.anchor_right = 0.73
    strip.anchor_top = 0.125
    strip.anchor_bottom = 0.185
    strip.offset_left = 0
    strip.offset_right = 0
    strip.offset_top = 0
    strip.offset_bottom = 0
    strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
    wallet_hud.add_child(strip)
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 8)
    row.mouse_filter = Control.MOUSE_FILTER_IGNORE
    strip.add_child(row)
    for item in [
        {"key":"zloty","title":"ЗЛОТЫЕ","icon":"◈"},
        {"key":"chessmatites","title":"ШАХМАТИТЫ","icon":"◆"},
        {"key":"xp","title":"ОПЫТ","icon":"★"}
    ]:
        var label := Label.new()
        label.name = str(item["key"])
        label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
        label.add_theme_font_override("font", UI_FONT)
        label.add_theme_font_size_override("font_size", 17)
        label.add_theme_color_override("font_color", PALE_GOLD)
        row.add_child(label)
        wallet_hud_labels[str(item["key"])] = label
    _refresh_wallet_hud()

func _refresh_wallet_hud() -> void:
    if wallet_hud_labels.is_empty():
        return
    wallet_hud_labels["zloty"].text = "◈  %s" % _format_wallet_amount(int(balances.get("zloty", 0)))
    wallet_hud_labels["chessmatites"].text = "◆  %s" % _format_wallet_amount(int(balances.get("chessmatites", 0)))
    wallet_hud_labels["xp"].text = "★  %s" % _format_wallet_amount(int(balances.get("xp", 0)))

func _format_wallet_amount(value: int) -> String:
    var raw := str(value)
    var output := ""
    while raw.length() > 3:
        output = " " + raw.substr(raw.length() - 3, 3) + output
        raw = raw.substr(0, raw.length() - 3)
    return raw + output

func _on_piece_preview_gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        _open_piece_progression(PIECES[selected_piece])
        preview_container.accept_event()
    elif event is InputEventScreenTouch and event.pressed:
        _open_piece_progression(PIECES[selected_piece])
        preview_container.accept_event()

func _build_piece_progression_panel() -> void:
    progression_panel = Control.new()
    progression_panel.name = "PieceProgressionWorkshop"
    progression_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    progression_panel.visible = false
    ui.add_child(progression_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.0, 0.0, 0.0, 0.91)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    progression_panel.add_child(shade)
    var frame := _panel(progression_panel, 0.06, 0.08, 0.94, 0.92)
    var title := Label.new()
    title.text = "МАСТЕРСКАЯ ФИГУРЫ"
    title.position = Vector2(20, 12)
    title.size = Vector2(650, 42)
    title.add_theme_font_override("font", UI_FONT)
    title.add_theme_font_size_override("font_size", 27)
    title.add_theme_color_override("font_color", PALE_GOLD)
    frame.add_child(title)
    progression_piece_label = Label.new()
    progression_piece_label.position = Vector2(22, 58)
    progression_piece_label.size = Vector2(700, 40)
    progression_piece_label.add_theme_font_override("font", UI_FONT)
    progression_piece_label.add_theme_font_size_override("font_size", 23)
    progression_piece_label.add_theme_color_override("font_color", Color(0.92,0.88,0.80))
    frame.add_child(progression_piece_label)
    progression_stats_label = Label.new()
    progression_stats_label.position = Vector2(22, 112)
    progression_stats_label.size = Vector2(700, 180)
    progression_stats_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    progression_stats_label.add_theme_font_override("font", UI_FONT)
    progression_stats_label.add_theme_font_size_override("font_size", 18)
    progression_stats_label.add_theme_color_override("font_color", Color(0.86,0.84,0.79))
    frame.add_child(progression_stats_label)
    var stats := [
        {"key":"health","title":"ЗДОРОВЬЕ","xp":80,"coins":120},
        {"key":"shield","title":"ЩИТ","xp":70,"coins":110},
        {"key":"damage","title":"УРОН","xp":90,"coins":140},
        {"key":"regen","title":"ВОССТАНОВЛЕНИЕ","xp":100,"coins":160}
    ]
    for i in range(stats.size()):
        var stat: Dictionary = stats[i]
        var y := 0.40 + float(i) * 0.105
        var button := _ornate_button(frame, str(stat["title"]) + "  +1", 0.035, y, 0.965, y + 0.085, 14, "card")
        button.pressed.connect(_upgrade_piece_stat.bind(str(stat["key"]), int(stat["xp"]), int(stat["coins"])))
    progression_skin_label = Label.new()
    progression_skin_label.anchor_left = 0.04
    progression_skin_label.anchor_right = 0.96
    progression_skin_label.anchor_top = 0.835
    progression_skin_label.anchor_bottom = 0.89
    progression_skin_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    progression_skin_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    progression_skin_label.add_theme_font_override("font", UI_FONT)
    progression_skin_label.add_theme_font_size_override("font_size", 16)
    progression_skin_label.add_theme_color_override("font_color", PALE_GOLD)
    frame.add_child(progression_skin_label)
    var skin := _ornate_button(frame, "ОТКРЫТЬ СКИН ФИГУРЫ", 0.20, 0.895, 0.80, 0.985, 14, "party")
    skin.pressed.connect(_purchase_piece_skin)
    var close := _ornate_button(frame, "×", 0.91, 0.015, 0.975, 0.105, 18, "nav")
    close.pressed.connect(_close_piece_progression)
    progression_status_label = Label.new()
    progression_status_label.anchor_left = 0.04
    progression_status_label.anchor_right = 0.96
    progression_status_label.anchor_top = 0.78
    progression_status_label.anchor_bottom = 0.835
    progression_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    progression_status_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    progression_status_label.add_theme_font_override("font", UI_FONT)
    progression_status_label.add_theme_font_size_override("font_size", 15)
    progression_status_label.add_theme_color_override("font_color", Color(0.94,0.55,0.40))
    frame.add_child(progression_status_label)

func _piece_progress_defaults(piece: String) -> Dictionary:
    var base := {
        "Пешка":{"health":100,"shield":20,"damage":20,"regen":2},
        "Конь":{"health":130,"shield":35,"damage":32,"regen":3},
        "Слон":{"health":145,"shield":45,"damage":34,"regen":3},
        "Ладья":{"health":180,"shield":60,"damage":38,"regen":4},
        "Ферзь":{"health":210,"shield":65,"damage":48,"regen":5},
        "Король":{"health":240,"shield":80,"damage":40,"regen":6}
    }
    return base.get(piece, base["Пешка"]).duplicate(true)

func _piece_progress_data(piece: String) -> Dictionary:
    if not piece_progression.has(piece):
        piece_progression[piece] = {"levels":{"health":0,"shield":0,"damage":0,"regen":0},"skin_level":0}
    return piece_progression[piece]

func _open_piece_progression(piece: String) -> void:
    if not progression_panel:
        return
    selected_piece = PIECES.find(piece)
    _refresh_main_piece_shelf()
    _refresh_piece_progression()
    progression_panel.visible = true
    wallet_hud.move_to_front()

func _refresh_piece_progression() -> void:
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var levels: Dictionary = data.get("levels", {})
    var base := _piece_progress_defaults(piece)
    progression_piece_label.text = piece.to_upper() + "  •  УРОВЕНЬ " + str(_piece_total_level(levels))
    progression_stats_label.text = "ЗДОРОВЬЕ: %d  (+%d)\nЩИТ: %d  (+%d)\nУРОН: %d  (+%d)\nВОССТАНОВЛЕНИЕ: %d  (+%d)\n\nКаждый уровень: опыт открывает улучшение, злотые покупают его." % [
        int(base["health"]) + int(levels.get("health",0))*20, int(levels.get("health",0))*20,
        int(base["shield"]) + int(levels.get("shield",0))*10, int(levels.get("shield",0))*10,
        int(base["damage"]) + int(levels.get("damage",0))*8, int(levels.get("damage",0))*8,
        int(base["regen"]) + int(levels.get("regen",0))*1, int(levels.get("regen",0))
    ]
    progression_skin_label.text = "Скин фигуры: " + ("уровень доступен" if _piece_total_level(levels) >= 3 else "откроется после 3 улучшений")
    progression_status_label.text = "Улучшения: %d XP + %d злотых за уровень характеристики" % [80,120]

func _piece_total_level(levels: Dictionary) -> int:
    var total := 0
    for key in ["health","shield","damage","regen"]:
        total += int(levels.get(key,0))
    return total

func _upgrade_piece_stat(stat: String, xp_cost: int, coin_cost: int) -> void:
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var levels: Dictionary = data.get("levels", {})
    var current_level := int(levels.get(stat,0))
    var xp_required := xp_cost * (current_level + 1)
    var coins_required := coin_cost * (current_level + 1)
    if int(balances["xp"]) < xp_required:
        progression_status_label.text = "НЕ ХВАТАЕТ ОПЫТА: нужно %d XP." % xp_required
        return
    if int(balances["zloty"]) < coins_required:
        progression_status_label.text = "НЕ ХВАТАЕТ ЗЛОТЫХ: нужно %d." % coins_required
        return
    balances["xp"] = int(balances["xp"]) - xp_required
    balances["zloty"] = int(balances["zloty"]) - coins_required
    levels[stat] = current_level + 1
    data["levels"] = levels
    piece_progression[piece] = data
    _save_economy()
    progression_status_label.text = "Улучшение куплено: " + stat.to_upper()
    _refresh_piece_progression()

func _purchase_piece_skin() -> void:
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var levels: Dictionary = data.get("levels", {})
    if _piece_total_level(levels) < 3:
        progression_status_label.text = "Сначала сделай 3 улучшения этой фигуры."
        return
    var skin_key: String = piece + " • Обсидиан"
    if owned_skins.has(skin_key):
        progression_status_label.text = "Этот скин уже открыт."
        return
    if int(balances["xp"]) < 150 or int(balances["zloty"]) < 400:
        progression_status_label.text = "Для скина нужно 150 XP и 400 злотых."
        return
    balances["xp"] = int(balances["xp"]) - 150
    balances["zloty"] = int(balances["zloty"]) - 400
    owned_skins.append(skin_key)
    data["skin_level"] = 1
    piece_progression[piece] = data
    _save_economy()
    progression_status_label.text = "Скин «Обсидиан» открыт навсегда для " + piece + "."
    _refresh_piece_progression()

func _close_piece_progression() -> void:
    if progression_panel:
        progression_panel.visible = false
'''
s += addition
p.write_text(s, encoding="utf-8")
print("CHECKMATE v66 progression workshop and persistent wallet added")
