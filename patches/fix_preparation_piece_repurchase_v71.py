from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

if "var prep_match_purchases: Dictionary = {}" not in s:
    anchor = 'var pending_match_purchase_piece := ""'
    if anchor not in s:
        raise SystemExit("Missing purchase state variable anchor")
    s = s.replace(anchor, anchor + '\nvar prep_match_purchases: Dictionary = {}', 1)

def replace_func(name: str, next_name: str, body: str) -> None:
    global s
    start = s.index("func " + name + "(")
    end = s.index("\nfunc " + next_name + "(", start)
    s = s[:start] + body.rstrip() + "\n\n" + s[end+1:]

replace_func("_select_preparation_piece", "_refresh_preparation_ui", r'''
func _select_preparation_piece(piece_name: String) -> void:
    # Keep every piece already bought during this preparation session.
    # Switching the highlighted piece must never silently refund its purchase.
    selected_prep_piece = PIECES.find(piece_name)
    _refresh_preparation_ui()
''')

replace_func("_refresh_preparation_ui", "_purchase_or_unlock_selected", r'''
func _refresh_preparation_ui() -> void:
    if preparation_panel == null:
        return
    for i in range(prep_piece_buttons.size()):
        var piece: String = ["Конь", "Слон", "Ладья", "Ферзь", "Король"][i]
        var glyphs := ["♞", "♝", "♜", "♛", "♚"]
        var purchased := prep_match_purchases.has(piece)
        prep_piece_buttons[i].text = glyphs[i] + ("  ✓" if purchased else "")
        prep_piece_buttons[i].modulate = Color(1.0,0.88,0.56,1) if piece == PIECES[selected_prep_piece] else Color(0.78,0.78,0.78,1)
        prep_piece_buttons[i].tooltip_text = piece + (" • уже куплена на эту партию" if purchased else "")
    var piece_name: String = PIECES[selected_prep_piece]
    var info := preparation_panel.find_child("PrepSelectedLabel", true, false) as Label
    var action := preparation_panel.find_child("PrepActionButton", true, false) as Button
    var cost := int(match_piece_costs.get(piece_name, 0))
    var purchased := prep_match_purchases.has(piece_name)
    if info:
        info.text = "КОМПЛЕКТ: ♟ + " + piece_name.to_upper() + ("   •   КУПЛЕНА" if purchased else "   •   %d ЗЛОТЫХ" % cost)
    if action:
        if purchased:
            action.text = "ВЫБРАТЬ И НАЧАТЬ"
        else:
            action.text = "КУПИТЬ КОМПЛЕКТ — %d ЗЛОТЫХ" % cost
    if prep_status:
        var have := int(balances["zloty"])
        if purchased:
            prep_status.text = "ЭТА ФИГУРА УЖЕ КУПЛЕНА. Можешь переключаться между фигурами — повторно платить не нужно."
        elif piece_name == "Конь" and have < 30:
            prep_status.text = "СТАРТОВАЯ ЗАЩИТА: комплект пешка + конь стоит 30 злотых. Баланс будет восстановлен до 30."
        else:
            prep_status.text = "РАСХОДНИК НА ОДНУ ПАРТИЮ: %d злотых\nБаланс: %d • %s" % [cost, have, ("не хватает " + str(cost - have)) if have < cost else "средств достаточно"]
    _save_economy()
''')

replace_func("_purchase_or_unlock_selected", "_confirm_preparation", r'''
func _purchase_or_unlock_selected() -> void:
    var piece_name: String = PIECES[selected_prep_piece]
    if piece_name == "Пешка":
        prep_status.text = "Пешка обязательна. Выбери вторую фигуру для комплекта."
        return
    if prep_match_purchases.has(piece_name):
        selected_match_piece = piece_name
        _confirm_preparation()
        return
    var cost := int(match_piece_costs.get(piece_name, 0))
    if piece_name == "Конь" and int(balances["zloty"]) < 30:
        balances["zloty"] = 30
    if int(balances["zloty"]) < cost:
        prep_status.text = "НЕ ХВАТАЕТ ЗЛОТЫХ: нужно %d, есть %d. Комплект пешка + конь доступен за 30." % [cost, int(balances["zloty"])]
        _save_economy()
        return
    balances["zloty"] = int(balances["zloty"]) - cost
    prep_match_purchases[piece_name] = cost
    selected_match_piece = piece_name
    _save_economy()
    prep_status.text = piece_name + " куплена на эту подготовку. Теперь можешь переключаться на другие фигуры и возвращаться без повторной оплаты."
    _refresh_preparation_ui()
''')

replace_func("_confirm_preparation", "_refund_pending_match_purchase", r'''
func _confirm_preparation() -> void:
    if selected_mode not in ["Классика", "Командное голосование"]:
        prep_status.text = "Этот режим пока закрыт."
        return
    var selected_name: String = PIECES[selected_prep_piece]
    if not prep_match_purchases.has(selected_name):
        prep_status.text = "Сначала купи выбранную фигуру. Уже купленные фигуры можно выбирать бесплатно."
        return
    # Only the selected figure is consumed by this match. Return any other
    # options bought while browsing the preparation screen.
    for bought_piece in prep_match_purchases.keys():
        if str(bought_piece) != selected_name:
            balances["zloty"] = int(balances["zloty"]) + int(prep_match_purchases[bought_piece])
    var selected_cost := int(prep_match_purchases[selected_name])
    prep_match_purchases.clear()
    pending_match_purchase = true
    pending_match_purchase_cost = selected_cost
    pending_match_purchase_piece = selected_name
    selected_match_piece = selected_name
    _save_economy()
    preparation_panel.visible = false
    menu_panel.visible = false
    _open_matchmaking_queue()
    if not developer_mode:
        _start_quick_match()
''')

replace_func("_refund_pending_match_purchase", "_load_economy", r'''
func _refund_pending_match_purchase() -> void:
    var refunded_cost := 0
    for bought_piece in prep_match_purchases.keys():
        refunded_cost += int(prep_match_purchases[bought_piece])
    prep_match_purchases.clear()
    if pending_match_purchase:
        refunded_cost += pending_match_purchase_cost
    if refunded_cost <= 0:
        pending_match_purchase = false
        pending_match_purchase_cost = 0
        pending_match_purchase_piece = ""
        return
    balances["zloty"] = int(balances["zloty"]) + refunded_cost
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _save_economy()
    if prep_status:
        prep_status.text = "Подготовка отменена. Возвращено %d злотых." % refunded_cost
''')

# Clear any browsing-session purchase records after a successful match is found.
anchor = '''    pending_match_purchase_piece = ""
    _save_economy()
    local_player_team = str(payload.get("team", "white"))
'''
replacement = '''    pending_match_purchase_piece = ""
    prep_match_purchases.clear()
    _save_economy()
    local_player_team = str(payload.get("team", "white"))
'''
if anchor not in s:
    raise SystemExit("Could not find successful matchmaking purchase cleanup")
s = s.replace(anchor, replacement, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v71: bought figures remain selectable during preparation; only chosen figure is charged for the match.")
