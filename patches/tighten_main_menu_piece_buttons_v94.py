from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v94 anchor: " + label)
    s = s.replace(old, new, 1)

# Give the six figure buttons a little more horizontal room and reduce gaps.
rep("""    silhouette_row.anchor_left = 0.165
    silhouette_row.anchor_right = 0.835
    silhouette_row.anchor_top = 0.705
    silhouette_row.anchor_bottom = 0.855""", """    silhouette_row.anchor_left = 0.12
    silhouette_row.anchor_right = 0.88
    silhouette_row.anchor_top = 0.705
    silhouette_row.anchor_bottom = 0.855""", "wider figure button shelf")

rep("""    silhouette_row.clip_contents = true
    menu_panel.add_child(silhouette_row)""", """    silhouette_row.clip_contents = true
    silhouette_row.add_theme_constant_override("separation", 2)
    menu_panel.add_child(silhouette_row)""", "tight figure button spacing")

rep('b.add_theme_font_size_override("font_size", 102)', 'b.add_theme_font_size_override("font_size", 88)', "fit silhouette glyphs inside buttons")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v94: figure silhouettes moved closer, shelf widened, glyphs fitted inside the button row.")
