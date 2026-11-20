from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v95 anchor: " + label)
    s = s.replace(old, new, 1)

# Make the three left information cards easier to read on a phone.
for name, old_size, new_size in [
    ("task_title", 22, 25), ("task_desc", 18, 20),
    ("pass_title", 22, 25), ("pass_desc", 18, 20),
    ("event_title", 22, 25), ("event_desc", 18, 20),
]:
    rep(f'{name}.add_theme_font_size_override("font_size", {old_size})',
        f'{name}.add_theme_font_size_override("font_size", {new_size})',
        name + " font size")

# Give the central figure more screen space, without colliding with the Party button or silhouette row.
rep("""    preview_container.anchor_left = 0.295
    preview_container.anchor_top = 0.245
    preview_container.anchor_right = 0.705
    preview_container.anchor_bottom = 0.665""", """    preview_container.anchor_left = 0.265
    preview_container.anchor_top = 0.235
    preview_container.anchor_right = 0.735
    preview_container.anchor_bottom = 0.700""", "larger central figure viewport")

# Use a straighter, more vertical front view of the figure.
rep("""    preview_camera.position = Vector3(0, 1.72, 5.45)
    preview_camera.fov = 30""", """    preview_camera.position = Vector3(0, 0.95, 5.9)
    preview_camera.fov = 26""", "front-on vertical camera")
rep("    preview_camera.look_at(Vector3(0, 0.95, 0), Vector3.UP)",
    "    preview_camera.look_at(Vector3(0, 0.68, 0), Vector3.UP)",
    "lower camera look target")

# Remove the complete stone pedestal and all of its decorative rings. The chess piece stands directly in the scene.
start = s.find("    # A restrained, dark carved-stone plinth:")
end = s.find("    preview_pawn = Node3D.new()", start)
if start < 0 or end < 0:
    raise SystemExit("Missing v95 pedestal block")
s = s[:start] + s[end:]

rep("    preview_pawn.position.y = 0.16", "    preview_pawn.position.y = 0.0", "stand figure on floor")
rep("    preview_pawn.scale = Vector3(1.22, 1.22, 1.22)",
    "    preview_pawn.scale = Vector3(1.62, 1.62, 1.62)",
    "larger central chess piece")

# Keep the piece upright and facing the camera when the menu opens.
rep("        preview_pawn.rotation.y = deg_to_rad(45.0)",
    "        preview_pawn.rotation = Vector3.ZERO",
    "upright front-facing preview")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v95: larger left-card text and central upright wooden figure, with pedestal removed.")

# Rebuild trigger after correcting the workflow patch sequence.
