from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

if "var gambit_packs_panel: Control" not in s:
    anchor = "var shop_panel: Control"
    if anchor not in s:
        raise SystemExit("v88: shop panel variable missing")
    s = s.replace(anchor, anchor + "\nvar gambit_packs_panel: Control", 1)

# The Gambits tile opens a dedicated store page rather than a generic placeholder.
anchor = '''        action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))'''
replacement = '''        if str(item["kind"]) == "gambits":
            action.text = "ВЫБРАТЬ ПАКЕТ"
            action.pressed.connect(_open_gambit_packs_screen)
        else:
            action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))'''
if anchor not in s:
    raise SystemExit("v88: shop card action anchor missing")
s = s.replace(anchor, replacement, 1)

# Insert the premium currency screen before the shop open/close functions.
anchor = "func _open_shop_screen() -> void:"
if anchor not in s:
    raise SystemExit("v88: open shop function missing")
gambit_ui = r'''
func _build_gambit_packs_screen() -> void:
    if gambit_packs_panel != null:
        return
    gambit_packs_panel = Control.new()
    gambit_packs_panel.name = "GambitPacksScreen"
    gambit_packs_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    gambit_packs_panel.visible = false
    ui.add_child(gambit_packs_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.98)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    gambit_packs_panel.add_child(shade)

    var frame := _panel(gambit_packs_panel, 0.025, 0.035, 0.975, 0.965)
    _add_label(frame, "ПОКУПКА ГАМБИТОВ", Vector2(18, 10), Vector2(620, 42), 24, PALE_GOLD)
    var back := _ornate_button(frame, "← В МАГАЗИН", 0.80, 0.02, 0.98, 0.105, 12, "nav")
    back.pressed.connect(_close_gambit_packs_screen)

    var wallet := _add_label(frame, "", Vector2(20, 58), Vector2(800, 30), 15, PALE_GOLD)
    wallet.name = "GambitPacksWallet"
    var note := _add_label(frame, "Выбери пакет. Все цены указаны в российских рублях.", Vector2(20, 92), Vector2(850, 30), 13, Color(0.82,0.79,0.72))
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

    var packs := [
        {"name":"СТАРТОВЫЙ", "amount":100, "price":99, "bonus":0, "tag":"Первое пополнение"},
        {"name":"МАЛЕНЬКИЙ", "amount":300, "price":299, "bonus":0, "tag":"Небольшой запас"},
        {"name":"СРЕДНИЙ", "amount":650, "price":599, "bonus":50, "tag":"Выгоднее"},
        {"name":"БОЛЬШОЙ", "amount":1200, "price":999, "bonus":200, "tag":"Популярный выбор"},
        {"name":"КРУПНЫЙ", "amount":2600, "price":1999, "bonus":600, "tag":"Большой запас"},
        {"name":"МАКСИМАЛЬНЫЙ", "amount":7000, "price":4999, "bonus":2000, "tag":"Максимальная выгода"}
    ]
    for i in range(packs.size()):
        var pack: Dictionary = packs[i]
        var col := i % 2
        var row := int(i / 2)
        var x1 := 0.025 + float(col) * 0.49
        var x2 := x1 + 0.46
        var y1 := 0.17 + float(row) * 0.255
        var y2 := y1 + 0.235
        var card := _panel(frame, x1, y1, x2, y2)
        var title := _add_label(card, str(pack["name"]), Vector2(12, 8), Vector2(360, 26), 14, PALE_GOLD)
        title.clip_text = true
        var total := int(pack["amount"]) + int(pack["bonus"])
        var amount_text := "%s ГАМБИТОВ" % total
        if int(pack["bonus"]) > 0:
            amount_text += "  (+%d БОНУС)" % int(pack["bonus"])
        _add_label(card, amount_text, Vector2(12, 38), Vector2(360, 30), 16, Color(0.92,0.88,0.76))
        _add_label(card, str(pack["tag"]), Vector2(12, 70), Vector2(360, 22), 11, Color(0.76,0.80,0.76))
        var buy := _ornate_button(card, "КУПИТЬ • %d ₽" % int(pack["price"]), 0.48, 0.64, 0.96, 0.94, 12, "party")
        buy.pressed.connect(_gambit_pack_purchase_unavailable.bind(int(pack["price"]), total))

func _open_gambit_packs_screen() -> void:
    if gambit_packs_panel == null:
        _build_gambit_packs_screen()
    if shop_panel:
        shop_panel.visible = false
    gambit_packs_panel.visible = true
    var wallet := gambit_packs_panel.find_child("GambitPacksWallet", true, false) as Label
    if wallet:
        wallet.text = "ТВОИ ГАМБИТЫ: %d" % int(balances.get("chessmatites", 0))

func _close_gambit_packs_screen() -> void:
    if gambit_packs_panel:
        gambit_packs_panel.visible = false
    if shop_panel:
        shop_panel.visible = true

func _gambit_pack_purchase_unavailable(price: int, amount: int) -> void:
    _show_notice("Пакет %d гамбитов за %d ₽ выбран. Реальная оплата пока не подключена — покупка не списывает деньги и не начисляет валюту." % [amount, price])

'''
s = s.replace(anchor, gambit_ui + anchor, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v88: six Gambit top-up packages in RUB, with clear bonus amounts and safe non-charging purchase placeholders.")
