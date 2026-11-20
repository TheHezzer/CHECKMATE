from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v90 anchor: " + label)
    s = s.replace(old, new, 1)

# The preview model stays still; touch gestures orbit the camera around it.
rep("""    var delta_y := pointer_y - last_pointer_y
    # Rotate the displayed figure around its own vertical axis only.
    if is_instance_valid(preview_pawn):
        preview_pawn.rotate_y(deg_to_rad(delta_x * 0.65))
""", """    var delta_y := pointer_y - last_pointer_y
    # Orbit the camera around the stationary figure; horizontal and vertical drags
    # change the viewing angle without rotating or tilting the model itself.
    if is_instance_valid(preview_camera_pivot):
        preview_camera_pivot.rotate_y(deg_to_rad(delta_x * 0.55))
        preview_camera_pitch = clampf(preview_camera_pitch + deg_to_rad(delta_y * 0.35), deg_to_rad(-24.0), deg_to_rad(24.0))
        preview_camera_pivot.rotation.x = preview_camera_pitch
""", "camera orbit instead of model rotation")

rep('hint.text = "🔒 ОТКРОЙ ФИГУРУ В КОЛЛЕКЦИИ" if selected_piece != 0 else "ВОДИ ПАЛЬЦЕМ ВЛЕВО/ВПРАВО И ВВЕРХ/ВНИЗ — ВРАЩЕНИЕ НА 360°"', 'hint.text = "🔒 ОТКРОЙ ФИГУРУ В КОЛЛЕКЦИИ" if selected_piece != 0 else "ПРОВЕДИ ПАЛЬЦЕМ — КАМЕРА ОБОЙДЁТ ФИГУРУ"', "preview hint")

# Give the collection shelf more width and height, with larger silhouettes.
rep("""    silhouette_row.anchor_left = 0.225
    silhouette_row.anchor_right = 0.775
    silhouette_row.anchor_top = 0.665
    silhouette_row.anchor_bottom = 0.805""", """    silhouette_row.anchor_left = 0.185
    silhouette_row.anchor_right = 0.815
    silhouette_row.anchor_top = 0.655
    silhouette_row.anchor_bottom = 0.815""", "wider silhouette shelf")
rep('b.add_theme_font_size_override("font_size", 88)', 'b.add_theme_font_size_override("font_size", 102)', "larger piece silhouettes")

# Slightly strengthen the shared button and label hierarchy without changing
# the established dark/wood visual style or button positions.
rep('button.add_theme_font_size_override("font_size", font_size + 17)', 'button.add_theme_font_size_override("font_size", font_size + 19)', "larger button typography")
rep('label.add_theme_font_size_override("font_size", font_size + 15)', 'label.add_theme_font_size_override("font_size", font_size + 17)', "larger label typography")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v90: camera orbits stationary preview figure; larger silhouette shelf and stronger typography.")
