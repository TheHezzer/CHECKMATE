from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

old = '''    var bg := TextureRect.new()
    bg.texture = load("res://assets/castle_hall.png")
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
    bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
    menu_panel.add_child(bg)
'''
if old not in s:
    raise SystemExit("Could not find flat menu background block")
s = s.replace(old, '''    _build_menu_3d_environment()
''', 1)

marker = "func _build_piece_preview() -> void:\n"
if marker not in s:
    raise SystemExit("Could not find preview insertion point")

code = '''func _build_menu_3d_environment() -> void:
    # Full-screen 3D throne hall. UI is layered above this viewport.
    var container := SubViewportContainer.new()
    container.name = "MainMenu3DEnvironment"
    container.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    container.mouse_filter = Control.MOUSE_FILTER_IGNORE
    container.stretch = true
    menu_panel.add_child(container)

    var viewport := SubViewport.new()
    viewport.name = "MainMenu3DViewport"
    viewport.size = Vector2i(1600, 900)
    viewport.own_world_3d = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    container.add_child(viewport)

    var hall := Node3D.new()
    hall.name = "ThroneHall3D"
    viewport.add_child(hall)

    var env_node := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.018, 0.015, 0.014)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.50, 0.43, 0.34)
    env.ambient_light_energy = 0.72
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    env_node.environment = env
    hall.add_child(env_node)

    var cam := Camera3D.new()
    cam.position = Vector3(0, 6.3, 17.8)
    cam.fov = 48
    hall.add_child(cam)
    cam.look_at(Vector3(0, 3.0, -3.8), Vector3.UP)

    var key := DirectionalLight3D.new()
    key.rotation_degrees = Vector3(-34, -22, 0)
    key.light_color = Color(1.0, 0.78, 0.52)
    key.light_energy = 1.05
    key.shadow_enabled = true
    hall.add_child(key)

    var floor_mat := _material(Color(0.075, 0.055, 0.043), 0.38, 0.12)
    var floor_alt := _material(Color(0.105, 0.078, 0.058), 0.42, 0.08)
    var wall_mat := _material(Color(0.095, 0.075, 0.064), 0.86, 0.02)
    var stone_mat := _material(Color(0.20, 0.17, 0.14), 0.78, 0.04)
    var trim_mat := _material(Color(0.31, 0.22, 0.13), 0.58, 0.18)
    var dark_mat := _material(Color(0.025, 0.021, 0.019), 0.9, 0.0)
    var glass_blue := _material(Color(0.055, 0.16, 0.22), 0.28, 0.22)
    var glass_red := _material(Color(0.25, 0.075, 0.045), 0.32, 0.16)
    var banner_mat := _material(Color(0.12, 0.025, 0.022), 0.94, 0.0)

    _menu_box(hall, Vector3(0, -0.35, -1.5), Vector3(32, 0.7, 34), floor_mat)
    # Large alternating stone floor slabs give the hall real depth and scale.
    for row in range(8):
        for col in range(12):
            var tile_mat: Material = floor_mat if (row + col) % 2 == 0 else floor_alt
            _menu_box(hall, Vector3((col - 5.5) * 2.55, 0.012, (row - 3.5) * 2.65 - 1.5), Vector3(2.48, 0.035, 2.58), tile_mat)

    _menu_box(hall, Vector3(0, 6.0, -11.8), Vector3(31, 13, 0.9), wall_mat)
    _menu_box(hall, Vector3(0, 12.4, -5.5), Vector3(31, 0.7, 13), dark_mat)
    # Rear stained-glass windows and their stone mullions.
    for x in [-9.0, -4.5, 0.0, 4.5, 9.0]:
        var glass := glass_blue if int(abs(x) * 10.0) % 2 == 0 else glass_red
        _menu_box(hall, Vector3(x, 7.1, -11.22), Vector3(3.15, 7.0, 0.10), glass)
        _menu_box(hall, Vector3(x - 1.72, 7.1, -11.05), Vector3(0.18, 7.6, 0.32), trim_mat)
        _menu_box(hall, Vector3(x + 1.72, 7.1, -11.05), Vector3(0.18, 7.6, 0.32), trim_mat)
        _menu_box(hall, Vector3(x, 3.52, -11.05), Vector3(3.55, 0.18, 0.32), trim_mat)
        _menu_box(hall, Vector3(x, 10.68, -11.05), Vector3(3.55, 0.18, 0.32), trim_mat)
        _menu_box(hall, Vector3(x, 7.1, -10.98), Vector3(0.12, 7.0, 0.30), trim_mat)
        _menu_box(hall, Vector3(x, 7.1, -10.97), Vector3(3.1, 0.12, 0.30), trim_mat)

    # Paired columns, stepped bases, capitals and dark hanging banners.
    for x in [-12.0, -8.0, 8.0, 12.0]:
        for z in [-8.8, -1.0, 6.2]:
            _menu_cylinder(hall, Vector3(x, 0.62, z), 0.95, 1.0, stone_mat)
            _menu_cylinder(hall, Vector3(x, 3.75, z), 0.54, 6.0, stone_mat)
            _menu_cylinder(hall, Vector3(x, 6.85, z), 0.82, 0.42, trim_mat)
            _menu_box(hall, Vector3(x, 7.18, z), Vector3(1.45, 0.28, 1.45), stone_mat)
            if z < 0:
                _menu_box(hall, Vector3(x, 5.0, z + 0.84), Vector3(1.25, 3.4, 0.10), banner_mat)
                _menu_box(hall, Vector3(x, 3.22, z + 0.84), Vector3(0.92, 0.12, 0.10), trim_mat)

    # Broad ceremonial stairs rising to the distant throne platform.
    for i in range(9):
        var depth := 0.62 + float(i) * 0.34
        var height := 0.20 + float(i) * 0.23
        _menu_box(hall, Vector3(0, height * 0.5, -7.2 - float(i) * 0.48), Vector3(9.0 + float(i) * 0.44, height, depth), stone_mat)
        _menu_box(hall, Vector3(0, height + 0.025, -7.2 - float(i) * 0.48), Vector3(9.0 + float(i) * 0.44, 0.05, depth), trim_mat)
    _menu_box(hall, Vector3(0, 2.65, -11.2), Vector3(8.2, 0.5, 2.2), dark_mat)
    _menu_box(hall, Vector3(0, 2.95, -11.2), Vector3(7.8, 0.12, 1.9), trim_mat)

    # Warm braziers and local light pools along the nave.
    for x in [-10.2, -5.6, 5.6, 10.2]:
        var brazier_mat := _material(Color(0.18, 0.105, 0.045), 0.48, 0.32)
        _menu_cylinder(hall, Vector3(x, 1.55, 1.4), 0.38, 2.6, brazier_mat)
        _menu_cylinder(hall, Vector3(x, 2.92, 1.4), 0.72, 0.18, trim_mat)
        var flame := OmniLight3D.new()
        flame.position = Vector3(x, 3.55, 1.4)
        flame.light_color = Color(1.0, 0.34, 0.08)
        flame.light_energy = 1.5
        flame.omni_range = 8.0
        hall.add_child(flame)
        _menu_sphere(hall, Vector3(x, 3.48, 1.4), 0.22, _material(Color(1.0, 0.25, 0.035), 0.25, 0.0))

    # Side arches are suggested with tall curved stone ribs.
    for x in [-14.0, -6.0, 6.0, 14.0]:
        _menu_box(hall, Vector3(x, 8.4, -4.0), Vector3(0.42, 8.0, 0.55), stone_mat)
        _menu_box(hall, Vector3(x, 12.35, -4.0), Vector3(4.4, 0.38, 0.55), stone_mat)

func _menu_box(parent: Node3D, pos: Vector3, size: Vector3, mat: Material) -> void:
    var mesh := BoxMesh.new()
    mesh.size = size
    var node := MeshInstance3D.new()
    node.mesh = mesh
    node.position = pos
    node.material_override = mat
    parent.add_child(node)

func _menu_cylinder(parent: Node3D, pos: Vector3, radius: float, height: float, mat: Material) -> void:
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius
    mesh.bottom_radius = radius * 1.12
    mesh.height = height
    mesh.radial_segments = 32
    var node := MeshInstance3D.new()
    node.mesh = mesh
    node.position = pos
    node.material_override = mat
    parent.add_child(node)

func _menu_sphere(parent: Node3D, pos: Vector3, radius: float, mat: Material) -> void:
    var mesh := SphereMesh.new()
    mesh.radius = radius
    mesh.height = radius * 2.0
    var node := MeshInstance3D.new()
    node.mesh = mesh
    node.position = pos
    node.material_override = mat
    parent.add_child(node)

'''
s = s.replace(marker, code + marker, 1)
p.write_text(s, encoding="utf-8")
print("Replaced flat main-menu backdrop with a procedural 3D throne hall.")
