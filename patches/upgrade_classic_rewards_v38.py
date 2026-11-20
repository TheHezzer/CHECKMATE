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
