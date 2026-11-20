from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

# Remove the three mode-selection cards from the main menu. Modes remain inside Party.
rep('''    # Four large mode cards, each using the same ornate frame as the reference.
    var modes := ["Классика", "Командное голосование", "Несколько фигур"]
    var subtitles := ["Командная партия", "Голосование за ход", "Несколько фигур на игрока"]
    var symbols := ["♞", "♟", "♛"]
    for i in range(modes.size()):
        var x := 0.225 + float(i) * 0.190
        var b := _ornate_button(menu_panel, symbols[i] + "\\n" + modes[i] + "\\n" + subtitles[i], x, 0.755, x + 0.180, 0.895, 19, "card")
        b.pressed.connect(_on_mode_pressed.bind(modes[i]))

''', '''    # Mode selection is intentionally available only after pressing PARTY.
    # The area below the piece silhouettes is reserved for the expanded figure collection.
''', "remove main menu mode cards")

# Enlarge the central 3D preview slightly while keeping the same center point.
rep('''    preview_container.anchor_left = 0.375
    preview_container.anchor_top = 0.275
    preview_container.anchor_right = 0.625
    preview_container.anchor_bottom = 0.705
''', '''    preview_container.anchor_left = 0.345
    preview_container.anchor_top = 0.255
    preview_container.anchor_right = 0.655
    preview_container.anchor_bottom = 0.715
''', "enlarge center piece preview")

# Increase the figure name visibility and position the large silhouettes in the space freed by mode cards.
rep('''    var piece_name := _add_label(menu_panel, "ПЕШКА  •  ДОСТУПНА", Vector2.ZERO, Vector2(360, 30), 17, PALE_GOLD)
''', '''    var piece_name := _add_label(menu_panel, "ПЕШКА  •  ДОСТУПНА", Vector2.ZERO, Vector2(440, 38), 21, PALE_GOLD)
''', "larger piece name")
rep('''    piece_name.offset_left = -180
    piece_name.offset_right = 180
''', '''    piece_name.offset_left = -220
    piece_name.offset_right = 220
''', "center piece name width")
rep('''    piece_name.offset_bottom = 28
''', '''    piece_name.offset_bottom = 38
''', "piece name height")
rep('''    silhouette_row.anchor_left = 0.295
    silhouette_row.anchor_right = 0.705
    silhouette_row.anchor_top = 0.665
    silhouette_row.anchor_bottom = 0.755
''', '''    silhouette_row.anchor_left = 0.185
    silhouette_row.anchor_right = 0.815
    silhouette_row.anchor_top = 0.715
    silhouette_row.anchor_bottom = 0.905
''', "expand silhouette row")
rep('''        b.add_theme_font_size_override("font_size", 58)
''', '''        b.add_theme_font_size_override("font_size", 112)
''', "make silhouettes much larger")
rep('''        b.add_theme_color_override("font_color", Color(0.68, 0.67, 0.63))
        b.add_theme_color_override("font_hover_color", Color(0.84, 0.82, 0.76))
''', '''        b.add_theme_color_override("font_color", Color(0.78, 0.76, 0.70))
        b.add_theme_color_override("font_hover_color", Color(0.98, 0.94, 0.84))
''', "increase silhouette contrast")

# Make all helper-generated labels and buttons consistently larger across menus, splash, dialogs and gameplay.
rep('''    button.add_theme_font_size_override("font_size", font_size + 4)
''', '''    button.add_theme_font_size_override("font_size", font_size + 8)
''', "global button typography")
rep('''    label.add_theme_font_size_override("font_size", font_size + 3)
''', '''    label.add_theme_font_size_override("font_size", font_size + 7)
''', "global label typography")

# Directly-created labels and buttons use the same display font and a readable baseline where possible.
rep('''    button.add_theme_font_override("font", UI_FONT)
''', '''    button.add_theme_font_override("font", UI_FONT)
''', "preserve button font")

# Enlarge the piece-name text and the party plaque in the main menu.
rep('''    var party := _ornate_button(menu_panel, "⚔   П А Р Т И Я", 0.365, 0.145, 0.635, 0.255, 23, "party")
''', '''    var party := _ornate_button(menu_panel, "⚔   П А Р Т И Я", 0.365, 0.145, 0.635, 0.255, 26, "party")
''', "party plaque")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v52: larger typography, larger figure silhouettes, expanded center preview, no mode cards on main menu.")
