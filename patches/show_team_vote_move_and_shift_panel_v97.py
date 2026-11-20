from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v97 anchor: " + label)
    s = s.replace(old, new, 1)

rep("var team_vote_side_label: Label\n", "var team_vote_side_label: Label\nvar pending_vote_visual_nodes: Array[Node3D] = []\n", "vote visual refs")

rep("""    vote_approve_button = _ornate_button(game_panel, "ЗА  •  ПОДДЕРЖАТЬ", 0.27, 0.88, 0.49, 0.98, 13, "party")
    vote_approve_button.visible = false
    vote_approve_button.pressed.connect(_cast_team_vote.bind("approve"))
    vote_reject_button = _ornate_button(game_panel, "ПРОТИВ  •  ОТКЛОНИТЬ", 0.51, 0.88, 0.73, 0.98, 13, "nav")
    vote_reject_button.visible = false
    vote_reject_button.pressed.connect(_cast_team_vote.bind("reject"))
    team_vote_side_panel = _panel(game_panel, 0.765, 0.31, 0.985, 0.79)""", """    vote_approve_button = _ornate_button(game_panel, "ЗА  •  ПОДДЕРЖАТЬ", 0.82, 0.73, 0.99, 0.82, 12, "party")
    vote_approve_button.visible = false
    vote_approve_button.pressed.connect(_cast_team_vote.bind("approve"))
    vote_reject_button = _ornate_button(game_panel, "ПРОТИВ  •  ОТКЛОНИТЬ", 0.82, 0.84, 0.99, 0.93, 12, "nav")
    vote_reject_button.visible = false
    vote_reject_button.pressed.connect(_cast_team_vote.bind("reject"))
    team_vote_side_panel = _panel(game_panel, 0.82, 0.25, 0.995, 0.71)""", "move vote panel and buttons right")

rep("""    team_vote_side_label = _add_label(team_vote_side_panel, "ПРЕДЛОЖЕНИЕ КОМАНДЫ", Vector2(10, 10), Vector2(260, 42), 16, PALE_GOLD)
    team_vote_side_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    team_vote_side_label.size = Vector2(260, 250)
    team_vote_side_label.add_theme_font_size_override("font_size", 14)""", """    team_vote_side_label = _add_label(team_vote_side_panel, "ПРЕДЛОЖЕНИЕ КОМАНДЫ", Vector2(8, 8), Vector2(205, 42), 15, PALE_GOLD)
    team_vote_side_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    team_vote_side_label.size = Vector2(205, 250)
    team_vote_side_label.add_theme_font_size_override("font_size", 13)""", "compact right vote details")

rep("""    if team_vote_side_panel:
        team_vote_side_panel.visible = voting_active
    if voting_active and team_vote_side_label:""", """    if team_vote_side_panel:
        team_vote_side_panel.visible = voting_active
    _show_pending_vote_board_move(data if voting_active else {})
    if voting_active and team_vote_side_label:""", "show proposed move on board")

anchor = "func _cast_team_vote(choice: String) -> void:\n"
helper = '''func _show_pending_vote_board_move(data: Dictionary) -> void:
    for marker in pending_vote_visual_nodes:
        if is_instance_valid(marker):
            marker.queue_free()
    pending_vote_visual_nodes.clear()
    if data.is_empty() or not is_instance_valid(world_root):
        return
    var pending: Dictionary = data.get("pendingVote", {})
    if pending.is_empty():
        return
    var move: Dictionary = pending.get("move", {})
    var from_col := int(move.get("fromFile", -1))
    var from_row := int(move.get("fromRow", -1))
    var to_col := int(move.get("toFile", -1))
    var to_row := int(move.get("toRow", -1))
    if from_col < 0 or from_col > 7 or from_row < 0 or from_row > 7 or to_col < 0 or to_col > 7 or to_row < 0 or to_row > 7:
        return
    # Gold marks the piece's current square; green marks the proposed destination.
    var squares: Array[Dictionary] = [
        {"col": from_col, "row": from_row, "color": Color(1.0, 0.68, 0.16, 0.96), "emission": Color(0.8, 0.34, 0.04)},
        {"col": to_col, "row": to_row, "color": Color(0.18, 1.0, 0.48, 0.98), "emission": Color(0.04, 0.72, 0.22)}
    ]
    for square in squares:
        var marker := MeshInstance3D.new()
        var mesh := CylinderMesh.new()
        mesh.top_radius = 0.34
        mesh.bottom_radius = 0.34
        mesh.height = 0.035
        marker.mesh = mesh
        marker.position = Vector3((int(square["col"]) - 3.5) * 1.12, 0.625, (int(square["row"]) - 3.5) * 1.0 - 0.4)
        var material := StandardMaterial3D.new()
        material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
        material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
        material.albedo_color = square["color"]
        material.emission_enabled = true
        material.emission = square["emission"]
        marker.material_override = material
        world_root.add_child(marker)
        pending_vote_visual_nodes.append(marker)

'''
if anchor not in s:
    raise SystemExit("Missing v97 anchor: vote callback")
s = s.replace(anchor, helper + anchor, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v97: pending move is highlighted on the board; vote panel and buttons moved to the right edge.")
