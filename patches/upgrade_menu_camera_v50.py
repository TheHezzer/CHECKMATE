from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def replace(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing block: " + label)
    s = s.replace(old, new, 1)

replace("var preview_pawn: Node3D\n", "var preview_pawn: Node3D\nvar preview_camera_pivot: Node3D\nvar preview_camera: Camera3D\nvar preview_camera_pitch := 0.0\n", "camera vars")

# More legible text and cleaner alignment on the landscape menu.
changes = [
('profile_name_label = _add_label(profile, "ГОСТЬ", Vector2(92, 10), Vector2(175, 25), 18, PALE_GOLD)', 'profile_name_label = _add_label(profile, "ГОСТЬ", Vector2(92, 8), Vector2(180, 28), 21, PALE_GOLD)'),
('profile_state_label = _add_label(profile, "НАЖМИ НА АВАТАР • ВОЙТИ", Vector2(92, 39), Vector2(150, 20), 12, Color(0.72, 0.72, 0.72))', 'profile_state_label = _add_label(profile, "НАЖМИ НА АВАТАР • ВОЙТИ", Vector2(92, 38), Vector2(180, 23), 14, Color(0.82, 0.82, 0.82))'),
('_add_label(profile, "ПРОГРЕСС НА ЭТОМ УСТРОЙСТВЕ", Vector2(92, 58), Vector2(185, 18), 9, Color(0.66, 0.62, 0.56))', '_add_label(profile, "ПРОГРЕСС НА ЭТОМ УСТРОЙСТВЕ", Vector2(92, 61), Vector2(185, 18), 11, Color(0.76, 0.72, 0.66))'),
('0.285, 0.035, 0.425, 0.125, 14, "nav")', '0.275, 0.035, 0.425, 0.125, 17, "nav")'),
('0.432, 0.035, 0.572, 0.125, 14, "nav")', '0.432, 0.035, 0.575, 0.125, 17, "nav")'),
('0.579, 0.035, 0.715, 0.125, 14, "nav")', '0.582, 0.035, 0.722, 0.125, 17, "nav")'),
('var q := _ornate_button(menu_panel, quick_icons[i] + "\\n" + quick_names[i], x, 0.018, x + 0.050, 0.115, 9, "nav")', 'var q := _ornate_button(menu_panel, quick_icons[i] + "\\n" + quick_names[i], x, 0.018, x + 0.050, 0.115, 12, "nav")'),
('_add_label(tasks, "Ежедневные\\nзадачи", Vector2(67, 12), Vector2(175, 42), 16, PALE_GOLD)', '_add_label(tasks, "Ежедневные\\nзадачи", Vector2(67, 12), Vector2(175, 42), 19, PALE_GOLD)'),
('_add_label(tasks, "Награды за победы и испытания", Vector2(67, 57), Vector2(175, 32), 10, Color(0.79, 0.72, 0.61))', '_add_label(tasks, "Награды за победы и испытания", Vector2(67, 57), Vector2(175, 32), 12, Color(0.88, 0.82, 0.73))'),
('_add_label(pass_panel, "Боевой\\nпропуск", Vector2(67, 12), Vector2(175, 42), 16, PALE_GOLD)', '_add_label(pass_panel, "Боевой\\nпропуск", Vector2(67, 12), Vector2(175, 42), 19, PALE_GOLD)'),
('_add_label(pass_panel, "Уровень 12  •  Награды сезона", Vector2(67, 57), Vector2(175, 32), 10, Color(0.79, 0.72, 0.61))', '_add_label(pass_panel, "Уровень 12  •  Награды сезона", Vector2(67, 57), Vector2(175, 32), 12, Color(0.88, 0.82, 0.73))'),
('_add_label(event_panel, "Событие\\n«Осенний турнир»", Vector2(67, 10), Vector2(180, 44), 15, PALE_GOLD)', '_add_label(event_panel, "Событие\\n«Осенний турнир»", Vector2(67, 10), Vector2(180, 44), 18, PALE_GOLD)'),
('_add_label(event_panel, "До конца: 7 д. 14 ч.", Vector2(67, 59), Vector2(170, 24), 10, Color(0.79, 0.72, 0.61))', '_add_label(event_panel, "До конца: 7 д. 14 ч.", Vector2(67, 59), Vector2(170, 24), 12, Color(0.88, 0.82, 0.73))'),
('piece_name.anchor_top = 0.625', 'piece_name.anchor_top = 0.615'),
('piece_name.anchor_bottom = 0.625', 'piece_name.anchor_bottom = 0.615'),
('silhouette_row.anchor_left = 0.29', 'silhouette_row.anchor_left = 0.295'),
('silhouette_row.anchor_right = 0.71', 'silhouette_row.anchor_right = 0.705'),
('silhouette_row.anchor_top = 0.675', 'silhouette_row.anchor_top = 0.665'),
('b.add_theme_font_size_override("font_size", 31)', 'b.add_theme_font_size_override("font_size", 58)'),
('var x := 0.235 + float(i) * 0.185', 'var x := 0.225 + float(i) * 0.190'),
('x, 0.735, x + 0.175, 0.885, 15, "card")', 'x, 0.755, x + 0.180, 0.895, 19, "card")'),
('x, 0.900, x + 0.158, 0.998, 13, "nav")', 'x, 0.905, x + 0.158, 0.998, 16, "nav")'),
]
for old, new in changes:
    if old in s:
        s = s.replace(old, new, 1)

replace("""    var cam := Camera3D.new()
    cam.position = Vector3(0, 1.55, 6.6)
    cam.fov = 32
    scene.add_child(cam)
    cam.look_at(Vector3(0, 1.05, 0), Vector3.UP)
""", """    preview_camera_pivot = Node3D.new()
    preview_camera_pivot.name = "PreviewCameraOrbitPivot"
    preview_camera_pivot.position = Vector3(0, 1.05, 0)
    scene.add_child(preview_camera_pivot)
    preview_camera = Camera3D.new()
    preview_camera.name = "OrbitingPreviewCamera"
    preview_camera.position = Vector3(0, 0, 6.6)
    preview_camera.fov = 32
    preview_camera_pivot.add_child(preview_camera)
    preview_camera.look_at(Vector3(0, 1.05, 0), Vector3.UP)
    preview_camera_pitch = 0.0
""", "camera rig")

replace("""    # Horizontal movement turns the piece around; vertical movement tilts it.
    preview_pawn.rotate_y(deg_to_rad(delta_x * 0.85))
    preview_pawn.rotate_x(deg_to_rad(delta_y * 0.75))
""", """    # Orbit the camera around a stationary piece and pedestal.
    if is_instance_valid(preview_camera_pivot):
        preview_camera_pivot.rotate_y(deg_to_rad(delta_x * 0.55))
        preview_camera_pitch = clampf(preview_camera_pitch + deg_to_rad(delta_y * 0.35), deg_to_rad(-24.0), deg_to_rad(24.0))
        preview_camera_pivot.rotation.x = preview_camera_pitch
""", "camera drag")

replace('hint.text = "🔒 ОТКРОЙ ФИГУРУ В КОЛЛЕКЦИИ" if selected_piece != 0 else "ВОДИ ПАЛЬЦЕМ ВЛЕВО/ВПРАВО И ВВЕРХ/ВНИЗ — ВРАЩЕНИЕ НА 360°"', 'hint.text = "🔒 ОТКРОЙ ФИГУРУ В КОЛЛЕКЦИИ" if selected_piece != 0 else "ПРОВЕДИ ПАЛЬЦЕМ — КАМЕРА ОБОЙДЁТ ФИГУРУ"', "hint")
s = s.replace("В центре можно вращать фигуру, стрелками переключать коллекцию.", "В центре можно вращать камеру вокруг неподвижной фигуры, стрелками переключать коллекцию.", 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v50 menu and camera-orbit patch applied")
