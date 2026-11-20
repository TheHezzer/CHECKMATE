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

if "var progression_upgrade_buttons: Dictionary = {}" not in s:
    anchor = "var progression_status_label: Label"
    if anchor not in s:
        raise SystemExit("progression variables anchor missing")
    s = s.replace(anchor, anchor + "\nvar progression_upgrade_buttons: Dictionary = {}\nvar progression_next_card: Control", 1)

build_panel = r'''
func _build_piece_progression_panel() -> void:
    progression_panel = Control.new()
    progression_panel.name = "PieceProgressionWorkshop"
    progression_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    progression_panel.visible = false
    ui.add_child(progression_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.0, 0.0, 0.0, 0.93)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    progression_panel.add_child(shade)

    var frame := _panel(progression_panel, 0.035, 0.055, 0.965, 0.945)
    var title := _add_label(frame, "ИССЛЕДОВАНИЕ ФИГУРЫ", Vector2(20, 12), Vector2(600, 42), 25, PALE_GOLD)
    var close := _ornate_button(frame, "×", 0.925, 0.015, 0.985, 0.105, 18, "nav")
    close.pressed.connect(_close_piece_progression)

    # Connector is deliberately behind both cards: current level at lower-left,
    # next level slightly shifted right and above it.
    var connector := Line2D.new()
    connector.name = "ResearchBranchConnector"
    connector.width = 4.0
    connector.default_color = Color(0.66, 0.48, 0.24, 0.95)
    connector.antialiased = true
    var fw := maxf(frame.size.x, 900.0)
    var fh := maxf(frame.size.y, 560.0)
    connector.points = PackedVector2Array([
        Vector2(fw * 0.605, fh * 0.365),
        Vector2(fw * 0.675, fh * 0.295)
    ])
    frame.add_child(connector)

    # Main research card.
    var main_card := _panel(frame, 0.025, 0.255, 0.635, 0.965)
    main_card.name = "CurrentResearchCard"
    _add_label(main_card, "УРОВЕНЬ 1 • ТЕКУЩИЙ ПЕРСОНАЖ", Vector2(16, 10), Vector2(520, 34), 18, PALE_GOLD)
    progression_piece_label = _add_label(main_card, "ФИГУРА", Vector2(16, 48), Vector2(500, 38), 23, Color(0.94,0.90,0.82))
    progression_stats_label = _add_label(main_card, "", Vector2(18, 92), Vector2(500, 78), 15, Color(0.86,0.84,0.79))
    progression_stats_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    var stat_rows := [
        {"key":"health","title":"ЗДОРОВЬЕ","icon":"♥"},
        {"key":"shield","title":"ЩИТ","icon":"◆"},
        {"key":"damage","title":"АТАКА","icon":"⚔"}
    ]
    progression_upgrade_buttons.clear()
    for i in range(stat_rows.size()):
        var stat: Dictionary = stat_rows[i]
        var y := 0.355 + float(i) * 0.175
        var row := _panel(main_card, 0.035, y, 0.965, y + 0.15)
        var label := _add_label(row, str(stat["icon"]) + "  " + str(stat["title"]), Vector2(12, 4), Vector2(210, 30), 16, PALE_GOLD)
        var detail := _add_label(row, "УРОВЕНЬ 0/5", Vector2(12, 34), Vector2(210, 25), 13, Color(0.82,0.80,0.75))
        detail.name = "Research_" + str(stat["key"]) + "_Detail"
        var upgrade := _ornate_button(row, "УЛУЧШИТЬ", 0.56, 0.12, 0.97, 0.88, 13, "party")
        upgrade.pressed.connect(_upgrade_piece_stat.bind(str(stat["key"])))
        progression_upgrade_buttons[str(stat["key"])] = {"button":upgrade,"detail":detail}

    progression_status_label = _add_label(main_card, "Прокачай три характеристики по 5 ступеней, чтобы открыть следующий уровень.", Vector2(14, 0), Vector2(530, 34), 13, Color(0.92,0.66,0.40))
    progression_status_label.anchor_left = 0.03
    progression_status_label.anchor_right = 0.97
    progression_status_label.anchor_top = 0.895
    progression_status_label.anchor_bottom = 0.99
    progression_status_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    progression_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    progression_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    # Smaller next-level card, positioned above and to the right.
    progression_next_card = _panel(frame, 0.685, 0.115, 0.975, 0.435)
    progression_next_card.name = "LockedNextResearchCard"
    var next_title := _add_label(progression_next_card, "УРОВЕНЬ 2", Vector2(10, 8), Vector2(230, 32), 18, PALE_GOLD)
    var lock := _add_label(progression_next_card, "🔒", Vector2(10, 48), Vector2(230, 70), 48, Color(0.78,0.70,0.52))
    lock.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    var next_desc := _add_label(progression_next_card, "СЛЕДУЮЩИЙ ПЕРСОНАЖ\nОткроется после полного исследования уровня 1", Vector2(12, 125), Vector2(230, 78), 13, Color(0.83,0.80,0.74))
    next_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var next_progress := _add_label(progression_next_card, "0 / 15 улучшений", Vector2(12, 205), Vector2(230, 28), 13, PALE_GOLD)
    next_progress.name = "NextResearchProgress"

    var wallet := _add_label(frame, "ЗЛОТЫЕ  %d     ОПЫТ  %d" % [int(balances["zloty"]), int(balances["xp"])], Vector2(18, 54), Vector2(560, 30), 16, PALE_GOLD)
    wallet.name = "ResearchWalletSummary"
'''

s = replace_func(s, "_build_piece_progression_panel", build_panel)

refresh = r'''
func _refresh_piece_progression() -> void:
    if selected_piece < 0 or selected_piece >= PIECES.size():
        return
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var levels: Dictionary = data.get("levels", {})
    var base := _piece_progress_defaults(piece)
    var health_level := int(levels.get("health", 0))
    var shield_level := int(levels.get("shield", 0))
    var damage_level := int(levels.get("damage", 0))
    var total := health_level + shield_level + damage_level
    progression_piece_label.text = piece.to_upper() + "  •  БАЗОВЫЙ ПЕРСОНАЖ"
    progression_stats_label.text = "ЗДОРОВЬЕ  %d     ЩИТ  %d     АТАКА  %d" % [
        int(base["health"]) + health_level * 20,
        int(base["shield"]) + shield_level * 10,
        int(base["damage"]) + damage_level * 8
    ]
    var stat_base_costs := {
        "health":{"xp":50,"gold":250},
        "shield":{"xp":45,"gold":225},
        "damage":{"xp":55,"gold":275}
    }
    for stat in ["health","shield","damage"]:
        var level := int(levels.get(stat, 0))
        var cost := _piece_upgrade_cost(stat, level)
        var detail: Label = progression_upgrade_buttons[stat]["detail"]
        var button: Button = progression_upgrade_buttons[stat]["button"]
        detail.text = "СТУПЕНЬ %d/5  •  %d XP + %d ЗЛОТЫХ" % [level, int(cost["xp"]), int(cost["gold"])]
        button.text = "МАКСИМУМ" if level >= 5 else "УЛУЧШИТЬ"
        button.disabled = level >= 5
    var next_progress := progression_next_card.find_child("NextResearchProgress", true, false) as Label
    if next_progress:
        next_progress.text = "%d / 15 улучшений" % total
    var unlocked := total >= 15
    progression_next_card.modulate = Color(1,1,1,1) if unlocked else Color(0.72,0.72,0.72,0.92)
    progression_status_label.text = "Уровень 2 открыт — можно переходить к следующему персонажу." if unlocked else "До следующего персонажа: %d из 15 улучшений. Все три характеристики нужно прокачать до 5." % total
    var wallet := progression_panel.find_child("ResearchWalletSummary", true, false) as Label
    if wallet:
        wallet.text = "ЗЛОТЫЕ  %d     ОПЫТ  %d" % [int(balances["zloty"]), int(balances["xp"])]
'''

s = replace_func(s, "_refresh_piece_progression", refresh)

upgrade = r'''
func _upgrade_piece_stat(stat: String, _legacy_xp_cost: int = 0, _legacy_coin_cost: int = 0) -> void:
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var levels: Dictionary = data.get("levels", {})
    var current_level := int(levels.get(stat, 0))
    if current_level >= 5:
        progression_status_label.text = "Эта характеристика уже улучшена до максимума."
        return
    var cost := _piece_upgrade_cost(stat, current_level)
    var xp_required := int(cost["xp"])
    var coins_required := int(cost["gold"])
    if int(balances["xp"]) < xp_required:
        progression_status_label.text = "Не хватает опыта: нужно %d XP." % xp_required
        return
    if int(balances["zloty"]) < coins_required:
        progression_status_label.text = "Не хватает злотых: нужно %d." % coins_required
        return
    balances["xp"] = int(balances["xp"]) - xp_required
    balances["zloty"] = int(balances["zloty"]) - coins_required
    levels[stat] = current_level + 1
    data["levels"] = levels
    piece_progression[piece] = data
    _save_economy()
    progression_status_label.text = "Исследование завершено: " + stat.to_upper()
    _refresh_piece_progression()
'''

s = replace_func(s, "_upgrade_piece_stat", upgrade)

# Count only the three combat stats toward the 15-step next-character requirement.
total_func = r'''
func _piece_total_level(levels: Dictionary) -> int:
    return int(levels.get("health", 0)) + int(levels.get("shield", 0)) + int(levels.get("damage", 0))
'''
s = replace_func(s, "_piece_total_level", total_func)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v79: connected research cards with locked next-level card and three upgrade tracks.")
