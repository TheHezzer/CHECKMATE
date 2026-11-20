from pathlib import Path
import re

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v91 anchor: " + label)
    s = s.replace(old, new, 1)

# Make the central 3D figure larger without changing its model.
rep("""    preview_container.anchor_left = 0.315
    preview_container.anchor_top = 0.285
    preview_container.anchor_right = 0.685
    preview_container.anchor_bottom = 0.625""", """    preview_container.anchor_left = 0.295
    preview_container.anchor_top = 0.245
    preview_container.anchor_right = 0.705
    preview_container.anchor_bottom = 0.665""", "larger central preview area")

# Lower the figure-selection strip and give the buttons more vertical room.
rep("""    silhouette_row.anchor_left = 0.185
    silhouette_row.anchor_right = 0.815
    silhouette_row.anchor_top = 0.655
    silhouette_row.anchor_bottom = 0.815""", """    silhouette_row.anchor_left = 0.165
    silhouette_row.anchor_right = 0.835
    silhouette_row.anchor_top = 0.705
    silhouette_row.anchor_bottom = 0.855""", "lower and wider figure button strip")

# Set consistent, clearly readable heading/body sizes even if earlier UI patches changed them.
for name, size in [
    ("task_title", 22), ("task_desc", 18),
    ("pass_title", 22), ("pass_desc", 18),
    ("event_title", 22), ("event_desc", 18),
]:
    pattern = rf'({name}\.add_theme_font_size_override\("font_size", )\d+(\))'
    s, count = re.subn(pattern, rf'\g<1>{size}\g<2>', s, count=1)
    if count != 1:
        raise SystemExit("Missing v91 left card typography anchor: " + name)

# Widen text columns to use the enlarged cards.
for name in ["task_title", "task_desc", "pass_title", "pass_desc", "event_title", "event_desc"]:
    # These labels are positioned in the left information cards.
    marker = name + ".add_theme_font_size_override"
    idx = s.find(marker)
    if idx < 0:
        raise SystemExit("Missing v91 label: " + name)
    line_start = s.rfind("\n", 0, idx) + 1
    line_end = s.find("\n", idx)
    line = s[line_start:line_end if line_end >= 0 else len(s)]
    line = line.replace("Vector2(245,", "Vector2(275,").replace("Vector2(245,", "Vector2(275,")
    line = line.replace("Vector2(180,", "Vector2(210,")
    s = s[:line_start] + line + s[line_end if line_end >= 0 else len(s):]

p.write_text(s, encoding="utf-8")
print("CHECKMATE v91: enlarged central figure and left information cards; lowered, widened figure button strip.")
