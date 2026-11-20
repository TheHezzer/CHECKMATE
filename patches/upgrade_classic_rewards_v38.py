from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
main = root / "scripts" / "main.gd"
s = main.read_text(encoding="utf-8")

s = s.replace(
    'var match_piece_costs := {"Пешка": 0, "Конь": 180, "Слон": 220, "Ладья": 260, "Ферзь": 520, "Король": 0}',
    'var match_piece_costs := {"Пешка": 10, "Конь": 30, "Слон": 35, "Ладья": 40, "Ферзь": 55, "Король": 45}'
)
s = s.replace(
    'Открытие фигуры: XP списывается один раз.\\nПокупка перед матчем: злотые списываются за каждую партию.\\nВ Шахматном городе открытые фигуры не расходуются.',
    'Все боевые фигуры открыты с начала. Перед каждой партией покупается комплект: обязательная пешка и выбранная вторая фигура. Минимальная цена комплекта — 30 злотых.'
)
s = s.replace('"ПРАВИЛА ПОКУПКИ"', '"ПРАВИЛА ВЫБОРА"')
def replace_func(source, name, body):
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        raise SystemExit("Missing function " + name)
    end = source.find("\nfunc ", start + len(marker))
    if end < 0:
        end = len(source)
    return source[:start] + body.rstrip() + "\n" + source[end:]

s = replace_func(s, "_refresh_preparation_ui", '''func _refresh_preparation_ui() -> void:
    if preparation_panel == null:
        return
    for i in range(prep_piece_buttons.size()):
        var piece: String = ["Конь", "Слон", "Ладья", "Ферзь", "Король"][i]
        prep_piece_buttons[i].text = "✓  " + piece.to_upper()
    var piece_name: String = PIECES[selected_prep_piece]
    var info := preparation_panel.find_child("PrepSelectedLabel", true, false) as Label
    var action := preparation_panel.find_child("PrepActionButton", true, false) as Button
    var cost := int(match_piece_costs.get(piece_name, 0))
    if info:
        info.text = "КОМПЛЕКТ: ПЕШКА + " + piece_name.to_upper()
    if action:
        if pending_match_purchase and pending_match_purchase_piece == piece_name:
            action.text = "ПОДТВЕРДИТЬ И НАЧАТЬ"
        else:
            action.text = "КУПИТЬ КОМПЛЕКТ — %d ЗЛОТЫХ" % cost
    if prep_status:
        var have := int(balances["zloty"])
        if piece_name == "Конь" and have < 30:
            prep_status.text = "СТАРТОВАЯ ЗАЩИТА: комплект пешка + конь стоит 30 злотых. Баланс будет восстановлен до 30."
        else:
            prep_status.text = "РАСХОДНИК НА ОДНУ ПАРТИЮ: %d злотых\\nБаланс: %d • %s" % [cost, have, ("не хватает " + str(cost - have)) if have < cost else "средств достаточно"]
    _save_economy()''')

s = replace_func(s, "_purchase_or_unlock_selected", '''func _purchase_or_unlock_selected() -> void:
    var piece_name: String = PIECES[selected_prep_piece]
    if piece_name == "Пешка":
        prep_status.text = "Пешка обязательна. Выбери вторую фигуру для комплекта."
        return
    if pending_match_purchase and pending_match_purchase_piece == piece_name:
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
    selected_match_piece = piece_name
    balances["zloty"] = int(balances["zloty"]) - cost
    pending_match_purchase = true
    pending_match_purchase_cost = cost
    pending_match_purchase_piece = piece_name
    _save_economy()
    prep_status.text = "Комплект пешка + " + piece_name.to_lower() + " куплен на одну партию за %d злотых. При отмене поиска деньги вернутся." % cost
    _refresh_preparation_ui()''')


# Update the tutorial's explanation to match the free Classic roster.
s = s.replace(
    'Фигуры открываются за XP. Дополнительная боевая фигура покупается за злотые перед классической партией. Скины после покупки остаются навсегда. Закрытые фигуры отмечены замком.',
    'В обычной партии все боевые фигуры открыты с начала, но перед каждой партией расходуются злотые на комплект из пешки и выбранной второй фигуры. Самый дешёвый комплект стоит 30 злотых. Скины покупаются отдельно и остаются навсегда.'
)
old_result = '        status_label.text = "ПАРТИЯ ЗАВЕРШЕНА • " + ("ПОБЕДА БЕЛЫХ" if data.get("winnerTeam", "") == "white" else "ПОБЕДА ЧЁРНЫХ" if data.get("winnerTeam", "") == "black" else "НИЧЬЯ") + " • " + result'
new_result = old_result + '''
        var reward: Variant = data.get("reward", null)
        if reward is Dictionary:
            status_label.text += "\\nТВОЯ НАГРАДА: +%d XP • +%d ЗЛОТЫХ • КАЧЕСТВО %d%%" % [int(reward.get("xp", 0)), int(reward.get("zloty", 0)), int(reward.get("accuracy", 0))]
            if not account_token.is_empty():
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
'''
if old_result not in s:
    raise SystemExit("Missing match reward display anchor")
s = s.replace(old_result, new_result, 1)

main.write_text(s, encoding="utf-8")

print("CHECKMATE v39 client: Classic figures are consumables purchased before every match.")
