from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v106 anchor: " + label)
    s = s.replace(old, new, 1)

rep('var game_piece_nodes: Array[Node3D] = []', '''var game_piece_nodes: Array[Node3D] = []
var board_square_nodes: Array[MeshInstance3D] = []
var board_skins_panel: Control
var owned_board_skins: Array = ["Орех"]
var selected_board_skin := "Орех"''', "board skin state")

rep('''        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)
        piece_progression''', '''        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)
        owned_board_skins = cfg.get_value("progress", "owned_board_skins", owned_board_skins)
        selected_board_skin = str(cfg.get_value("progress", "selected_board_skin", selected_board_skin))
        if not owned_board_skins.has("Орех"):
            owned_board_skins.append("Орех")
        if not owned_board_skins.has(selected_board_skin):
            selected_board_skin = "Орех"
        piece_progression''', "load board skins")
rep('''    cfg.set_value("progress", "owned_skins", owned_skins)
    cfg.set_value("progress", "piece_progression", piece_progression)''', '''    cfg.set_value("progress", "owned_skins", owned_skins)
    cfg.set_value("progress", "owned_board_skins", owned_board_skins)
    cfg.set_value("progress", "selected_board_skin", selected_board_skin)
    cfg.set_value("progress", "piece_progression", piece_progression)''', "save board skins")

# Raise the gameplay camera to a more top-down angle and enlarge the board in view.
rep('''    camera.position = Vector3(0, 14.0, 9.5)
    camera.fov = 43.0''', '''    camera.position = Vector3(0, 17.2, 6.6)
    camera.fov = 37.0''', "mobile board viewing angle")
rep('''    for row in range(8):
        for col in range(8):
            var square_color := Color(0.78, 0.69, 0.55) if (row + col) % 2 == 0 else Color(0.12, 0.14, 0.17)
            _add_game_box(Vector3((col - 3.5) * 1.12, 0.56, (row - 3.5) * 1.0 - 0.4), Vector3(1.105, 0.065, 0.99), square_color)''', '''    board_square_nodes.clear()
    for row in range(8):
        for col in range(8):
            var square_color := _board_skin_light() if (row + col) % 2 == 0 else _board_skin_dark()
            var square := _add_game_box(Vector3((col - 3.5) * 1.12, 0.56, (row - 3.5) * 1.0 - 0.4), Vector3(1.105, 0.065, 0.99), square_color)
            board_square_nodes.append(square)''', "skin material on all 64 gameplay squares")

rep('''func _add_game_box(pos: Vector3, size: Vector3, color: Color) -> void:''', '''func _add_game_box(pos: Vector3, size: Vector3, color: Color) -> MeshInstance3D:''', "return board tile node")
rep('''    node.material_override = _material(color, 0.78)
    world_root.add_child(node)

func _add_game_cylinder''', '''    node.material_override = _material(color, 0.78)
    world_root.add_child(node)
    return node

func _add_game_cylinder''', "return created mesh")

# Add a dedicated board-skins category and keep the shop's seven cards on screen.
rep('''        {"title":"УНИКАЛЬНЫЕ СКИНЫ", "desc":"Постоянные визуальные облики для твоих фигур.", "cta":"СКИНЫ • СКОРО", "kind":"skins"},
        {"title":"ЕЖЕДНЕВНЫЙ СУНДУК"''', '''        {"title":"УНИКАЛЬНЫЕ СКИНЫ", "desc":"Постоянные визуальные облики для твоих фигур.", "cta":"СКИНЫ • СКОРО", "kind":"skins"},
        {"title":"СКИНЫ ШАХМАТНОЙ ДОСКИ", "desc":"Покупай оформление доски навсегда и выбирай его перед каждой партией.", "cta":"ВЫБРАТЬ ДОСКУ", "kind":"board_skins"},
        {"title":"ЕЖЕДНЕВНЫЙ СУНДУК"''', "board skins shop category")
rep('''        var y1 := 0.205 + float(row) * 0.355
        var y2 := y1 + 0.31''', '''        var y1 := 0.17 + float(row) * 0.255
        var y2 := y1 + 0.225''', "fit three shop rows")
rep('''        elif str(item["kind"]) == "pass":
            action.pressed.connect(_open_season_pass_screen)
        else:''', '''        elif str(item["kind"]) == "pass":
            action.pressed.connect(_open_season_pass_screen)
        elif str(item["kind"]) == "board_skins":
            action.pressed.connect(_open_board_skins_screen)
        else:''', "open board skin catalogue")

# Insert the persistent board-skin catalogue before gambit-pack screen construction.
anchor = "func _build_gambit_packs_screen() -> void:"
catalogue = """
func _board_skin_catalogue() -> Array:
    return [
        {"name":"Орех", "price":0, "light":Color(0.76,0.62,0.43), "dark":Color(0.20,0.13,0.085), "desc":"Тёплая классическая древесина."},
        {"name":"Мрамор", "price":1800, "light":Color(0.84,0.82,0.76), "dark":Color(0.25,0.29,0.32), "desc":"Светлый камень и графит."},
        {"name":"Сланец", "price":2800, "light":Color(0.56,0.61,0.64), "dark":Color(0.105,0.13,0.16), "desc":"Холодный тёмный камень."},
        {"name":"Красное дерево", "price":3500, "light":Color(0.68,0.39,0.25), "dark":Color(0.19,0.055,0.045), "desc":"Глубокие красно-коричневые тона."}
    ]

func _board_skin_data(skin_name: String) -> Dictionary:
    for item in _board_skin_catalogue():
        if str(item["name"]) == skin_name:
            return item
    return _board_skin_catalogue()[0]

func _board_skin_light() -> Color:
    return _board_skin_data(selected_board_skin)["light"]

func _board_skin_dark() -> Color:
    return _board_skin_data(selected_board_skin)["dark"]

func _apply_selected_board_skin() -> void:
    var light := _board_skin_light()
    var dark := _board_skin_dark()
    for i in range(board_square_nodes.size()):
        var tile := board_square_nodes[i]
        if is_instance_valid(tile):
            tile.material_override = _material(light if int(i / 8) % 2 == i % 8 % 2 else dark, 0.78)
    # The Chess City deployment grid uses the same selected board palette.
    for i in range(castle_hub_board_cells.size()):
        var cell := castle_hub_board_cells[i] as Button
        if not is_instance_valid(cell):
            continue
        var row := int(i / 8)
        var col := i % 8
        var style := StyleBoxFlat.new()
        style.bg_color = light if (row + col) % 2 == 0 else dark
        style.border_color = Color(0.08,0.08,0.08)
        style.set_border_width_all(1)
        cell.add_theme_stylebox_override("normal", style)
        var hover := style.duplicate() as StyleBoxFlat
        hover.bg_color = light.lightened(0.12) if (row + col) % 2 == 0 else dark.lightened(0.12)
        cell.add_theme_stylebox_override("hover", hover)

func _build_board_skins_screen() -> void:
    if board_skins_panel != null:
        return
    board_skins_panel = Control.new()
    board_skins_panel.name = "BoardSkinsCatalogue"
    board_skins_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    board_skins_panel.visible = false
    ui.add_child(board_skins_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008,0.007,0.006,0.98)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    board_skins_panel.add_child(shade)
    var frame := _panel(board_skins_panel,0.035,0.045,0.965,0.955)
    _add_label(frame,"СКИНЫ ШАХМАТНОЙ ДОСКИ",Vector2(18,10),Vector2(650,42),23,PALE_GOLD)
    var back := _ornate_button(frame,"← В МАГАЗИН",0.79,0.02,0.98,0.105,12,"nav")
    back.pressed.connect(_close_board_skins_screen)
    var wallet := _add_label(frame,"ЗЛОТЫЕ: %d   •   ВЫБРАНО: %s" % [int(balances["zloty"]),selected_board_skin],Vector2(20,58),Vector2(760,30),15,PALE_GOLD)
    wallet.name = "BoardSkinsWallet"
    _add_label(frame,"Покупка навсегда. После покупки скин можно менять без повторной оплаты.",Vector2(20,92),Vector2(850,28),12,Color(0.82,0.79,0.72))
    var items := _board_skin_catalogue()
    for i in range(items.size()):
        var item: Dictionary = items[i]
        var x1 := 0.025 + float(i % 2) * 0.49
        var y1 := 0.16 + float(int(i / 2)) * 0.255
        var card := _panel(frame,x1,y1,x1+0.46,y1+0.235)
        _add_label(card,str(item["name"]).to_upper(),Vector2(12,8),Vector2(350,25),15,PALE_GOLD)
        var swatch := ColorRect.new()
        swatch.position = Vector2(14,42)
        swatch.size = Vector2(92,58)
        swatch.color = item["light"]
        card.add_child(swatch)
        var dark_swatch := ColorRect.new()
        dark_swatch.position = Vector2(106,42)
        dark_swatch.size = Vector2(92,58)
        dark_swatch.color = item["dark"]
        card.add_child(dark_swatch)
        var desc := _add_label(card,str(item["desc"]),Vector2(210,42),Vector2(190,58),11,Color(0.84,0.81,0.74))
        desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        var name := str(item["name"])
        var owned := owned_board_skins.has(name)
        var selected := selected_board_skin == name
        var caption := "ВЫБРАНА" if selected else ("ВЫБРАТЬ" if owned else "КУПИТЬ • %d ЗЛ." % int(item["price"]))
        var action := _ornate_button(card,caption,0.06,0.72,0.94,0.95,11,"party" if owned else "nav")
        action.pressed.connect(_board_skin_action.bind(name,int(item["price"])))
    _refresh_board_skins_wallet()

func _refresh_board_skins_wallet() -> void:
    if board_skins_panel == null:
        return
    var wallet := board_skins_panel.find_child("BoardSkinsWallet",true,false) as Label
    if wallet:
        wallet.text = "ЗЛОТЫЕ: %d   •   ВЫБРАНО: %s" % [int(balances["zloty"]),selected_board_skin]

func _open_board_skins_screen() -> void:
    if board_skins_panel == null:
        _build_board_skins_screen()
    if shop_panel:
        shop_panel.visible = false
    board_skins_panel.visible = true
    _refresh_board_skins_wallet()

func _close_board_skins_screen() -> void:
    if board_skins_panel:
        board_skins_panel.visible = false
    if shop_panel:
        shop_panel.visible = true

func _board_skin_action(skin_name: String, price: int) -> void:
    if not owned_board_skins.has(skin_name):
        if int(balances["zloty"]) < price:
            _show_notice("Недостаточно злотых для покупки этой доски.")
            return
        balances["zloty"] = int(balances["zloty"]) - price
        owned_board_skins.append(skin_name)
    selected_board_skin = skin_name
    _save_economy()
    _apply_selected_board_skin()
    _refresh_board_skins_wallet()
    if board_skins_panel:
        board_skins_panel.queue_free()
        board_skins_panel = null
        _build_board_skins_screen()
        board_skins_panel.visible = true
    _show_notice("Доска «%s» выбрана. Оформление сохранено навсегда." % skin_name)

"""
if anchor not in s:
    raise SystemExit("catalogue insertion anchor missing")
s = s.replace(anchor, catalogue + "\n" + anchor);

# Re-apply selected palette whenever the city board has been created.
rep('''    _refresh_castle_hub_deployment()

func _open_castle_hub_deployment()''', '''    _refresh_castle_hub_deployment()
    _apply_selected_board_skin()

func _open_castle_hub_deployment()''', "apply palette to Chess City deployment board")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v106 board rotation and permanent board-skin shop patch applied.")
