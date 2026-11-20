from pathlib import Path
p=Path(__file__).resolve().parent.parent/"scripts"/"main.gd"
s=p.read_text(encoding="utf-8")
def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("Missing: "+label)
    s=s.replace(old,new,1)

rep('''    var delta_y := pointer_y - last_pointer_y
    # Orbit the camera around a stationary piece and pedestal.
    if is_instance_valid(preview_camera_pivot):
        preview_camera_pivot.rotate_y(deg_to_rad(delta_x * 0.55))
        preview_camera_pitch = clampf(preview_camera_pitch + deg_to_rad(delta_y * 0.35), deg_to_rad(-24.0), deg_to_rad(24.0))
        preview_camera_pivot.rotation.x = preview_camera_pitch
''','''    # Rotate the displayed figure around its own vertical axis only.
    if is_instance_valid(preview_pawn):
        preview_pawn.rotate_y(deg_to_rad(delta_x * 0.65))
''',"figure-only rotation")

rep('''    background.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED''','''    background.stretch_mode = TextureRect.STRETCH_SCALE''',"full-screen intro background")
rep('''    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)''','''    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.offset_left = 0
    shade.offset_top = 0
    shade.offset_right = 0
    shade.offset_bottom = 0''',"full-screen intro shade")

rep('''    var pieces := ["Конь", "Слон", "Ладья", "Ферзь", "Король"]
    var glyphs := ["♞", "♝", "♜", "♛", "♚"]
    for i in range(pieces.size()):
        var x := 0.025 + float(i) * 0.19
        var piece: String = pieces[i]
        var btn := _ornate_button(frame, glyphs[i], x, 0.245, x + 0.175, 0.43, 30, "card")
        btn.tooltip_text = piece
        btn.pressed.connect(_select_preparation_piece.bind(piece))
        prep_piece_buttons.append(btn)
''','''    var pieces := ["Пешка", "Конь", "Слон", "Ладья", "Ферзь", "Король"]
    var glyphs := ["♟", "♞", "♝", "♜", "♛", "♚"]
    for i in range(pieces.size()):
        var x := 0.025 + float(i) * 0.16
        var piece: String = pieces[i]
        var btn := _ornate_button(frame, glyphs[i], x, 0.245, x + 0.145, 0.43, 34, "card")
        btn.tooltip_text = piece + (" • обязательная фигура" if piece == "Пешка" else "")
        if piece == "Пешка":
            btn.text = "♟  ✓"
            btn.disabled = true
            btn.modulate = Color(1.0, 0.88, 0.56, 1)
        else:
            btn.pressed.connect(_select_preparation_piece.bind(piece))
            prep_piece_buttons.append(btn)
''',"mandatory pawn button and six piece layout")

rep('''        prep_piece_buttons[i].text = glyphs[i] + ("  ✓" if piece == selected_match_piece else "")
        prep_piece_buttons[i].modulate = Color(1.0,0.88,0.56,1) if piece == selected_match_piece else Color(0.78,0.78,0.78,1)''','''        prep_piece_buttons[i].text = glyphs[i] + ("  ✓" if piece == PIECES[selected_prep_piece] else "")
        prep_piece_buttons[i].modulate = Color(1.0,0.88,0.56,1) if piece == PIECES[selected_prep_piece] else Color(0.78,0.78,0.78,1)''',"move selection checkmark")

rep('''button.add_theme_font_size_override("font_size", font_size + 13)''','''button.add_theme_font_size_override("font_size", font_size + 17)''',"larger button text")
rep('''label.add_theme_font_size_override("font_size", font_size + 11)''','''label.add_theme_font_size_override("font_size", font_size + 15)''',"larger label text")

p.write_text(s,encoding="utf-8")
print("CHECKMATE v57 screen, rotation, typography and piece selection fixes applied")
