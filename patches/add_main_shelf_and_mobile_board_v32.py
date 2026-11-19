from pathlib import Path
p=Path(__file__).resolve().parent.parent/'scripts'/'main.gd'
s=p.read_text(encoding='utf-8')
def rep(a,b,n):
 global s
 if a not in s: raise SystemExit('Missing anchor: '+n)
 s=s.replace(a,b,1)
for a,b,n in [
('Vector3(9.4, 0.5, 8.0)','Vector3(10.15, 0.5, 9.15)','board base'),
('Vector3(9.15, 0.08, 7.75)','Vector3(9.95, 0.08, 9.0)','board trim'),
('Vector3(8.75, 0.22, 7.35)','Vector3(9.55, 0.22, 8.6)','board surface'),
('(col - 3.5) * 1.05, 0.56, (row - 3.5) * 0.88 - 0.4), Vector3(1.03, 0.055, 0.86)','(col - 3.5) * 1.12, 0.56, (row - 3.5) * 1.0 - 0.4), Vector3(1.10, 0.055, 0.98)','tiles'),
('var x := (col - 3.5) * 1.05','var x := (col - 3.5) * 1.12','piece spacing'),
('(0 - 3.5) * 0.88 - 0.4','(0 - 3.5) * 1.0 - 0.4','black back rank'),
('(1 - 3.5) * 0.88 - 0.4','(1 - 3.5) * 1.0 - 0.4','black pawns'),
('(6 - 3.5) * 0.88 - 0.4','(6 - 3.5) * 1.0 - 0.4','white pawns'),
('(7 - 3.5) * 0.88 - 0.4','(7 - 3.5) * 1.0 - 0.4','white back rank'),
('roundi(x / 1.05 + 3.5)','roundi(x / 1.12 + 3.5)','piece col'),
('roundi((z + 0.4) / 0.88 + 3.5)','roundi((z + 0.4) / 1.0 + 3.5)','piece row'),
('roundi(hit.x / 1.05 + 3.5)','roundi(hit.x / 1.12 + 3.5)','tap col'),
('roundi((hit.z + 0.4) / 0.88 + 3.5)','roundi((hit.z + 0.4) / 1.0 + 3.5)','tap row'),
('(col - 3.5) * 1.05, 0.64, (row - 3.5) * 0.88 - 0.4','(col - 3.5) * 1.12, 0.64, (row - 3.5) * 1.0 - 0.4','move position'),
('(rook_to_col - 3.5) * 1.05, 0.64, (from_row - 3.5) * 0.88 - 0.4','(rook_to_col - 3.5) * 1.12, 0.64, (from_row - 3.5) * 1.0 - 0.4','rook position'),
('(to_col - 3.5) * 1.05, 0.64, (to_row - 3.5) * 0.88 - 0.4','(to_col - 3.5) * 1.12, 0.64, (to_row - 3.5) * 1.0 - 0.4','final position')]: rep(a,b,n)
rep('root.position = Vector3(x, 0.64, z)','root.position = Vector3(x, 0.64, z)\n    root.scale = Vector3(1.12, 1.12, 1.12)','piece scale')
rep('var prep_piece_buttons: Array[Button] = []','var prep_piece_buttons: Array[Button] = []\nvar main_piece_buttons: Array[Button] = []','shelf state')
rep('    lock_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER\n\n    # Large ornamental "PARTY" plaque.','''    lock_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER\n    piece_name.anchor_top = 0.625\n    piece_name.anchor_bottom = 0.625\n    piece_name.offset_top = 0\n    piece_name.offset_bottom = 28\n    lock_hint.visible = false\n    var shelf := _panel(menu_panel, 0.205, 0.675, 0.795, 0.735)\n    shelf.name = "MainPieceShelf"\n    for i in range(PIECES.size()):\n        var piece_title: String = PIECES[i]\n        var unlocked: bool = unlocked_pieces.has(piece_title)\n        var label := piece_title if unlocked else "🔒\\n" + piece_title\n        var b := _ornate_button(shelf, label, 0.012 + float(i) * 0.164, 0.06, 0.168 + float(i) * 0.164, 0.94, 10, "nav")\n        b.modulate = Color(1,1,1,1) if unlocked else Color(0.48,0.48,0.48,0.82)\n        b.pressed.connect(_select_main_piece.bind(i))\n        main_piece_buttons.append(b)\n    _refresh_main_piece_shelf()\n\n    # Large ornamental "PARTY" plaque.''','main shelf')
rep('func _open_mode_selection() -> void:\n    if mode_selection_panel == null:','func _open_mode_selection() -> void:\n    if not unlocked_pieces.has(selected_match_piece):\n        _show_notice("Сначала выбери открытую фигуру на полке.")\n        return\n    if mode_selection_panel == null:','locked piece guard')
s += '''\n\nfunc _select_main_piece(index: int) -> void:\n    if index < 0 or index >= PIECES.size(): return\n    selected_piece = index\n    var name: String = PIECES[index]\n    _build_preview_piece(name)\n    var unlocked: bool = unlocked_pieces.has(name)\n    if unlocked:\n        selected_match_piece = name\n        _show_notice(name + " выбрана. Нажми «ПАРТИЯ», чтобы продолжить.")\n    else:\n        _show_notice("🔒 " + name + " закрыта. Пока доступна только пешка.")\n    var title := menu_panel.find_child("PieceName", true, false) as Label\n    if title: title.text = name.to_upper() + ("  •  ДОСТУПНА" if unlocked else "  •  🔒 ЗАКРЫТА")\n    _refresh_main_piece_shelf()\n\nfunc _refresh_main_piece_shelf() -> void:\n    for i in range(main_piece_buttons.size()):\n        var name: String = PIECES[i]\n        var unlocked: bool = unlocked_pieces.has(name)\n        main_piece_buttons[i].text = name if unlocked else "🔒\\n" + name\n        main_piece_buttons[i].modulate = Color(1,1,1,1) if unlocked else Color(0.48,0.48,0.48,0.82)\n        main_piece_buttons[i].add_theme_color_override("font_color", PALE_GOLD if i == selected_piece else Color(0.72,0.68,0.61))\n'''
p.write_text(s,encoding='utf-8')
print('CHECKMATE v32: larger mobile board and selectable main-menu figure shelf')