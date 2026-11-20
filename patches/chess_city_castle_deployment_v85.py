from pathlib import Path
import re

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# City screen state is stored with the existing economy profile.
if "var city_battle_panel: Control" not in s:
    anchor = "var shop_panel: Control"
    if anchor not in s:
        raise SystemExit("City v85: shop_panel anchor missing")
    s = s.replace(anchor, anchor + """
var city_battle_panel: Control
var city_deploy_panel: Control
var city_castle_level_label: Label
var city_energy_label: Label
var city_army_power_label: Label
var city_deploy_status: Label
var city_piece_buttons: Dictionary = {}
var city_board_cells: Array = []
var city_selected_piece: String = ""
var city_army: Dictionary = {}
var city_state: Dictionary = {}
var city_deploy_visible := false
""", 1)

# Persist city progress and army layout.
anchor = '    cfg.set_value("season", "pass_state", season_pass_state)\n'
if anchor not in s:
    raise SystemExit("City v85: economy save anchor missing")
s = s.replace(anchor, anchor + '    cfg.set_value("city", "state", city_state)\n', 1)
anchor = '        season_pass_state = cfg.get_value("season", "pass_state", season_pass_state)\n'
if anchor not in s:
    raise SystemExit("City v85: economy load anchor missing")
s = s.replace(anchor, anchor + '        city_state = cfg.get_value("city", "state", city_state)\n', 1)

# Create the city battle UI during the normal UI build.
anchor = "    _build_season_pass_screen()\n    _build_onboarding_screen()"
if anchor not in s:
    raise SystemExit("City v85: screen build anchor missing")
s = s.replace(anchor, "    _build_season_pass_screen()\n    _build_city_battle_screen()\n    _build_onboarding_screen()", 1)

# Replace the former city entry point so the city button opens the new castle hub.
start = s.find("func _open_city_screen() -> void:")
if start < 0:
    raise SystemExit("City v85: _open_city_screen not found")
end = s.find("\nfunc ", start + 10)
if end < 0:
    raise SystemExit("City v85: cannot locate end of _open_city_screen")
replacement = """func _open_city_screen() -> void:
    _city_ensure_state()
    if menu_panel:
        menu_panel.visible = false
    if city_battle_panel:
        city_battle_panel.visible = true
    _refresh_city_battle_screen()
"""
s = s[:start] + replacement + s[end:]

city_ui = r'''
func _city_piece_names() -> Array:
    return ["Пешка", "Конь", "Слон", "Ладья", "Ферзь", "Король"]

func _city_ensure_state() -> void:
    var today := Time.get_date_string_from_system()
    if city_state.is_empty():
        city_state = {
            "castle_level":1,
            "energy":150,
            "energy_date":today,
            "army":{},
            "shield_enabled":false
        }
    var last_date := str(city_state.get("energy_date", today))
    if last_date != today:
        city_state["energy"] = 150
        city_state["energy_date"] = today
    city_state["castle_level"] = clampi(int(city_state.get("castle_level", 1)), 1, 5)
    city_state["energy"] = clampi(int(city_state.get("energy", 150)), 0, 150)
    if not (city_state.get("army", {}) is Dictionary):
        city_state["army"] = {}
    city_army = city_state.get("army", {}).duplicate(true)

func _city_save_state() -> void:
    city_state["army"] = city_army.duplicate(true)
    _save_economy()

func _city_army_power() -> int:
    var total := 0
    for key in city_army.keys():
        var piece := str(city_army[key])
        var tier := mini(int(city_state.get("castle_level", 1)), int(_piece_progress_data(piece).get("tier", 1)))
        var stats := _piece_progress_defaults(piece, tier)
        total += int(stats.get("health", 0)) + int(stats.get("damage", 0)) * 3
    return total

func _build_city_battle_screen() -> void:
    city_battle_panel = Control.new()
    city_battle_panel.name = "ChessCityCastleHub"
    city_battle_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    city_battle_panel.visible = false
    ui.add_child(city_battle_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.012, 0.014, 0.018, 0.985)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    city_battle_panel.add_child(shade)

    var frame := _panel(city_battle_panel, 0.025, 0.035, 0.975, 0.965)
    var title := _add_label(frame, "ШАХМАТНЫЙ ГОРОД", Vector2(18, 8), Vector2(520, 42), 25, PALE_GOLD)
    title.add_theme_font_size_override("font_size", 25)
    var back := _ornate_button(frame, "← НАЗАД", 0.82, 0.018, 0.98, 0.105, 12, "nav")
    back.pressed.connect(_close_city_battle_screen)

    city_energy_label = _add_label(frame, "ЭНЕРГИЯ 150 / 150", Vector2(18, 58), Vector2(350, 30), 17, Color(0.76,0.88,0.78))
    city_castle_level_label = _add_label(frame, "ЗАМОК • УРОВЕНЬ 1", Vector2(18, 96), Vector2(500, 34), 20, PALE_GOLD)
    city_army_power_label = _add_label(frame, "СИЛА АРМИИ 0", Vector2(18, 134), Vector2(500, 28), 15, Color(0.84,0.81,0.74))

    var castle := _ornate_button(frame, "ЗАМОК I\nНАЖМИ, ЧТОБЫ РАССТАВИТЬ АРМИЮ", 0.16, 0.25, 0.84, 0.69, 25, "card")
    castle.name = "CityCastleButton"
    castle.add_theme_font_size_override("font_size", 23)
    castle.pressed.connect(_open_city_deployment)

    var upgrade := _ornate_button(frame, "УЛУЧШИТЬ ЗАМОК", 0.20, 0.72, 0.80, 0.82, 15, "nav")
    upgrade.name = "CityCastleUpgradeButton"
    upgrade.pressed.connect(_upgrade_city_castle)

    var attack := _ornate_button(frame, "⚔  НАПАСТЬ  •  10 ЭНЕРГИИ", 0.12, 0.86, 0.88, 0.97, 19, "party")
    attack.name = "CityAttackButton"
    attack.pressed.connect(_city_attack_pressed)

    _build_city_deployment_panel()

func _build_city_deployment_panel() -> void:
    city_deploy_panel = Control.new()
    city_deploy_panel.name = "CityArmyDeployment"
    city_deploy_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    city_deploy_panel.visible = false
    city_battle_panel.add_child(city_deploy_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.008,0.009,0.012,0.985)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    city_deploy_panel.add_child(shade)

    var frame := _panel(city_deploy_panel, 0.015, 0.025, 0.985, 0.975)
    _add_label(frame, "РАССТАНОВКА ОБОРОНЫ", Vector2(12, 6), Vector2(470, 34), 21, PALE_GOLD)
    var back := _ornate_button(frame, "← К ЗАМКУ", 0.80, 0.015, 0.98, 0.095, 11, "nav")
    back.pressed.connect(_close_city_deployment)

    var note := _add_label(frame, "Выбирай фигуру и ставь её на любую свою клетку. Обычная начальная расстановка не обязательна.", Vector2(12, 46), Vector2(850, 42), 13, Color(0.82,0.79,0.72))
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    city_deploy_status = _add_label(frame, "Выбери фигуру снизу, затем свою клетку.", Vector2(12, 91), Vector2(850, 26), 13, Color(0.76,0.88,0.78))

    city_board_cells.clear()
    var board := GridContainer.new()
    board.columns = 8
    board.set_anchors_preset(Control.PRESET_TOP_WIDE)
    board.anchor_left = 0.035
    board.anchor_right = 0.965
    board.anchor_top = 0.17
    board.anchor_bottom = 0.70
    board.offset_top = 0
    board.offset_bottom = 0
    board.add_theme_constant_override("h_separation", 1)
    board.add_theme_constant_override("v_separation", 1)
    board.custom_minimum_size = Vector2(0, 0)
    frame.add_child(board)
    for row in range(8):
        for col in range(8):
            var cell := Button.new()
            cell.custom_minimum_size = Vector2(0, 34)
            cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
            cell.size_flags_vertical = Control.SIZE_EXPAND_FILL
            cell.text = ""
            cell.focus_mode = Control.FOCUS_NONE
            var light := ((row + col) % 2) == 0
            var style := StyleBoxFlat.new()
            style.bg_color = Color(0.60,0.49,0.35) if light else Color(0.20,0.23,0.26)
            style.border_width_left = 1
            style.border_width_top = 1
            style.border_width_right = 1
            style.border_width_bottom = 1
            style.border_color = Color(0.08,0.08,0.08)
            cell.add_theme_stylebox_override("normal", style)
            var hover := style.duplicate() as StyleBoxFlat
            hover.bg_color = Color(0.72,0.60,0.40) if light else Color(0.31,0.35,0.38)
            cell.add_theme_stylebox_override("hover", hover)
            cell.add_theme_font_size_override("font_size", 18)
            cell.set_meta("city_col", col)
            cell.set_meta("city_row", row)
            cell.pressed.connect(_city_deploy_cell_pressed.bind(col, row))
            board.add_child(cell)
            city_board_cells.append(cell)

    var piece_title := _add_label(frame, "ФИГУРЫ ПЕРВОГО УРОВНЯ", Vector2(12, 0), Vector2(600, 25), 14, PALE_GOLD)
    piece_title.anchor_left = 0.035
    piece_title.anchor_right = 0.96
    piece_title.anchor_top = 0.72
    piece_title.anchor_bottom = 0.76
    piece_title.offset_left = 0
    piece_title.offset_right = 0
    piece_title.offset_top = 0
    piece_title.offset_bottom = 0

    city_piece_buttons.clear()
    var names := _city_piece_names()
    for i in range(names.size()):
        var x1 := 0.025 + float(i) * 0.16
        var x2 := x1 + 0.15
        var button := _ornate_button(frame, str(names[i]).to_upper(), x1, 0.77, x2, 0.88, 10, "nav")
        button.pressed.connect(_city_select_deploy_piece.bind(str(names[i])))
        city_piece_buttons[str(names[i])] = button

    var clear := _ornate_button(frame, "УБРАТЬ ФИГУРУ", 0.25, 0.90, 0.75, 0.98, 11, "card")
    clear.pressed.connect(_city_clear_deploy_selection)
    _refresh_city_deployment()

func _open_city_deployment() -> void:
    _city_ensure_state()
    city_selected_piece = ""
    city_battle_panel.visible = false
    city_deploy_panel.visible = true
    _refresh_city_deployment()

func _close_city_deployment() -> void:
    if city_deploy_panel:
        city_deploy_panel.visible = false
    if city_battle_panel:
        city_battle_panel.visible = true
    city_selected_piece = ""
    _refresh_city_battle_screen()

func _city_select_deploy_piece(piece: String) -> void:
    if not _city_piece_names().has(piece):
        return
    city_selected_piece = piece
    if city_deploy_status:
        city_deploy_status.text = "Выбрана фигура: %s. Теперь нажми на свою клетку." % piece.to_upper()
    _refresh_city_deployment()

func _city_deploy_cell_pressed(col: int, row: int) -> void:
    if row < 4:
        city_deploy_status.text = "Это сторона соперника. Расставлять фигуры можно на своих четырёх рядах."
        return
    var key := "%d,%d" % [col,row]
    if city_selected_piece == "":
        if city_army.has(key):
            city_army.erase(key)
            _city_save_state()
            _refresh_city_deployment()
        else:
            city_deploy_status.text = "Сначала выбери фигуру внизу."
        return
    var counts := {}
    for existing in city_army.values():
        counts[str(existing)] = int(counts.get(str(existing),0)) + 1
    var limits := {"Пешка":8,"Конь":2,"Слон":2,"Ладья":2,"Ферзь":1,"Король":1}
    if not city_army.has(key) and int(counts.get(city_selected_piece,0)) >= int(limits.get(city_selected_piece,1)):
        city_deploy_status.text = "Больше фигур этого типа поставить нельзя."
        return
    city_army[key] = city_selected_piece
    _city_save_state()
    city_deploy_status.text = "%s размещена на %s." % [city_selected_piece, "abcdefgh".substr(col, 1) + str(8 - row)]
    _refresh_city_deployment()

func _city_clear_deploy_selection() -> void:
    city_selected_piece = ""
    city_deploy_status.text = "Выбор снят. Нажми на занятую клетку, чтобы убрать фигуру."
    _refresh_city_deployment()

func _refresh_city_deployment() -> void:
    if city_deploy_panel == null:
        return
    var counts := {}
    for cell_key in city_army.keys():
        counts[str(city_army[cell_key])] = int(counts.get(str(city_army[cell_key]),0)) + 1
    for i in range(city_board_cells.size()):
        var cell := city_board_cells[i] as Button
        var col := i % 8
        var row := int(i / 8)
        var key := "%d,%d" % [col,row]
        var piece := str(city_army.get(key, ""))
        cell.text = ""
        if piece != "":
            var glyphs := {"Пешка":"♙","Конь":"♘","Слон":"♗","Ладья":"♖","Ферзь":"♕","Король":"♔"}
            cell.text = str(glyphs.get(piece,"?"))
            cell.add_theme_color_override("font_color", Color(0.98,0.94,0.84))
        else:
            cell.text = "·" if row >= 4 else ""
            cell.add_theme_color_override("font_color", Color(0.45,0.82,0.48))
    for piece in city_piece_buttons.keys():
        var button := city_piece_buttons[piece] as Button
        var tier := mini(int(city_state.get("castle_level",1)), int(_piece_progress_data(str(piece)).get("tier",1)))
        button.text = "%s\n%d/%d • %d" % [str(piece).to_upper(), int(counts.get(str(piece),0)), int({"Пешка":8,"Конь":2,"Слон":2,"Ладья":2,"Ферзь":1,"Король":1}.get(str(piece),1)), tier]
        button.disabled = tier < 1

func _refresh_city_battle_screen() -> void:
    if city_battle_panel == null:
        return
    _city_ensure_state()
    var level := int(city_state.get("castle_level",1))
    var energy := int(city_state.get("energy",150))
    city_energy_label.text = "ЭНЕРГИЯ  %d / 150   •   +150 КАЖДЫЙ ДЕНЬ" % energy
    city_castle_level_label.text = "ЗАМОК • УРОВЕНЬ %d" % level
    city_army_power_label.text = "СИЛА АРМИИ  %d   •   ФИГУР: %d" % [_city_army_power(), city_army.size()]
    var castle := city_battle_panel.find_child("CityCastleButton",true,false) as Button
    if castle:
        castle.text = "ЗАМОК %s\nНАЖМИ, ЧТОБЫ РАССТАВИТЬ АРМИЮ" % ["I","II","III","IV","V"][level-1]
    var upgrade := city_battle_panel.find_child("CityCastleUpgradeButton",true,false) as Button
    if upgrade:
        if level >= 5:
            upgrade.text = "МАКСИМАЛЬНЫЙ УРОВЕНЬ ЗАМКА"
            upgrade.disabled = true
        else:
            var xp_cost := [500,1200,2500,5000][level-1]
            var gold_cost := [1500,3500,7000,14000][level-1]
            upgrade.text = "УЛУЧШИТЬ ЗАМОК ДО %d • %d XP / %d ЗЛОТЫХ" % [level+1,xp_cost,gold_cost]
            upgrade.disabled = false
    var attack := city_battle_panel.find_child("CityAttackButton",true,false) as Button
    if attack:
        attack.disabled = energy < 10 or city_army.is_empty()

func _upgrade_city_castle() -> void:
    _city_ensure_state()
    var level := int(city_state.get("castle_level",1))
    if level >= 5:
        return
    var xp_cost := [500,1200,2500,5000][level-1]
    var gold_cost := [1500,3500,7000,14000][level-1]
    if int(balances.get("xp",0)) < xp_cost or int(balances.get("zloty",0)) < gold_cost:
        _show_notice("Для улучшения замка нужно %d XP и %d злотых." % [xp_cost,gold_cost])
        return
    balances["xp"] = int(balances["xp"]) - xp_cost
    balances["zloty"] = int(balances["zloty"]) - gold_cost
    city_state["castle_level"] = level + 1
    _city_save_state()
    _refresh_wallet_labels()
    _refresh_city_battle_screen()
    _show_notice("Замок улучшен до уровня %d. Теперь доступны фигуры соответствующего уровня, если они исследованы." % (level+1))

func _city_attack_pressed() -> void:
    _city_ensure_state()
    if int(city_state.get("energy",150)) < 10:
        _show_notice("Недостаточно энергии. Каждый день начисляется 150 энергии.")
        return
    if city_army.is_empty():
        _show_notice("Сначала расставь фигуры на доске обороны.")
        return
    _show_notice("Армия готова. Следующий этап — подключение подбора соперника по силе армии, уровню замка и рейтингу. Энергия спишется только при подтверждённом начале партии.")

func _close_city_battle_screen() -> void:
    if city_battle_panel:
        city_battle_panel.visible = false
    if menu_panel:
        menu_panel.visible = true
'''
if "func _build_city_battle_screen() -> void:" not in s:
    s += "\n" + city_ui + "\n"

# Replace only the permanent figure-research stat with regenerating armor.
# Combat shield fields elsewhere remain available for the temporary paid battle add-on.
for function_name in [
    "_build_piece_progression_panel",
    "_piece_progress_defaults",
    "_piece_progress_data",
    "_piece_upgrade_cost",
    "_refresh_piece_progression",
    "_piece_total_level",
    "_upgrade_piece_stat",
    "_unlock_next_piece_tier"
]:
    function_start = s.find("func " + function_name + "(")
    if function_start < 0:
        raise SystemExit("Armor research function missing: " + function_name)
    function_end = s.find("\nfunc ", function_start + 10)
    if function_end < 0:
        function_end = len(s)
    block = s[function_start:function_end]
    block = block.replace('"shield"', '"armor"')
    block = block.replace("ЩИТ", "БРОНЯ")
    block = block.replace("UpgradeShieldButton", "UpgradeArmorButton")
    block = block.replace("10 ЩИТА", "10 БРОНИ")
    s = s[:function_start] + block + s[function_end:]

p.write_text(s, encoding="utf-8")
print("CHECKMATE v85: new Chess City castle hub, persistent daily energy, free-form home-side army deployment, castle progression gates and attack preparation.")
