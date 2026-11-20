from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")
old = '''    var shelf := _panel(menu_panel, 0.205, 0.675, 0.795, 0.735)
    shelf.name = "MainPieceShelf"
    for i in range(PIECES.size()):
        var piece_title: String = PIECES[i]
        var unlocked: bool = unlocked_pieces.has(piece_title)
        var glyphs := ["♟", "♜", "♞", "♝", "♛", "♚"]
        var label: String = str(glyphs[i]) + ("\\n🔒" if not unlocked else "")
        var b := _ornate_button(shelf, label, 0.012 + float(i) * 0.164, 0.06, 0.168 + float(i) * 0.164, 0.94, 22, "nav")
        b.tooltip_text = piece_title + (" • открыта" if unlocked else " • скоро")
        b.modulate = Color(1,1,1,1) if unlocked else Color(0.48,0.48,0.48,0.82)
        b.pressed.connect(_select_main_piece.bind(i))
        main_piece_buttons.append(b)
    _refresh_main_piece_shelf()
'''
new = '''    # Minimal silhouettes without cards, square backgrounds or bright fills.
    var silhouette_row := Control.new()
    silhouette_row.name = "MainPieceSilhouettes"
    silhouette_row.anchor_left = 0.29
    silhouette_row.anchor_right = 0.71
    silhouette_row.anchor_top = 0.675
    silhouette_row.anchor_bottom = 0.755
    menu_panel.add_child(silhouette_row)
    for i in range(PIECES.size()):
        var piece_title: String = PIECES[i]
        var b := Button.new()
        b.flat = true
        b.focus_mode = Control.FOCUS_NONE
        b.anchor_left = float(i) / 6.0
        b.anchor_right = float(i + 1) / 6.0
        b.anchor_top = 0.0
        b.anchor_bottom = 1.0
        b.text = ["♟", "♜", "♞", "♝", "♛", "♚"][i]
        b.add_theme_font_size_override("font_size", 31)
        b.add_theme_color_override("font_color", Color(0.68, 0.67, 0.63))
        b.add_theme_color_override("font_hover_color", Color(0.84, 0.82, 0.76))
        b.add_theme_stylebox_override("normal", StyleBoxEmpty.new())
        b.add_theme_stylebox_override("hover", StyleBoxEmpty.new())
        b.add_theme_stylebox_override("pressed", StyleBoxEmpty.new())
        b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
        b.tooltip_text = piece_title + (" • доступна" if unlocked_pieces.has(piece_title) else " • закрыта")
        b.pressed.connect(_select_main_piece.bind(i))
        silhouette_row.add_child(b)
        main_piece_buttons.append(b)
    _refresh_main_piece_shelf()
'''
if old not in s: raise SystemExit("shelf anchor missing")
s = s.replace(old, new, 1)
old2 = '''func _refresh_main_piece_shelf() -> void:
    for i in range(main_piece_buttons.size()):
        var name: String = PIECES[i]
        var unlocked: bool = unlocked_pieces.has(name)
        var glyphs := ["♟", "♜", "♞", "♝", "♛", "♚"]
        main_piece_buttons[i].text = glyphs[i] + ("\\n🔒" if not unlocked else "")
        main_piece_buttons[i].modulate = Color(1,1,1,1) if unlocked else Color(0.38,0.38,0.38,0.72)
        main_piece_buttons[i].add_theme_color_override("font_color", Color(1.0,0.86,0.52) if i == selected_piece else Color(0.72,0.68,0.61))
        main_piece_buttons[i].add_theme_color_override("font_outline_color", Color(0.03,0.02,0.01,1))
        main_piece_buttons[i].add_theme_constant_override("outline_size", 5)
'''
new2 = '''func _refresh_main_piece_shelf() -> void:
    for i in range(main_piece_buttons.size()):
        var name: String = PIECES[i]
        var unlocked: bool = unlocked_pieces.has(name)
        var shade := Color(0.82, 0.81, 0.77) if i == selected_piece else Color(0.57, 0.57, 0.54)
        if not unlocked:
            shade = Color(0.37, 0.37, 0.35)
        main_piece_buttons[i].add_theme_color_override("font_color", shade)
        main_piece_buttons[i].tooltip_text = name + (" • доступна" if unlocked else " • закрыта")
'''
if old2 not in s: raise SystemExit("refresh anchor missing")
s = s.replace(old2, new2, 1)
old3 = '''    if selected_piece != 0:
        _show_notice("🔒 " + piece_name + " пока заблокирована. Открой её в магазине.")
'''
new3 = '''    if selected_piece != 0 and unlocked_pieces.has(piece_name):
        selected_match_piece = piece_name
        _show_notice(piece_name + " выбрана. Нажми «ПАРТИЯ», чтобы продолжить.")
    elif selected_piece != 0:
        _show_notice("🔒 " + piece_name + " пока заблокирована. Открой её в магазине.")
    _refresh_main_piece_shelf()
'''
if old3 not in s: raise SystemExit("carousel anchor missing")
s = s.replace(old3, new3, 1)
p.write_text(s, encoding="utf-8")
print("Clean main menu v47 applied")
