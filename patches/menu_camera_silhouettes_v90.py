from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# Replace only the preview-model rotation block. The camera rig is created by v50.
needle = "preview_pawn.rotate_y(deg_to_rad(delta_x * 0.65))"
idx = s.find(needle)
if idx < 0:
    nearby = s.find("preview_pawn.rotate_y")
    raise SystemExit("Missing v90 model rotation call; nearby source: " + repr(s[max(0, nearby-180):nearby+220]))
block_start = s.rfind("    if is_instance_valid(preview_pawn):", 0, idx)
if block_start < 0:
    raise SystemExit("Missing v90 preview model guard")
line_end = s.find("\n", idx)
if line_end < 0:
    line_end = len(s)
new_block = """    # Orbit the camera around the stationary figure.
    if is_instance_valid(preview_camera_pivot):
        preview_camera_pivot.rotate_y(deg_to_rad(delta_x * 0.55))
        preview_camera_pitch = clampf(preview_camera_pitch + deg_to_rad(delta_y * 0.35), deg_to_rad(-24.0), deg_to_rad(24.0))
        preview_camera_pivot.rotation.x = preview_camera_pitch"""
s = s[:block_start] + new_block + s[line_end:]

# Update the instruction shown below the central preview.
s = s.replace("ВОДИ ПАЛЬЦЕМ ВЛЕВО/ВПРАВО И ВВЕРХ/ВНИЗ — ВРАЩЕНИЕ НА 360°", "ПРОВЕДИ ПАЛЬЦЕМ — КАМЕРА ОБОЙДЁТ ФИГУРУ", 1)

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v90 anchor: " + label)
    s = s.replace(old, new, 1)

rep("""    silhouette_row.anchor_left = 0.225
    silhouette_row.anchor_right = 0.775
    silhouette_row.anchor_top = 0.665
    silhouette_row.anchor_bottom = 0.805""", """    silhouette_row.anchor_left = 0.185
    silhouette_row.anchor_right = 0.815
    silhouette_row.anchor_top = 0.655
    silhouette_row.anchor_bottom = 0.815""", "wider silhouette shelf")
rep('b.add_theme_font_size_override("font_size", 88)', 'b.add_theme_font_size_override("font_size", 102)', "larger piece silhouettes")
rep('button.add_theme_font_size_override("font_size", font_size + 17)', 'button.add_theme_font_size_override("font_size", font_size + 19)', "larger button typography")
rep('label.add_theme_font_size_override("font_size", font_size + 15)', 'label.add_theme_font_size_override("font_size", font_size + 17)', "larger label typography")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v90: camera orbits stationary preview figure; larger silhouette shelf and stronger typography.")
