from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'scripts' / 'main.gd'
s = p.read_text(encoding='utf-8')
if 'var shop_panel: Control' not in s:
    anchor = 'var wallet_hud_labels: Dictionary = {}'
    if anchor not in s: raise SystemExit('wallet vars anchor missing')
    s = s.replace(anchor, anchor + '\nvar shop_panel: Control', 1)
anchor = '    _build_city_screen()\n    _build_onboarding_screen()'
if anchor not in s: raise SystemExit('build UI shop anchor missing')
s = s.replace(anchor, '    _build_city_screen()\n    _build_shop_screen()\n    _build_onboarding_screen()', 1)
anchor = '''        if nav_names[i] == "Шахматный город":
            b.pressed.connect(_open_city_screen)
        else:
            b.disabled = true
            b.text = "🔒  " + nav_names[i].to_upper() + "\\nСКОРО"
            b.add_theme_font_size_override("font_size", 13)'''
replacement = '''        if nav_names[i] == "Шахматный город":
            b.pressed.connect(_open_city_screen)
        elif nav_names[i] == "Магазин":
            b.pressed.connect(_open_shop_screen)
        else:
            b.disabled = true
            b.text = "🔒  " + nav_names[i].to_upper() + "\\nСКОРО"
            b.add_theme_font_size_override("font_size", 13)'''
if anchor not in s: raise SystemExit('shop nav anchor missing')
s = s.replace(anchor, replacement, 1)
s = s.replace('ШАХМАТИТЫ\\n%d', 'ГАМБИТЫ\\n%d')
s = s.replace('Шахматиты — премиальная валюта', 'Гамбиты — премиальная валюта')
start = s.index('func _piece_upgrade_cost(stat: String, rank: int) -> Dictionary:')
end = s.index('\nfunc _refresh_piece_progression() -> void:', start)
new_cost = '''func _piece_upgrade_cost(stat: String, rank: int) -> Dictionary:
    var xp_steps := [50, 75, 110, 160, 230]
    var gold_steps := [250, 400, 650, 1000, 1500]
    var index := clampi(rank, 0, 4)
    var tier := 1
    if selected_piece >= 0 and selected_piece < PIECES.size():
        tier = int(_piece_progress_data(str(PIECES[selected_piece])).get("tier", 1))
    var tier_multiplier: float = [1.0, 1.5, 2.2, 3.2, 4.5][clampi(tier - 1, 0, 4)]
    var stat_multiplier := 1.0
    if stat == "shield":
        stat_multiplier = 0.9
    elif stat == "damage":
        stat_multiplier = 1.1
    return {
        "xp": int(ceil(float(xp_steps[index]) * tier_multiplier * stat_multiplier)),
        "gold": int(ceil(float(gold_steps[index]) * tier_multiplier * stat_multiplier))
    }
'''
s = s[:start] + new_cost + s[end:]
s = s.replace('''        var xp_cost := 400 * tier
        var gold_cost := 900 * tier''', '''        var xp_cost: int = [400, 800, 1400, 2200][clampi(tier - 1, 0, 3)]
        var gold_cost: int = [900, 1800, 3200, 5000][clampi(tier - 1, 0, 3)]''', 1)
s = s.replace('''    var xp_required := 400 * tier
    var gold_required := 900 * tier''', '''    var xp_required: int = [400, 800, 1400, 2200][clampi(tier - 1, 0, 3)]
    var gold_required: int = [900, 1800, 3200, 5000][clampi(tier - 1, 0, 3)]''', 1)
anchor = '    balances["zloty"]=int(wallet.get("zloty",balances["zloty"]))\n    balances["xp"]=int(wallet.get("xp",balances["xp"]))'
replacement = '    balances["zloty"]=int(wallet.get("zloty",balances["zloty"]))\n    balances["xp"]=int(wallet.get("xp",balances["xp"]))\n    balances["chessmatites"]=int(wallet.get("gambits",wallet.get("chessmatites",balances["chessmatites"])))'
if anchor not in s: raise SystemExit('city wallet sync anchor missing')
s = s.replace(anchor, replacement, 1)
shop = r'''
func _build_shop_screen() -> void:
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
        {"title":"ГАМБИТЫ", "desc":"Премиальная валюта для редких персонажей и особых предложений.", "cta":"ПОПОЛНЕНИЕ • СКОРО", "kind":"gambits"},
        {"title":"ПРЕМИУМ-ПЕРСОНАЖИ", "desc":"Уникальные бойцы без обычной ветки исследований. Покупка за гамбиты.", "cta":"КОЛЛЕКЦИЯ • СКОРО", "kind":"premium"},
        {"title":"ЗОЛОТЫЕ ПАКЕТЫ", "desc":"Дополнительные злотые для развития города и обычных персонажей.", "cta":"ПАКЕТЫ • СКОРО", "kind":"gold"},
        {"title":"УНИКАЛЬНЫЕ СКИНЫ", "desc":"Постоянные визуальные облики для твоих фигур.", "cta":"СКИНЫ • СКОРО", "kind":"skins"},
        {"title":"ЕЖЕДНЕВНЫЙ СУНДУК", "desc":"Ресурсы и карточки улучшений. Редкие награды выпадают с низким шансом.", "cta":"СУНДУК • СКОРО", "kind":"chest"},
        {"title":"БОЕВОЙ ПРОПУСК", "desc":"Сезонные задания, бесплатные награды и премиальная дорожка.", "cta":"ПРОПУСК • СКОРО", "kind":"pass"}
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
        action.pressed.connect(_shop_coming_soon.bind(str(item["kind"])))

func _open_shop_screen() -> void:
    if shop_panel == null:
        _build_shop_screen()
    menu_panel.visible = false
    shop_panel.visible = true
    var wallet := shop_panel.find_child("ShopWalletSummary", true, false) as Label
    if wallet:
        wallet.text = "ЗЛОТЫЕ  %d       ОПЫТ  %d       ГАМБИТЫ  %d" % [int(balances["zloty"]), int(balances["xp"]), int(balances["chessmatites"])]

func _close_shop_screen() -> void:
    if shop_panel:
        shop_panel.visible = false
    menu_panel.visible = true

func _shop_coming_soon(kind: String) -> void:
    var messages := {
        "gambits":"Покупка гамбитов появится после подключения безопасной оплаты и проверки транзакций.",
        "premium":"Премиальные персонажи будут добавлены после подготовки их 3D-моделей и баланса.",
        "gold":"Пакеты злотых добавим после настройки серверной экономики.",
        "skins":"Уникальные скины добавим по мере готовности моделей.",
        "chest":"Ежедневный сундук и карточки улучшений — следующий этап.",
        "pass":"Боевой пропуск подключим после системы ежедневных и сезонных заданий."
    }
    _show_notice(str(messages.get(kind, "Раздел скоро появится.")))

'''
if 'func _build_shop_screen() -> void:' not in s:
    anchor = '\nfunc _open_city_screen() -> void:'
    if anchor not in s: raise SystemExit('shop insertion point missing')
    s = s.replace(anchor, '\n' + shop + anchor, 1)
p.write_text(s, encoding='utf-8')
print('CHECKMATE v77: progressive research economy, Gambits naming and Shop screen.')
