from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

if "var gambit_packs_panel: Control" not in s:
    anchor = "var shop_panel: Control"
    if anchor not in s:
        raise SystemExit("v89: shop panel variable missing")
    s = s.replace(anchor, anchor + "\nvar gambit_packs_panel: Control", 1)

# Replace the entire shop builder. This also normalizes indentation after the previous shop
# action block was changed by the seasonal pass patch.
start = s.find("func _build_shop_screen() -> void:")
if start < 0:
    raise SystemExit("v89: _build_shop_screen missing")
end = s.find("\nfunc _open_shop_screen() -> void:", start)
if end < 0:
    raise SystemExit("v89: _open_shop_screen boundary missing")

new_builder = r'''func _build_shop_screen() -> void:
    shop_panel = Control.new()
    shop_panel.name = "CheckmateShop"
    shop_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shop_panel.visible = false
    ui.add_child(shop_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.97)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    shop_panel.add_child(shade)
    var frame := _panel(shop_panel, 0.035, 0.045, 0.965, 0.955)
    _add_label(frame, "МАГАЗИН • ШАХМАТНЫЙ ГОРОД", Vector2(20, 12), Vector2(650, 42), 25, PALE_GOLD)
    var back := _ornate_button(frame, "← НАЗАД", 0.82, 0.025, 0.97, 0.12, 13, "nav")
    back.pressed.connect(_close_shop_screen)
    var wallet := _add_label(frame, "ЗЛОТЫЕ  %d       ОПЫТ  %d       ГАМБИТЫ  %d" % [int(balances["zloty"]), int(balances["xp"]), int(balances["chessmatites"])], Vector2(22, 66), Vector2(850, 32), 17, PALE_GOLD)
    wallet.name = "ShopWalletSummary"
    var intro := _add_label(frame, "Премиальные покупки не заменяют исследования. Опыт нельзя купить.", Vector2(22, 105), Vector2(850, 28), 14, Color(0.82,0.79,0.72))
    intro.name = "ShopDescription"
    var cards := [
        {"title":"ГАМБИТЫ", "desc":"Пополнение премиальной валюты. Пакеты от 99 рублей.", "cta":"ВЫБРАТЬ ПАКЕТ", "kind":"gambits"},
        {"title":"ПРЕМИУМ-ПЕРСОНАЖИ", "desc":"Уникальные бойцы без обычной ветки исследований. Покупка за гамбиты.", "cta":"КОЛЛЕКЦИЯ • СКОРО", "kind":"premium"},
        {"title":"ЗОЛОТЫЕ ПАКЕТЫ", "desc":"Дополнительные злотые для развития города и обычных персонажей.", "cta":"ПАКЕТЫ • СКОРО", "kind":"gold"},
        {"title":"УНИКАЛЬНЫЕ СКИНЫ", "desc":"Постоянные визуальные облики для твоих фигур.", "cta":"СКИНЫ • СКОРО", "kind":"skins"},
        {"title":"ЕЖЕДНЕВНЫЙ СУНДУК", "desc":"Ресурсы и карточки улучшений. Редкие награды выпадают с низким шансом.", "cta":"ЗАДАНИЯ И СУНДУК", "kind":"chest"},
        {"title":"БОЕВОЙ ПРОПУСК", "desc":"Сезонные задания, бесплатные награды и премиальная дорожка.", "cta":"ОТКРЫТЬ ПРОПУСК", "kind":"pass"}
    ]
    for i in range(cards.size()):
        var item: Dictionary = cards[i]
        var col := i % 3
        var row := int(i / 3)
        var x1 := 0.025 + float(col) * 0.325
        var x2 := x1 + 0.305
        var y1 := 0.205 + float(row) * 0.355
        var y2 := y1 + 0.31
        var card := _panel(frame, x1, y1, x2, y2)
        _add_label(card, str(item["title"]), Vector2(14, 12), Vector2(270, 38), 17, PALE_GOLD)
        var desc := _add_label(card, str(item["desc"]), Vector2(14, 58), Vector2(270, 90), 13, Color(0.84,0.81,0.74))
        desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        var action := _ornate_button(card, str(item["cta"]), 0.06, 0.72, 0.94, 0.94, 11, "nav")
        if str(item["kind"]) == "gambits":
            action.pressed.connect(_open_gambit_packs_screen)
        elif str(item["kind"]) == "chest":
            action.pressed.connect(_open_daily_tasks_screen)
        elif str(item["kind"]) == "pass":
            action.pressed.connect(_open_season_pass_screen)
        else:
            action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))
'''
s = s[:start] + new_builder + s[end:]

# Ensure the dedicated package screen and callbacks exist exactly once.
if "func _build_gambit_packs_screen() -> void:" not in s:
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
    var note := _add_label(frame, "Все цены указаны в российских рублях.", Vector2(20, 92), Vector2(850, 30), 13, Color(0.82,0.79,0.72))
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
    _show_notice("Пакет %d гамбитов за %d ₽ выбран. Реальная оплата пока не подключена — деньги не списываются и валюта не начисляется." % [amount, price])

'''
    anchor = "func _open_shop_screen() -> void:"
    if anchor not in s:
        raise SystemExit("v89: insertion point for Gambit UI missing")
    s = s.replace(anchor, gambit_ui + anchor, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v89: fixed shop builder and completed RUB Gambit package page.")
