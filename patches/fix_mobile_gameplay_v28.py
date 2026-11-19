from pathlib import Path

root = Path(__file__).resolve().parent.parent
main_path = root / "scripts" / "main.gd"
source = main_path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if old not in source:
        raise SystemExit("Patch anchor not found: " + label)
    source = source.replace(old, new, 1)

replace_once(
'''var game_piece_nodes: Array[Node3D] = []
var selected_game_piece: Node3D''',
'''var game_piece_nodes: Array[Node3D] = []
var turn_highlight_nodes: Array[MeshInstance3D] = []
var selected_game_piece: Node3D''',
"highlight state"
)

replace_once(
'''    camera.position = Vector3(0, 10.5, 12.0)
    camera.look_at(Vector3(0, 0.5, -0.4), Vector3.UP)
    _remember_position()''',
'''    # Wider, higher view keeps all 64 squares and every piece visible on phone screens.
    camera.fov = 54.0
    camera.position = Vector3(0, 15.5, 13.8)
    camera.look_at(Vector3(0, 0.45, -0.4), Vector3.UP)
    _update_turn_highlights()
    _remember_position()''',
"fit full board camera"
)

replace_once(
'''            selected_game_piece = target_piece
            status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + ". Выбери клетку."''',
'''            selected_game_piece = target_piece
            _update_turn_highlights()
            status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + ". Выбери клетку."''',
"highlight selected piece"
)
replace_once(
'''        selected_game_piece = null
        status_label.text = "Выбор отменён."''',
'''        selected_game_piece = null
        _update_turn_highlights()
        status_label.text = "Выбор отменён."''',
"clear selected highlight"
)
replace_once(
'''        selected_game_piece = target_piece
        status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        return''',
'''        selected_game_piece = target_piece
        _update_turn_highlights()
        status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        return''',
"highlight reselection"
)
replace_once(
'''    selected_game_piece = null
    _advance_team_turn()''',
'''    selected_game_piece = null
    _update_turn_highlights()
    _advance_team_turn()''',
"turn button highlight refresh"
)

replace_once(
'''    selected_game_piece = null
    current_team = "white"
    active_teammate = 1''',
'''    selected_game_piece = null
    current_team = "white"
    active_teammate = 1
    for marker in turn_highlight_nodes:
        if is_instance_valid(marker):
            marker.queue_free()
    turn_highlight_nodes.clear()''',
"clear old highlights on reset"
)

replace_once(
'''func _local_team() -> String:
    if not online_active:
        return current_team
    return "white" if multiplayer.is_server() else "black"''',
'''func _local_team() -> String:
    if not online_active:
        return current_team
    return "white" if multiplayer.is_server() else "black"

func _update_turn_highlights() -> void:
    for marker in turn_highlight_nodes:
        if is_instance_valid(marker):
            marker.queue_free()
    turn_highlight_nodes.clear()
    if not is_instance_valid(world_root):
        return
    for piece in game_piece_nodes:
        if not is_instance_valid(piece) or str(piece.get_meta("team")) != current_team:
            continue
        var ring := MeshInstance3D.new()
        var ring_mesh := TorusMesh.new()
        ring_mesh.inner_radius = 0.30
        ring_mesh.outer_radius = 0.39
        ring_mesh.rings = 4
        ring_mesh.ring_segments = 32
        ring.mesh = ring_mesh
        ring.position = piece.position + Vector3(0, -0.035, 0)
        var ring_material := StandardMaterial3D.new()
        ring_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
        ring_material.albedo_color = Color(0.95, 0.72, 0.28, 0.82)
        ring_material.emission_enabled = true
        ring_material.emission = Color(0.62, 0.32, 0.08)
        ring.material_override = ring_material
        world_root.add_child(ring)
        turn_highlight_nodes.append(ring)
    if is_instance_valid(selected_game_piece):
        var selected_ring := MeshInstance3D.new()
        var selected_mesh := TorusMesh.new()
        selected_mesh.inner_radius = 0.40
        selected_mesh.outer_radius = 0.49
        selected_mesh.rings = 4
        selected_mesh.ring_segments = 36
        selected_ring.mesh = selected_mesh
        selected_ring.position = selected_game_piece.position + Vector3(0, -0.015, 0)
        var selected_material := StandardMaterial3D.new()
        selected_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
        selected_material.albedo_color = Color(0.35, 0.95, 0.55, 0.95)
        selected_material.emission_enabled = true
        selected_material.emission = Color(0.10, 0.55, 0.20)
        selected_ring.material_override = selected_material
        world_root.add_child(selected_ring)
        turn_highlight_nodes.append(selected_ring)''',
"add active and selected piece rings"
)

replace_once(
'''    button.add_theme_font_size_override("font_size", font_size)
    button.add_theme_font_override("font", UI_FONT)''',
'''    button.add_theme_font_size_override("font_size", font_size + 2)
    button.add_theme_font_override("font", UI_FONT)''',
"larger bold buttons"
)
replace_once(
'''    label.add_theme_font_size_override("font_size", font_size)
    label.add_theme_font_override("font", UI_LABEL_FONT)
    label.add_theme_color_override("font_color", color)''',
'''    label.add_theme_font_size_override("font_size", font_size + 2)
    label.add_theme_font_override("font", UI_FONT)
    label.add_theme_constant_override("line_spacing", 4)
    label.add_theme_color_override("font_color", color)''',
"larger bold labels"
)

replace_once(
'''    if int(balances["xp"]) < xp_cost:
            prep_status.text = "Недостаточно XP. Нужно ещё %d." % (xp_cost - int(balances["xp"]))''',
'''    if int(balances["xp"]) < xp_cost:
            prep_status.text = "НЕ ХВАТАЕТ ОПЫТА (XP)\\nНужно: %d XP • Есть: %d XP • Не хватает: %d XP." % [xp_cost, int(balances["xp"]), xp_cost - int(balances["xp"])]''',
"xp shortage message"
) if '''    if int(balances["xp"]) < xp_cost:
            prep_status.text = "Недостаточно XP. Нужно ещё %d." % (xp_cost - int(balances["xp"]))''' in source else None

# More explicit economy feedback for both currencies.
source = source.replace(
'''            prep_status.text = "Для открытия нужно %d XP. Сейчас: %d XP." % [int(piece_unlock_xp.get(piece_name, 0)), int(balances["xp"])]''',
'''            var need_xp := int(piece_unlock_xp.get(piece_name, 0))
            var have_xp := int(balances["xp"])
            prep_status.text = "НЕ ХВАТАЕТ XP: нужно %d, есть %d, не хватает %d." % [need_xp, have_xp, maxi(0, need_xp - have_xp)]'''
)
source = source.replace(
'''            prep_status.text = "Фигура открыта. Покупка на одну партию стоит %d злотых." % int(match_piece_costs[piece_name])''',
'''            var need_zloty := int(match_piece_costs[piece_name])
            var have_zloty := int(balances["zloty"])
            prep_status.text = "ПОКУПКА НА ПАРТИЮ: %d ЗЛОТЫХ\\nБаланс: %d • %s" % [need_zloty, have_zloty, ("не хватает " + str(need_zloty - have_zloty)) if have_zloty < need_zloty else "средств достаточно"]'''
)
source = source.replace(
'''            prep_status.text = "Недостаточно XP. Нужно ещё %d." % (xp_cost - int(balances["xp"]))''',
'''            prep_status.text = "НЕ ХВАТАЕТ XP: нужно %d, есть %d, не хватает %d." % [xp_cost, int(balances["xp"]), xp_cost - int(balances["xp"])]'''
)
source = source.replace(
'''        prep_status.text = "Недостаточно злотых. Нужно ещё %d." % (cost - int(balances["zloty"]))''',
'''        prep_status.text = "НЕ ХВАТАЕТ ЗЛОТЫХ: нужно %d, есть %d, не хватает %d." % [cost, int(balances["zloty"]), cost - int(balances["zloty"])]'''
)

main_path.write_text(source, encoding="utf-8")

project_path = root / "project.godot"
project = project_path.read_text(encoding="utf-8")
project = project.replace('window/stretch/mode="canvas_items"', 'window/stretch/mode="canvas_items"\\nwindow/stretch/aspect="expand"')
project_path.write_text(project, encoding="utf-8")
print("CHECKMATE v28 mobile board, turn highlights, economy messages and typography patch applied.")
