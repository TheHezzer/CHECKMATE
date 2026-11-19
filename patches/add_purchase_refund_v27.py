from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "scripts" / "main.gd"
source = path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if old not in source:
        raise SystemExit("Patch anchor not found: " + label)
    source = source.replace(old, new, 1)

replace_once(
    'var selected_match_piece := "Пешка"\n',
    'var selected_match_piece := "Пешка"\nvar pending_match_purchase := false\nvar pending_match_purchase_cost := 0\nvar pending_match_purchase_piece := ""\n',
    "add pending match purchase state"
)

replace_once(
'''func _close_preparation() -> void:
    preparation_panel.visible = false
    menu_panel.visible = true''',
'''func _close_preparation() -> void:
    _refund_pending_match_purchase()
    preparation_panel.visible = false
    menu_panel.visible = true''',
    "refund when leaving preparation"
)

replace_once(
'''func _select_preparation_piece(piece_name: String) -> void:
    selected_prep_piece = PIECES.find(piece_name)
    _refresh_preparation_ui()''',
'''func _select_preparation_piece(piece_name: String) -> void:
    if pending_match_purchase and pending_match_purchase_piece != piece_name:
        _refund_pending_match_purchase()
    selected_prep_piece = PIECES.find(piece_name)
    _refresh_preparation_ui()''',
    "refund reservation when changing figure"
)

replace_once(
'''    if action:
        if not unlocked_pieces.has(piece_name):
            action.text = "ОТКРЫТЬ ЗА %d XP" % int(piece_unlock_xp.get(piece_name, 0))
        elif int(match_piece_costs.get(piece_name, 0)) > 0:
            action.text = "КУПИТЬ И НАЧАТЬ — %d ЗЛОТЫХ" % int(match_piece_costs[piece_name])
        else:
            action.text = "НАЧАТЬ ТЕСТОВУЮ ПАРТИЮ"''',
'''    if action:
        if pending_match_purchase and pending_match_purchase_piece == piece_name:
            action.text = "ПОДТВЕРДИТЬ И НАЧАТЬ"
        elif not unlocked_pieces.has(piece_name):
            action.text = "ОТКРЫТЬ ЗА %d XP" % int(piece_unlock_xp.get(piece_name, 0))
        elif int(match_piece_costs.get(piece_name, 0)) > 0:
            action.text = "КУПИТЬ НА ПАРТИЮ — %d ЗЛОТЫХ" % int(match_piece_costs[piece_name])
        else:
            action.text = "ВЫБРАТЬ И НАЧАТЬ ТЕСТ"''',
    "show two-step purchase confirmation"
)

replace_once(
'''    var cost := int(match_piece_costs.get(piece_name, 0))
    if int(balances["zloty"]) < cost:
        prep_status.text = "Недостаточно злотых. Нужно ещё %d." % (cost - int(balances["zloty"]))
        return
    selected_match_piece = piece_name
    balances["zloty"] = int(balances["zloty"]) - cost
    _save_economy()
    prep_status.text = piece_name + " выбрана. Списано %d злотых. Запускаем локальную тестовую партию." % cost
    _confirm_preparation()''',
'''    if pending_match_purchase and pending_match_purchase_piece == piece_name:
        selected_match_piece = piece_name
        _confirm_preparation()
        return
    var cost := int(match_piece_costs.get(piece_name, 0))
    if int(balances["zloty"]) < cost:
        prep_status.text = "Недостаточно злотых. Нужно ещё %d." % (cost - int(balances["zloty"]))
        return
    selected_match_piece = piece_name
    balances["zloty"] = int(balances["zloty"]) - cost
    pending_match_purchase = true
    pending_match_purchase_cost = cost
    pending_match_purchase_piece = piece_name
    _save_economy()
    prep_status.text = piece_name + " подготовлена. Зарезервировано %d злотых. Нажми «ПОДТВЕРДИТЬ И НАЧАТЬ». При отмене злотые вернутся." % cost
    _refresh_preparation_ui()''',
    "reserve purchase then confirm"
)

replace_once(
'''func _confirm_preparation() -> void:
    if selected_mode != "Классика":
        prep_status.text = "Этот режим ещё разрабатывается. Сейчас доступна только классическая тестовая партия."
        return
    preparation_panel.visible = false
    _start_game(selected_mode)''',
'''func _confirm_preparation() -> void:
    if selected_mode != "Классика":
        prep_status.text = "Этот режим ещё разрабатывается. Сейчас доступна только классическая тестовая партия."
        _refund_pending_match_purchase()
        return
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _save_economy()
    preparation_panel.visible = false
    _start_game(selected_mode)

func _refund_pending_match_purchase() -> void:
    if not pending_match_purchase:
        return
    balances["zloty"] = int(balances["zloty"]) + pending_match_purchase_cost
    var refunded_cost := pending_match_purchase_cost
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _save_economy()
    if prep_status:
        prep_status.text = "Подготовка отменена. Возвращено %d злотых." % refunded_cost''',
    "confirm purchase and add refund"
)

path.write_text(source, encoding="utf-8")
print("CHECKMATE v27 purchase reservation/refund patch applied.")
