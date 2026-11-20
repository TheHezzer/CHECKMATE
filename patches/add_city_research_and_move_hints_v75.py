from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# Replace the old four-stat workshop with a three-stat, five-tier research tree.
start = s.index("func _build_piece_progression_panel(")
workshop = r'''func _build_piece_progression_panel() -> void:
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
    var frame := _panel(progression_panel, 0.045, 0.055, 0.955, 0.945)
    var title := _add_label(frame, "ИССЛЕДОВАНИЯ • ШАХМАТНЫЙ ГОРОД", Vector2(20, 12), Vector2(760, 42), 25, PALE_GOLD)
    title.add_theme_font_size_override("font_size", 25)
    progression_piece_label = _add_label(frame, "ПЕШКА • ПЕРСОНАЖ 1/5", Vector2(22, 60), Vector2(720, 38), 21, Color(0.92,0.88,0.80))
    progression_piece_label.add_theme_font_size_override("font_size", 24)
    progression_stats_label = _add_label(frame, "", Vector2(22, 105), Vector2(720, 92), 16, Color(0.86,0.84,0.79))
    progression_stats_label.add_theme_font_size_override("font_size", 18)
    progression_stats_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var stats := [
        {"key":"health","title":"ЗДОРОВЬЕ","name":"UpgradeHealthButton"},
        {"key":"shield","title":"ЩИТ","name":"UpgradeShieldButton"},
        {"key":"damage","title":"АТАКА","name":"UpgradeDamageButton"}
    ]
    for i in range(stats.size()):
        var stat: Dictionary = stats[i]
        var y := 0.345 + float(i) * 0.125
        var button := _ornate_button(frame, str(stat["title"]), 0.035, y, 0.965, y + 0.105, 15, "card")
        button.name = str(stat["name"])
        button.add_theme_font_size_override("font_size", 17)
        button.pressed.connect(_upgrade_piece_stat.bind(str(stat["key"])))
    progression_skin_label = _add_label(frame, "", Vector2(22, 0), Vector2(720, 30), 15, PALE_GOLD)
    progression_skin_label.add_theme_font_size_override("font_size", 17)
    progression_skin_label.anchor_left = 0.04
    progression_skin_label.anchor_right = 0.96
    progression_skin_label.anchor_top = 0.735
    progression_skin_label.anchor_bottom = 0.79
    progression_skin_label.offset_left = 0
    progression_skin_label.offset_right = 0
    progression_skin_label.offset_top = 0
    progression_skin_label.offset_bottom = 0
    progression_skin_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    progression_skin_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    progression_status_label = _add_label(frame, "", Vector2(22, 0), Vector2(720, 28), 14, Color(0.94,0.65,0.42))
    progression_status_label.add_theme_font_size_override("font_size", 16)
    progression_status_label.anchor_left = 0.04
    progression_status_label.anchor_right = 0.96
    progression_status_label.anchor_top = 0.79
    progression_status_label.anchor_bottom = 0.85
    progression_status_label.offset_left = 0
    progression_status_label.offset_right = 0
    progression_status_label.offset_top = 0
    progression_status_label.offset_bottom = 0
    progression_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    progression_status_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    var unlock := _ornate_button(frame, "ОТКРЫТЬ СЛЕДУЮЩЕГО ПЕРСОНАЖА", 0.18, 0.865, 0.82, 0.965, 15, "party")
    unlock.name = "UnlockNextTierButton"
    unlock.add_theme_font_size_override("font_size", 18)
    unlock.pressed.connect(_unlock_next_piece_tier)
    var close := _ornate_button(frame, "×", 0.91, 0.015, 0.975, 0.105, 18, "nav")
    close.pressed.connect(_close_piece_progression)

func _piece_progress_defaults(piece: String, tier: int = 1) -> Dictionary:
    var base := {
        "Пешка":{"health":100,"shield":30,"damage":25},
        "Конь":{"health":125,"shield":40,"damage":35},
        "Слон":{"health":140,"shield":50,"damage":40},
        "Ладья":{"health":160,"shield":65,"damage":45},
        "Ферзь":{"health":190,"shield":70,"damage":55},
        "Король":{"health":220,"shield":80,"damage":50}
    }
    var values: Dictionary = base.get(piece, base["Пешка"]).duplicate(true)
    var bonus := maxi(0, tier - 1)
    values["health"] = int(values["health"]) + bonus * 110
    values["shield"] = int(values["shield"]) + bonus * 55
    values["damage"] = int(values["damage"]) + bonus * 45
    return values

func _piece_progress_data(piece: String) -> Dictionary:
    var data: Dictionary = piece_progression.get(piece, {})
    if data.is_empty():
        data = {"tier":1,"levels":{"health":0,"shield":0,"damage":0}}
    data["tier"] = clampi(int(data.get("tier", 1)), 1, 5)
    var levels: Dictionary = data.get("levels", {})
    for stat in ["health", "shield", "damage"]:
        levels[stat] = clampi(int(levels.get(stat, 0)), 0, 5)
    data["levels"] = levels
    piece_progression[piece] = data
    return data

func _open_piece_progression(piece: String) -> void:
    if not progression_panel:
        return
    selected_piece = PIECES.find(piece)
    if selected_piece < 0:
        selected_piece = 0
    _refresh_main_piece_shelf()
    _refresh_piece_progression()
    progression_panel.visible = true
    if wallet_hud:
        wallet_hud.move_to_front()

func _piece_upgrade_cost(stat: String, rank: int) -> Dictionary:
    var xp_base := 80
    var gold_base := 120
    match stat:
        "shield":
            xp_base = 70
            gold_base = 110
        "damage":
            xp_base = 90
            gold_base = 140
    return {"xp":xp_base * (rank + 1), "gold":gold_base * (rank + 1)}

func _refresh_piece_progression() -> void:
    if not progression_panel or selected_piece < 0 or selected_piece >= PIECES.size():
        return
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var tier := int(data.get("tier", 1))
    var levels: Dictionary = data.get("levels", {})
    var base := _piece_progress_defaults(piece, tier)
    var tier_names := ["ДЕРЕВО", "СТРАЖ", "ВОИН", "РЫЦАРЬ", "ЛЕГЕНДА"]
    progression_piece_label.text = "%s  •  ПЕРСОНАЖ %d/5 — %s" % [piece.to_upper(), tier, tier_names[tier - 1]]
    progression_stats_label.text = "ЗДОРОВЬЕ  %d  (+%d)     ЩИТ  %d  (+%d)\nАТАКА  %d  (+%d)\nУ каждого параметра 5 ступеней. Улучшения действуют только в режиме «Шахматный город»." % [
        int(base["health"]) + int(levels.get("health",0))*20, int(levels.get("health",0))*20,
        int(base["shield"]) + int(levels.get("shield",0))*10, int(levels.get("shield",0))*10,
        int(base["damage"]) + int(levels.get("damage",0))*8, int(levels.get("damage",0))*8
    ]
    var titles := {"health":"ЗДОРОВЬЕ", "shield":"ЩИТ", "damage":"АТАКА"}
    var names := {"health":"UpgradeHealthButton", "shield":"UpgradeShieldButton", "damage":"UpgradeDamageButton"}
    for stat in ["health", "shield", "damage"]:
        var rank := int(levels.get(stat, 0))
        var cost := _piece_upgrade_cost(stat, rank)
        var button := progression_panel.find_child(str(names[stat]), true, false) as Button
        if button:
            var gain := "20 HP" if stat == "health" else ("10 ЩИТА" if stat == "shield" else "8 АТАКИ")
            button.text = ("%s  •  %d/5     +%s     %d XP / %d ЗЛОТЫХ" % [str(titles[stat]), rank, gain, int(cost["xp"]), int(cost["gold"])]) if rank < 5 else "%s  •  5/5  •  МАКСИМУМ" % str(titles[stat])
            button.disabled = rank >= 5
    var total := _piece_total_level(levels)
    progression_skin_label.text = "ПРОГРЕСС ПЕРСОНАЖА: %d/15  •  СЛЕДУЮЩИЙ УРОВЕНЬ ПОСЛЕ 15/15" % total
    var unlock_button := progression_panel.find_child("UnlockNextTierButton", true, false) as Button
    if tier >= 5:
        progression_status_label.text = "Это максимальный, пятый персонаж для данной фигуры."
        if unlock_button:
            unlock_button.text = "МАКСИМАЛЬНЫЙ УРОВЕНЬ"
            unlock_button.disabled = true
    elif total < 15:
        progression_status_label.text = "Сначала доведи здоровье, щит и атаку до 5/5."
        if unlock_button:
            unlock_button.text = "ЗАКРЫТО • НУЖНО 15/15 УЛУЧШЕНИЙ"
            unlock_button.disabled = true
    else:
        var xp_cost := 400 * tier
        var gold_cost := 900 * tier
        progression_status_label.text = "Все характеристики максимальны. Можно открыть более сильного персонажа."
        if unlock_button:
            unlock_button.text = "ОТКРЫТЬ ПЕРСОНАЖ %d • %d XP / %d ЗЛОТЫХ" % [tier + 1, xp_cost, gold_cost]
            unlock_button.disabled = false

func _piece_total_level(levels: Dictionary) -> int:
    return int(levels.get("health",0)) + int(levels.get("shield",0)) + int(levels.get("damage",0))

func _upgrade_piece_stat(stat: String) -> void:
    if not ["health", "shield", "damage"].has(stat):
        return
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var levels: Dictionary = data.get("levels", {})
    var rank := int(levels.get(stat, 0))
    if rank >= 5:
        progression_status_label.text = "Эта характеристика уже улучшена до максимума."
        return
    var cost := _piece_upgrade_cost(stat, rank)
    var xp_required := int(cost["xp"])
    var gold_required := int(cost["gold"])
    if int(balances.get("xp", 0)) < xp_required:
        progression_status_label.text = "НЕ ХВАТАЕТ ОПЫТА: нужно %d XP." % xp_required
        return
    if int(balances.get("zloty", 0)) < gold_required:
        progression_status_label.text = "НЕ ХВАТАЕТ ЗЛОТЫХ: нужно %d." % gold_required
        return
    balances["xp"] = int(balances["xp"]) - xp_required
    balances["zloty"] = int(balances["zloty"]) - gold_required
    levels[stat] = rank + 1
    data["levels"] = levels
    piece_progression[piece] = data
    _save_economy()
    progression_status_label.text = "Улучшение выполнено: " + stat.to_upper()
    _refresh_piece_progression()

func _unlock_next_piece_tier() -> void:
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var tier := int(data.get("tier", 1))
    var levels: Dictionary = data.get("levels", {})
    if tier >= 5 or _piece_total_level(levels) < 15:
        progression_status_label.text = "Сначала полностью исследуй все три характеристики."
        return
    var xp_required := 400 * tier
    var gold_required := 900 * tier
    if int(balances.get("xp", 0)) < xp_required:
        progression_status_label.text = "Для нового персонажа нужно %d XP." % xp_required
        return
    if int(balances.get("zloty", 0)) < gold_required:
        progression_status_label.text = "Для нового персонажа нужно %d злотых." % gold_required
        return
    balances["xp"] = int(balances["xp"]) - xp_required
    balances["zloty"] = int(balances["zloty"]) - gold_required
    data["tier"] = tier + 1
    data["levels"] = {"health":0,"shield":0,"damage":0}
    piece_progression[piece] = data
    _save_economy()
    progression_status_label.text = "Открыт персонаж %d/5 для фигуры %s." % [tier + 1, piece]
    _refresh_piece_progression()

func _close_piece_progression() -> void:
    if progression_panel:
        progression_panel.visible = false'''
s = s[:start] + workshop + "\n"

# Legal destinations: green for empty squares, red for captures.
anchor = '''    if is_instance_valid(selected_game_piece):
        var selected_ring := MeshInstance3D.new()'''
replacement = '''    if is_instance_valid(selected_game_piece) and str(selected_game_piece.get_meta("team")) == current_team:
        _add_legal_move_highlights(selected_game_piece)
    if is_instance_valid(selected_game_piece):
        var selected_ring := MeshInstance3D.new()'''
if anchor not in s:
    raise SystemExit("Missing selected-piece highlight anchor")
s = s.replace(anchor, replacement, 1)

helper = r'''
func _add_legal_move_highlights(piece: Node3D) -> void:
    if not is_instance_valid(piece) or not is_instance_valid(world_root):
        return
    var old_selected := selected_game_piece
    selected_game_piece = piece
    var team := str(piece.get_meta("team"))
    var from_col := int(piece.get_meta("col"))
    var from_row := int(piece.get_meta("row"))
    var kind := str(piece.get_meta("kind"))
    for to_col in range(8):
        for to_row in range(8):
            if to_col == from_col and to_row == from_row:
                continue
            var target := _get_game_piece_at(to_col, to_row)
            if not _is_valid_classic_move(kind, team, from_col, from_row, to_col, to_row, target):
                continue
            if not _move_keeps_king_safe(piece, to_col, to_row, target):
                continue
            var marker := MeshInstance3D.new()
            var mesh := CylinderMesh.new()
            mesh.top_radius = 0.17 if target == null else 0.23
            mesh.bottom_radius = mesh.top_radius
            mesh.height = 0.018
            marker.mesh = mesh
            marker.position = Vector3((to_col - 3.5) * 1.12, 0.615, (to_row - 3.5) * 1.0 - 0.4)
            var material := StandardMaterial3D.new()
            material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
            material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
            material.albedo_color = Color(0.18,0.88,0.42,0.72) if target == null else Color(0.98,0.30,0.20,0.82)
            material.emission_enabled = true
            material.emission = Color(0.06,0.45,0.16) if target == null else Color(0.60,0.08,0.035)
            marker.material_override = material
            world_root.add_child(marker)
            turn_highlight_nodes.append(marker)
    selected_game_piece = old_selected
'''
if "func _add_legal_move_highlights(" not in s:
    anchor = "\nfunc _manual_end_turn() -> void:"
    if anchor not in s:
        raise SystemExit("Missing manual turn insertion point")
    s = s.replace(anchor, "\n" + helper + anchor, 1)

# Bot legality checks now use the actual candidate piece; briefly show the bot's chosen legal moves.
bot_start = s.index("func _make_bot_move() -> void:")
bot_end = s.index("func _build_startup_sequence() -> void:", bot_start)
bot = r'''func _make_bot_move() -> void:
    if not (developer_mode or local_bot_test_active or local_offline_mode_active) or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:
        return
    var candidates: Array[Dictionary] = []
    for piece in game_piece_nodes:
        if not is_instance_valid(piece) or str(piece.get_meta("team")) != current_team:
            continue
        if not standard_chess_mode_active and int(piece.get_meta("owner_slot", 0)) != active_teammate:
            continue
        selected_game_piece = piece
        var fc := int(piece.get_meta("col"))
        var fr := int(piece.get_meta("row"))
        var kind := str(piece.get_meta("kind"))
        for tc in range(8):
            for tr in range(8):
                if fc == tc and fr == tr:
                    continue
                var target := _get_game_piece_at(tc, tr)
                if target != null and str(target.get_meta("team")) == current_team:
                    continue
                if _is_valid_classic_move(kind, current_team, fc, fr, tc, tr, target) and _move_keeps_king_safe(piece, tc, tr, target):
                    candidates.append({"fc":fc,"fr":fr,"tc":tc,"tr":tr})
    selected_game_piece = null
    if candidates.is_empty():
        _advance_team_turn()
        return
    var move: Dictionary = candidates[randi_range(0, candidates.size()-1)]
    selected_game_piece = _get_game_piece_at(int(move["fc"]), int(move["fr"]))
    _update_turn_highlights()
    var bot_name := "Бот"
    for entry in local_bot_roster:
        if str(entry.get("team", "")) == current_team and int(entry.get("slot", -1)) + 1 == active_teammate:
            bot_name = str(entry.get("name", "Бот"))
            break
    status_label.text = "ХОДИТ " + bot_name + " • " + _role_name_for_slot(active_teammate)
    get_tree().create_timer(0.45).timeout.connect(_execute_bot_move.bind(move))

func _execute_bot_move(move: Dictionary) -> void:
    if game_over or not game_panel.visible:
        return
    var piece := _get_game_piece_at(int(move.get("fc", -1)), int(move.get("fr", -1)))
    if piece == null:
        selected_game_piece = null
        _update_turn_highlights()
        return
    _apply_classic_move(int(move["fc"]), int(move["fr"]), int(move["tc"]), int(move["tr"]), false)


'''
s = s[:bot_start] + bot + s[bot_end:]

s = s.replace(
    'var is_my_piece := (developer_mode or local_bot_test_active) and str(piece.get_meta("team")) == local_user_team',
    'var is_my_piece := (developer_mode or local_bot_test_active or local_offline_mode_active) and str(piece.get_meta("team")) == local_user_team',
    1
)
s = s.replace("camera.position = Vector3(0, 14.8, 10.8)", "camera.position = Vector3(0, 15.8, 9.8)", 1)

for old, new in [
    ('task_title.add_theme_font_size_override("font_size", 17)', 'task_title.add_theme_font_size_override("font_size", 18)'),
    ('task_desc.add_theme_font_size_override("font_size", 14)', 'task_desc.add_theme_font_size_override("font_size", 15)'),
    ('pass_title.add_theme_font_size_override("font_size", 17)', 'pass_title.add_theme_font_size_override("font_size", 18)'),
    ('pass_desc.add_theme_font_size_override("font_size", 14)', 'pass_desc.add_theme_font_size_override("font_size", 15)'),
    ('event_title.add_theme_font_size_override("font_size", 17)', 'event_title.add_theme_font_size_override("font_size", 18)'),
    ('event_desc.add_theme_font_size_override("font_size", 14)', 'event_desc.add_theme_font_size_override("font_size", 15)')
]:
    if old not in s:
        raise SystemExit("Missing left card font anchor: " + old)
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v75: City research tree, three stats with five ranks, legal move markers, bot previews and clearer board/menu text.")
