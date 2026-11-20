from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v86 anchor: " + label)
    s = s.replace(old, new, 1)

def replace_func(name: str, next_name: str, body: str) -> None:
    global s
    start = s.find("func " + name + "(")
    if start < 0:
        raise SystemExit("Missing function: " + name)
    end = s.find("\nfunc " + next_name + "(", start + 10)
    if end < 0:
        raise SystemExit("Missing next function after: " + name)
    s = s[:start] + body.rstrip() + "\n\n" + s[end:]

# Restore the 3D figure preview in the main menu and move the silhouette row down.
rep("    preview_container.visible = false", "    preview_container.visible = true", "restore central 3D figure")
rep("    preview_container.mouse_filter = Control.MOUSE_FILTER_IGNORE", "    preview_container.mouse_filter = Control.MOUSE_FILTER_STOP", "preview touch target")
rep("""    preview_container.anchor_left = 0.285
    preview_container.anchor_top = 0.265
    preview_container.anchor_right = 0.715
    preview_container.anchor_bottom = 0.805""", """    preview_container.anchor_left = 0.315
    preview_container.anchor_top = 0.285
    preview_container.anchor_right = 0.685
    preview_container.anchor_bottom = 0.625""", "central preview layout")
rep("""    silhouette_row.anchor_top = 0.595
    silhouette_row.anchor_bottom = 0.735""", """    silhouette_row.anchor_top = 0.665
    silhouette_row.anchor_bottom = 0.805""", "lower silhouette row")

# Enter Chess City directly: never show the old account/login form over the castle territory.
rep("""func _open_city_screen() -> void:
    _castle_hub_ensure_state()
    if menu_panel:""", """func _open_city_screen() -> void:
    _castle_hub_ensure_state()
    if account_panel:
        account_panel.visible = false
    if city_panel:
        city_panel.visible = false
    if menu_panel:""", "direct city entry")

# Remove the throne-hall environment from the actual chess match. Keep only a neutral backdrop,
# lighting and the chessboard, so the board becomes the visual focus.
world_body = r'''func _build_world() -> void:
    world_root = Node3D.new()
    world_root.name = "ChessGameWorld"
    add_child(world_root)
    var env_node := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.105, 0.115, 0.13)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.78, 0.80, 0.84)
    env.ambient_light_energy = 1.0
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    env_node.environment = env
    world_root.add_child(env_node)

    camera = Camera3D.new()
    camera.position = Vector3(0, 11.6, 7.0)
    camera.fov = 43.0
    world_root.add_child(camera)
    camera.look_at(Vector3(0, 0.50, -0.4), Vector3.UP)

    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-48, -28, 0)
    sun.light_color = Color(1.0, 0.92, 0.80)
    sun.light_energy = 1.35
    sun.shadow_enabled = true
    world_root.add_child(sun)

    # The board is the only large object in the match environment.
    _add_game_box(Vector3(0, 0.05, -0.4), Vector3(10.15, 0.5, 9.15), Color(0.20, 0.13, 0.075))
    _add_game_box(Vector3(0, 0.31, -0.4), Vector3(9.95, 0.08, 9.0), Color(0.32, 0.27, 0.22))
    _add_game_box(Vector3(0, 0.43, -0.4), Vector3(9.55, 0.22, 8.6), Color(0.075, 0.055, 0.04))
    for row in range(8):
        for col in range(8):
            var square_color := Color(0.78, 0.69, 0.55) if (row + col) % 2 == 0 else Color(0.12, 0.14, 0.17)
            _add_game_box(Vector3((col - 3.5) * 1.12, 0.56, (row - 3.5) * 1.0 - 0.4), Vector3(1.105, 0.065, 0.99), square_color)
    _build_game_pieces()
    world_root.visible = false
'''
replace_func("_build_world", "_build_game_pieces", world_body)

# Make each figure significantly larger.
rep("    root.scale = Vector3(1.30, 1.30, 1.30)", "    root.scale = Vector3(1.62, 1.62, 1.62)", "larger chess pieces")

# Zoom the board to roughly half the screen and turn the player's own colour toward the camera.
rep("""    camera.fov = 49.0
    camera.position = Vector3(0, 15.8, 9.8)
    camera.look_at(Vector3(0, 0.50, -0.4), Vector3.UP)""", """    camera.fov = 42.0
    var viewing_team := "white"
    if not local_self_play_active:
        viewing_team = local_player_team if online_active else local_user_team
    if viewing_team != "black":
        camera.position = Vector3(0, 11.6, 7.0)
    else:
        camera.position = Vector3(0, 11.6, -7.0)
    camera.look_at(Vector3(0, 0.50, -0.4), Vector3.UP)""", "zoom and player-side orientation")

# Reliable mobile board mapping: choose the closest projected square centre, rather than relying
# only on a ray-plane intersection that can miss on tall phones or after camera rotation.
click_start = s.find("func _handle_game_board_click(screen_position: Vector2) -> void:")
if click_start < 0:
    raise SystemExit("Missing board click function")
click_end = s.find("\nfunc _process_classic_move(", click_start)
if click_end < 0:
    raise SystemExit("Missing next function after board click")
click_body = s[click_start:click_end]
old_mapping = '''    var ray_origin: Vector3 = camera.project_ray_origin(screen_position)
    var ray_direction: Vector3 = camera.project_ray_normal(screen_position)
    var hit = Plane(Vector3.UP, 0.59).intersects_ray(ray_origin, ray_direction)
    if hit == null:
        return
    var col: int = roundi(hit.x / 1.12 + 3.5)
    var row: int = roundi((hit.z + 0.4) / 1.0 + 3.5)
    # Perspective can shift a tap from the piece's base to a neighbouring cell.
    # Prefer the nearest visible piece when the user taps directly on a model.
    var nearest_piece: Node3D = null
    var cell_a := camera.unproject_position(Vector3(0.0, 0.64, -0.4))
    var cell_b := camera.unproject_position(Vector3(1.12, 0.64, -0.4))
    var nearest_distance := clampf(cell_a.distance_to(cell_b) * 0.43, 18.0, 52.0)
    for visible_piece in game_piece_nodes:
        if not is_instance_valid(visible_piece):
            continue
        var projected := camera.unproject_position(visible_piece.global_position + Vector3(0, 0.62, 0))
        var distance := projected.distance_to(screen_position)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_piece = visible_piece
    if nearest_piece != null:
        col = int(nearest_piece.get_meta("col"))
        row = int(nearest_piece.get_meta("row"))
    if col < 0 or col > 7 or row < 0 or row > 7:
        return'''
new_mapping = '''    var col := -1
    var row := -1
    var best_distance := INF
    var best_limit := 0.0
    for candidate_row in range(8):
        for candidate_col in range(8):
            var world_center := Vector3((candidate_col - 3.5) * 1.12, 0.60, (candidate_row - 3.5) * 1.0 - 0.4)
            var screen_center := camera.unproject_position(world_center)
            var distance := screen_center.distance_to(screen_position)
            var local_step := 10000.0
            if candidate_col < 7:
                var right_center := camera.unproject_position(world_center + Vector3(1.12, 0, 0))
                local_step = minf(local_step, screen_center.distance_to(right_center))
            if candidate_row < 7:
                var lower_center := camera.unproject_position(world_center + Vector3(0, 0, 1.0))
                local_step = minf(local_step, screen_center.distance_to(lower_center))
            if distance < best_distance:
                best_distance = distance
                best_limit = maxf(22.0, local_step * 0.82)
                col = candidate_col
                row = candidate_row
    if col < 0 or row < 0 or best_distance > best_limit:
        return
    # Tapping the visible model itself always selects its actual square.
    var nearest_piece: Node3D = null
    var nearest_piece_distance := best_limit * 0.78
    for visible_piece in game_piece_nodes:
        if not is_instance_valid(visible_piece):
            continue
        var projected := camera.unproject_position(visible_piece.global_position + Vector3(0, 0.62, 0))
        var distance := projected.distance_to(screen_position)
        if distance < nearest_piece_distance:
            nearest_piece_distance = distance
            nearest_piece = visible_piece
    if nearest_piece != null:
        col = int(nearest_piece.get_meta("col"))
        row = int(nearest_piece.get_meta("row"))'''
if old_mapping not in click_body:
    raise SystemExit("Could not find original board tap mapping")
click_body = click_body.replace(old_mapping, new_mapping, 1)
s = s[:click_start] + click_body + s[click_end:]

# Local games must not be blocked by the network-server authority check.
rep("""    if game_over or current_team != _local_team() and not multiplayer.is_server():
        return
    var piece := _get_game_piece_at(from_col, from_row)""", """    if game_over:
        return
    if online_active and current_team != _local_team() and not multiplayer.is_server():
        return
    var piece := _get_game_piece_at(from_col, from_row)""", "allow local classic moves")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v86: restored main menu piece preview, direct Chess City entry, larger zoomed board and pieces, player-side camera orientation, simplified match background and reliable touch-to-square mapping.")
