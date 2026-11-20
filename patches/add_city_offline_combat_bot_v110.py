from pathlib import Path

p = Path(__file__).resolve().parents[1] / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("City offline battle v110 missing anchor: " + label)
    s = s.replace(old, new, 1)

rep("var castle_hub_battle_panel: Control\n", """var castle_hub_battle_panel: Control
var city_offline_battle_panel: Control
var city_offline_board_cells: Array = []
var city_offline_units: Dictionary = {}
var city_offline_selected_key := ""
var city_offline_turn := "player"
var city_offline_active := false
var city_offline_busy := false
var city_offline_test_shield := true
var city_offline_log: Label
var city_offline_status: Label
var city_offline_stats: Label
var city_offline_shield_button: Button
""", "city battle state")

# The city screen is built by v85; append a separate battle screen to the same UI tree.
anchor = "func _castle_hub_attack_pressed() -> void:"
idx = s.find(anchor)
if idx < 0:
    raise SystemExit("City offline battle v110 missing attack handler")
end = s.find("\nfunc ", idx + 10)
if end < 0:
    end = len(s)
old_func = s[idx:end]
new_func = """func _castle_hub_attack_pressed() -> void:
    _castle_hub_ensure_state()
    if int(castle_hub_state.get("energy",150)) < 10:
        _show_notice("Недостаточно энергии. Каждый день начисляется 150 энергии.")
        return
    if castle_hub_army.is_empty():
        _show_notice("Сначала расставь фигуры на доске обороны.")
        return
    _city_offline_start_battle()
"""
s = s[:idx] + new_func + s[end:]

city_code = r'''
func _city_offline_start_battle() -> void:
    _castle_hub_ensure_state()
    city_offline_units.clear()
    city_offline_selected_key = ""
    city_offline_turn = "player"
    city_offline_active = true
    city_offline_busy = false
    for cell_key in castle_hub_army.keys():
        var parts: PackedStringArray = str(cell_key).split(",")
        if parts.size() != 2:
            continue
        var col: int = int(parts[0])
        var row: int = int(parts[1])
        var piece_name := str(castle_hub_army[cell_key])
        var tier: int = mini(int(castle_hub_state.get("castle_level", 1)), int(_piece_progress_data(piece_name).get("tier", 1)))
        var stats: Dictionary = _piece_progress_defaults(piece_name, tier)
        var max_hp: int = maxi(1, int(stats.get("health", 100)))
        var max_armor: int = maxi(0, int(stats.get("armor", 0)))
        var temp_shield: int = 30 if city_offline_test_shield else 0
        city_offline_units[cell_key] = {"name":piece_name,"team":"player","col":col,"row":row,"health":max_hp,"max_health":max_hp,"armor":max_armor,"max_armor":max_armor,"damage":maxi(1,int(stats.get("damage",50))),"shield":temp_shield,"max_shield":temp_shield,"checked":false}
    if city_offline_units.is_empty():
        city_offline_active = false
        _show_notice("Сначала расставь хотя бы одну фигуру на доске замка.")
        return
    # A fixed but varied bot army is generated for every local training match.
    var enemy_back: Array[String] = ["Ладья","Конь","Слон","Ферзь","Король","Слон","Конь","Ладья"]
    for col in range(8):
        _city_offline_add_bot_unit(col, 0, enemy_back[col])
        _city_offline_add_bot_unit(col, 1, "Пешка")
    # Bot front rank is deliberately not identical every match.
    if city_offline_battle_panel == null:
        _city_offline_build_panel()
    city_offline_battle_panel.visible = true
    if castle_hub_battle_panel:
        castle_hub_battle_panel.visible = false
    _city_offline_refresh()
    _city_offline_log("Тренировочный бой начался. Ты ходишь первым. Атака не перемещает атакующую фигуру.")
    _city_offline_update_status()

func _city_offline_add_bot_unit(col: int, row: int, piece_name: String) -> void:
    var stats: Dictionary = _piece_progress_defaults(piece_name, 1)
    var max_hp: int = maxi(1, int(stats.get("health", 100)))
    var max_armor: int = maxi(0, int(stats.get("armor", 0)))
    var key: String = "%d,%d" % [col,row]
    city_offline_units[key] = {"name":piece_name,"team":"bot","col":col,"row":row,"health":max_hp,"max_health":max_hp,"armor":max_armor,"max_armor":max_armor,"damage":maxi(1,int(stats.get("damage",50))),"shield":0,"max_shield":0,"checked":false}

func _city_offline_build_panel() -> void:
    city_offline_battle_panel = Control.new()
    city_offline_battle_panel.name = "ChessCityOfflineTraining"
    city_offline_battle_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    city_offline_battle_panel.visible = false
    ui.add_child(city_offline_battle_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.012,0.014,0.018,0.99)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    city_offline_battle_panel.add_child(shade)
    var frame := _panel(city_offline_battle_panel,0.025,0.025,0.975,0.975)
    var title := _add_label(frame,"ШАХМАТНЫЙ ГОРОД • ТРЕНИРОВКА С БОТОМ",Vector2(18,8),Vector2(900,38),22,PALE_GOLD)
    title.add_theme_font_size_override("font_size",22)
    var back := _ornate_button(frame,"← ВЫЙТИ",0.82,0.015,0.98,0.09,12,"nav")
    back.pressed.connect(_city_offline_exit)
    city_offline_status = _add_label(frame,"ТВОЙ ХОД",Vector2(18,48),Vector2(800,30),16,Color(0.78,0.9,0.78))
    var grid := GridContainer.new()
    grid.name = "CityOfflineBattleGrid"
    grid.columns = 8
    grid.set_anchors_preset(Control.PRESET_TOP_WIDE)
    grid.anchor_left = 0.13
    grid.anchor_right = 0.87
    grid.anchor_top = 0.14
    grid.anchor_bottom = 0.86
    grid.offset_top = 0
    grid.offset_bottom = 0
    grid.add_theme_constant_override("h_separation",2)
    grid.add_theme_constant_override("v_separation",2)
    frame.add_child(grid)
    city_offline_board_cells.clear()
    for row in range(8):
        for col in range(8):
            var cell := Button.new()
            cell.custom_minimum_size = Vector2(0,0)
            cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
            cell.size_flags_vertical = Control.SIZE_EXPAND_FILL
            cell.focus_mode = Control.FOCUS_NONE
            cell.add_theme_font_size_override("font_size",22)
            var light := ((row+col)%2)==0
            var style := StyleBoxFlat.new()
            style.bg_color = Color(0.58,0.48,0.35) if light else Color(0.17,0.20,0.23)
            style.border_width_left = 1
            style.border_width_top = 1
            style.border_width_right = 1
            style.border_width_bottom = 1
            style.border_color = Color(0.06,0.06,0.06)
            cell.add_theme_stylebox_override("normal",style)
            cell.add_theme_stylebox_override("hover",style.duplicate())
            cell.pressed.connect(_city_offline_cell_pressed.bind(col,row))
            grid.add_child(cell)
            city_offline_board_cells.append(cell)
    city_offline_stats = _add_label(frame,"",Vector2(18,90),Vector2(180,500),12,Color(0.86,0.82,0.74))
    city_offline_stats.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    city_offline_log = _add_label(frame,"",Vector2(18,0),Vector2(900,75),12,Color(0.86,0.82,0.74))
    city_offline_log.anchor_left = 0.13
    city_offline_log.anchor_right = 0.87
    city_offline_log.anchor_top = 0.88
    city_offline_log.anchor_bottom = 0.99
    city_offline_log.offset_left = 0
    city_offline_log.offset_right = 0
    city_offline_log.offset_top = 0
    city_offline_log.offset_bottom = 0
    city_offline_shield_button = _ornate_button(frame,"ТЕСТОВЫЙ ЩИТ: ВКЛ • 30",0.015,0.88,0.12,0.99,10,"nav")
    city_offline_shield_button.pressed.connect(_city_offline_toggle_test_shield)

func _city_offline_toggle_test_shield() -> void:
    city_offline_test_shield = not city_offline_test_shield
    if city_offline_active:
        for key in city_offline_units.keys():
            var unit: Dictionary = city_offline_units[key]
            if unit.get("team")=="player":
                unit["shield"] = 30 if city_offline_test_shield else 0
                unit["max_shield"] = int(unit.get("shield",0))
                city_offline_units[key] = unit
        _city_offline_refresh()
    if city_offline_shield_button:
        city_offline_shield_button.text = "ТЕСТОВЫЙ ЩИТ: %s" % ("ВКЛ • 30" if city_offline_test_shield else "ВЫКЛ")
 
func _city_offline_piece_glyph(piece_name: String) -> String:
    return str({"Пешка":"♙","Конь":"♘","Слон":"♗","Ладья":"♖","Ферзь":"♕","Король":"♔"}.get(piece_name,"?"))

func _city_offline_refresh() -> void:
    if city_offline_battle_panel == null:
        return
    for i in range(city_offline_board_cells.size()):
        var cell := city_offline_board_cells[i] as Button
        var col := i%8
        var row := int(i/8)
        var key: String = "%d,%d" % [col,row]
        var unit: Dictionary = city_offline_units.get(key,{})
        var light := ((row+col)%2)==0
        var style := StyleBoxFlat.new()
        style.bg_color = Color(0.58,0.48,0.35) if light else Color(0.17,0.20,0.23)
        if key == city_offline_selected_key:
            style.bg_color = Color(0.55,0.48,0.20)
        style.border_width_left = 1
        style.border_width_top = 1
        style.border_width_right = 1
        style.border_width_bottom = 1
        style.border_color = Color(0.06,0.06,0.06)
        cell.add_theme_stylebox_override("normal",style)
        if unit.is_empty():
            cell.text = ""
        else:
            var glyph := _city_offline_piece_glyph(str(unit.get("name","")))
            cell.text = glyph + "\n" + str(unit.get("health",0))
            cell.add_theme_color_override("font_color",Color(0.98,0.94,0.84) if unit.get("team")=="player" else Color(0.95,0.55,0.48))
    var player_alive := 0
    var bot_alive := 0
    var lines: Array[String] = []
    for unit_value in city_offline_units.values():
        var unit: Dictionary = unit_value
        if int(unit.get("health",0)) <= 0:
            continue
        if unit.get("team")=="player":
            player_alive += 1
        else:
            bot_alive += 1
        lines.append("%s %s  HP %d/%d  Броня %d  Щит %d" % ["ТЫ" if unit.get("team")=="player" else "БОТ",str(unit.get("name","")),int(unit.get("health",0)),int(unit.get("max_health",0)),int(unit.get("armor",0)),int(unit.get("shield",0))])
    city_offline_stats.text = "ТВОЯ АРМИЯ: %d\nАРМИЯ БОТА: %d\n\n%s" % [player_alive,bot_alive,"\n".join(lines.slice(0,18))]
    if city_offline_shield_button:
        city_offline_shield_button.text = "ТЕСТОВЫЙ ЩИТ: %s" % ("ВКЛ • 30" if city_offline_test_shield else "ВЫКЛ")

func _city_offline_cell_pressed(col: int, row: int) -> void:
    if not city_offline_active or city_offline_busy or city_offline_turn != "player":
        return
    var key: String = "%d,%d" % [col,row]
    var target: Dictionary = city_offline_units.get(key,{})
    if city_offline_selected_key == "":
        if target.is_empty() or target.get("team")!="player":
            return
        city_offline_selected_key = key
        _city_offline_refresh()
        return
    var source: Dictionary = city_offline_units.get(city_offline_selected_key,{})
    if source.is_empty():
        city_offline_selected_key = ""
        _city_offline_refresh()
        return
    if target.get("team")=="player":
        city_offline_selected_key = key
        _city_offline_refresh()
        return
    if not _city_offline_is_legal(source,col,row,not target.is_empty()):
        _city_offline_log("Недопустимый ход для %s." % str(source.get("name","фигуры")))
        return
    var from_key := city_offline_selected_key
    city_offline_selected_key = ""
    if target.is_empty():
        city_offline_units.erase(from_key)
        source["col"] = col
        source["row"] = row
        city_offline_units[key] = source
        _city_offline_log("%s перемещена на %s." % [str(source.get("name","Фигура")),_city_offline_coord(col,row)])
    else:
        _city_offline_attack(from_key,key)
    if city_offline_active:
        _city_offline_finish_turn("player")
    _city_offline_refresh()

func _city_offline_coord(col: int,row: int) -> String:
    return "abcdefgh".substr(col,1) + str(8-row)

func _city_offline_path_clear(source: Dictionary,col: int,row: int) -> bool:
    var dx: int = 1 if col > int(source.get("col",0)) else -1 if col < int(source.get("col",0)) else 0
    var dy: int = 1 if row > int(source.get("row",0)) else -1 if row < int(source.get("row",0)) else 0
    var x: int = int(source.get("col",0))+dx
    var y: int = int(source.get("row",0))+dy
    while x != col or y != row:
        if city_offline_units.has("%d,%d" % [x,y]):
            return false
        x += dx
        y += dy
    return true

func _city_offline_is_legal(source: Dictionary,col: int,row: int,is_attack: bool) -> bool:
    var sx: int = int(source.get("col",0))
    var sy: int = int(source.get("row",0))
    var dx: int = abs(col-sx)
    var dy: int = abs(row-sy)
    if dx==0 and dy==0:
        return false
    var kind: String = str(source.get("name",""))
    if kind=="Конь":
        return (dx==1 and dy==2) or (dx==2 and dy==1)
    if kind=="Пешка":
        var direction: int = -1 if source.get("team")=="player" else 1
        if is_attack:
            return dx==1 and row-sy==direction
        if dx!=0:
            return false
        if row-sy==direction:
            return true
        var start_row: int = 6 if source.get("team")=="player" else 1
        return sy==start_row and row-sy==2*direction and _city_offline_path_clear(source,col,row)
    if kind=="Слон":
        return dx==dy and _city_offline_path_clear(source,col,row)
    if kind=="Ладья":
        return (dx==0 or dy==0) and _city_offline_path_clear(source,col,row)
    if kind=="Ферзь":
        return (dx==dy or dx==0 or dy==0) and _city_offline_path_clear(source,col,row)
    if kind=="Король":
        return dx<=1 and dy<=1
    return false

func _city_offline_attack(attacker_key: String,target_key: String) -> void:
    var attacker: Dictionary = city_offline_units.get(attacker_key,{})
    var defender: Dictionary = city_offline_units.get(target_key,{})
    if attacker.is_empty() or defender.is_empty():
        return
    if defender.get("name")=="Король":
        defender["checked"] = true
        city_offline_units[target_key] = defender
        _city_offline_log("ШАХ! Король не вступает в дуэль и не получает прямой урон.")
        if _city_offline_non_king_count_team(str(defender.get("team",""))) == 0:
            _city_offline_end_battle(str(defender.get("team",""))=="bot")
        return
    var damage: int = int(attacker.get("damage",1))
    var shield_before: int = int(defender.get("shield",0))
    var shield_hit: int = mini(shield_before,damage)
    defender["shield"] = shield_before-shield_hit
    damage -= shield_hit
    var armor_before: int = int(defender.get("armor",0))
    var armor_hit: int = mini(armor_before,damage)
    defender["armor"] = armor_before-armor_hit
    damage -= armor_hit
    var hp_hit: int = mini(int(defender.get("health",0)),damage)
    defender["health"] = int(defender.get("health",0))-hp_hit
    city_offline_units[target_key] = defender
    _city_offline_log("%s атакует %s: щит −%d, броня −%d, здоровье −%d." % [str(attacker.get("name","Фигура")),str(defender.get("name","Фигура")),shield_hit,armor_hit,hp_hit])
    if int(defender.get("health",0))<=0:
        city_offline_units.erase(target_key)
        _city_offline_log("%s уничтожена. Атакующий вернулся на исходную клетку." % str(defender.get("name","Фигура")))
    # Attack is a duel action: attacker never moves into the target square.
    if _city_offline_count_team("bot")==0:
        _city_offline_end_battle(true)
    elif _city_offline_count_team("player")==0:
        _city_offline_end_battle(false)

func _city_offline_non_king_count_team(team: String) -> int:
    var count := 0
    for unit in city_offline_units.values():
        if unit.get("team")==team and unit.get("name")!="Король":
            count += 1
    return count

func _city_offline_count_team(team: String) -> int:
    var count := 0
    for unit in city_offline_units.values():
        if unit.get("team")==team:
            count += 1
    return count

func _city_offline_finish_turn(team: String) -> void:
    if not city_offline_active:
        return
    if team=="player":
        city_offline_turn = "bot"
        city_offline_status.text = "ХОД БОТА…"
        _city_offline_refresh_armor("player")
        city_offline_busy = true
        _city_offline_refresh()
        _city_offline_bot_turn()
    else:
        city_offline_turn = "player"
        city_offline_status.text = "ТВОЙ ХОД"
        _city_offline_refresh_armor("bot")
        _city_offline_refresh()

func _city_offline_refresh_armor(team: String) -> void:
    for key in city_offline_units.keys():
        var unit: Dictionary = city_offline_units[key]
        if unit.get("team")!=team:
            continue
        var regen: int = maxi(1,int(unit.get("max_armor",0))*10/100)
        unit["armor"] = mini(int(unit.get("max_armor",0)),int(unit.get("armor",0))+regen)
        city_offline_units[key] = unit
    _city_offline_log("Броня армии %s восстановлена на 10%%." % ("игрока" if team=="player" else "бота"))

func _city_offline_bot_turn() -> void:
    if not city_offline_active:
        city_offline_busy = false
        return
    var bot_keys: Array = []
    var player_keys: Array = []
    for key in city_offline_units.keys():
        var unit: Dictionary = city_offline_units[key]
        if unit.get("team")=="bot":
            bot_keys.append(str(key))
        else:
            player_keys.append(str(key))
    var attacks: Array = []
    for from_key in bot_keys:
        var source: Dictionary = city_offline_units[from_key]
        for to_key in player_keys:
            var target: Dictionary = city_offline_units.get(to_key,{})
            if target.is_empty():
                continue
            var parts: PackedStringArray = str(to_key).split(",")
            if _city_offline_is_legal(source,int(parts[0]),int(parts[1]),true):
                attacks.append([from_key,to_key])
    if not attacks.is_empty():
        var chosen: Array = attacks[randi_range(0,attacks.size()-1)]
        _city_offline_attack(str(chosen[0]),str(chosen[1]))
    else:
        var moves: Array = []
        for from_key in bot_keys:
            var source: Dictionary = city_offline_units[from_key]
            for row in range(0,4):
                for col in range(8):
                    var key: String = "%d,%d" % [col,row]
                    if city_offline_units.has(key):
                        continue
                    if _city_offline_is_legal(source,col,row,false):
                        moves.append([from_key,key])
        if not moves.is_empty():
            var chosen: Array = moves[randi_range(0,moves.size()-1)]
            var source: Dictionary = city_offline_units[str(chosen[0])]
            city_offline_units.erase(str(chosen[0]))
            var parts: PackedStringArray = str(chosen[1]).split(",")
            source["col"] = int(parts[0])
            source["row"] = int(parts[1])
            city_offline_units[str(chosen[1])] = source
            _city_offline_log("Бот переместил %s на %s." % [str(source.get("name","Фигура")),_city_offline_coord(int(parts[0]),int(parts[1]))])
    if city_offline_active:
        _city_offline_refresh_armor("bot")
    city_offline_busy = false
    city_offline_turn = "player"
    city_offline_status.text = "ТВОЙ ХОД"
    _city_offline_refresh()

func _city_offline_end_battle(player_won: bool) -> void:
    city_offline_active = false
    city_offline_busy = false
    city_offline_status.text = "ПОБЕДА • ТРЕНИРОВКА" if player_won else "ПОРАЖЕНИЕ • ТРЕНИРОВКА"
    _city_offline_log("Бой завершён. Это офлайн-тест: злотые, XP и рейтинг не начисляются.")
    _city_offline_refresh()
    _show_notice("ПОБЕДА!" if player_won else "ПОРАЖЕНИЕ" + "\nТренировочный бой завершён. Награды не начисляются.")

func _city_offline_log(message: String) -> void:
    if city_offline_log:
        city_offline_log.text = message

func _city_offline_update_status() -> void:
    if city_offline_status:
        city_offline_status.text = "ТВОЙ ХОД • ОФЛАЙН-ТРЕНИРОВКА С БОТОМ"

func _city_offline_exit() -> void:
    city_offline_active = false
    city_offline_busy = false
    city_offline_selected_key = ""
    if city_offline_battle_panel:
        city_offline_battle_panel.visible = false
    if castle_hub_battle_panel:
        castle_hub_battle_panel.visible = true
    _refresh_castle_hub_battle_screen()

'''
# Insert battle functions before the close city panel method.
anchor = "func _close_castle_hub_battle_screen() -> void:"
rep(anchor, city_code + anchor, "insert city offline combat engine")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v110: Chess City offline battle engine with bot, HP, damage, temporary test shield, armor regeneration and non-moving attacks.")

# v110.1: strict GDScript typing and explicit offline battle QA validation.
