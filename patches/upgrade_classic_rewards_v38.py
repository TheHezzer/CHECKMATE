from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
main = root / "scripts" / "main.gd"
s = main.read_text(encoding="utf-8")

s = s.replace(
    'var match_piece_costs := {"Пешка": 0, "Конь": 0, "Слон": 0, "Ладья": 0, "Ферзь": 0, "Король": 0}',
    'var match_piece_costs := {"Пешка": 0, "Конь": 0, "Слон": 0, "Ладья": 0, "Ферзь": 0, "Король": 0}'
)
s = s.replace(
    'Открытие фигуры: XP списывается один раз.\\nПокупка перед матчем: злотые списываются за каждую партию.\\nВ Шахматном городе открытые фигуры не расходуются.',
    'Все фигуры доступны с начала игры.\\nВ обычном режиме выбирай любую дополнительную фигуру бесплатно.\\nЗдесь продаются только косметические скины без боевых бонусов.'
)

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
    if info:
        info.text = "ВЫБРАНА: " + piece_name.to_upper()
    if action:
        action.text = "ВЫБРАТЬ И НАЧАТЬ"
    if prep_status:
        prep_status.text = "Фигура доступна бесплатно. Все боевые фигуры открыты с начала игры."
    _save_economy()''')

s = replace_func(s, "_purchase_or_unlock_selected", '''func _purchase_or_unlock_selected() -> void:
    var piece_name: String = PIECES[selected_prep_piece]
    if piece_name == "Пешка":
        prep_status.text = "Пешка обязательна и уже входит в комплект. Выбери дополнительную фигуру."
        return
    selected_match_piece = piece_name
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _confirm_preparation()''')

s = replace_func(s, "_refund_pending_match_purchase", '''func _refund_pending_match_purchase() -> void:
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""''')

# Update the tutorial's explanation to match the free Classic roster.
s = s.replace(
    'Фигуры открываются за XP. Дополнительная боевая фигура покупается за злотые перед классической партией. Скины после покупки остаются навсегда. Закрытые фигуры отмечены замком.',
    'В обычной партии все боевые фигуры доступны сразу и выбираются бесплатно. За злотые можно покупать косметические скины, которые не усиливают фигуры. Прокачка характеристик будет отдельной системой Шахматного города.'
)
old_result = '        status_label.text = "ПАРТИЯ ЗАВЕРШЕНА • " + ("ПОБЕДА БЕЛЫХ" if data.get("winnerTeam", "") == "white" else "ПОБЕДА ЧЁРНЫХ" if data.get("winnerTeam", "") == "black" else "НИЧЬЯ") + " • " + result'
new_result = old_result + '''
        var reward: Variant = data.get("reward", null)
        if reward is Dictionary:
            status_label.text += "\\nТВОЯ НАГРАДА: +%d XP • +%d ЗЛОТЫХ • КАЧЕСТВО %d%%" % [int(reward.get("xp", 0)), int(reward.get("zloty", 0)), int(reward.get("accuracy", 0))]
            if not account_token.is_empty():
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
    if old_result not in s:
        raise SystemExit("Missing match reward display anchor")
    s = s.replace(old_result, new_result, 1)

main.write_text(s, encoding="utf-8")

print("CHECKMATE v38 client: all Classic pieces are free; selection only chooses the role.")
