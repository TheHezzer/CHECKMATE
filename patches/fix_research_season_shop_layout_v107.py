from pathlib import Path
p = Path(__file__).resolve().parents[1] / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing anchor: " + label)
    s = s.replace(old, new, 1)

# Season pass: the shared label helper intentionally adds 17px, which made this dense screen overlap.
replace_once(
'''    _add_label(frame, "СЕЗОННЫЙ БОЕВОЙ ПРОПУСК", Vector2(18, 10), Vector2(680, 40), 24, PALE_GOLD)
    var back := _ornate_button(frame, "← В МАГАЗИН", 0.82, 0.02, 0.98, 0.105, 12, "nav")''',
'''    var season_title := _add_label(frame, "СЕЗОННЫЙ БОЕВОЙ ПРОПУСК", Vector2(18, 10), Vector2(680, 40), 24, PALE_GOLD)
    season_title.add_theme_font_size_override("font_size", 26)
    var back := _ornate_button(frame, "← В МАГАЗИН", 0.82, 0.02, 0.98, 0.105, 12, "nav")''',
"season title")
replace_once(
'''    season_pass_progress_label = _add_label(frame, "", Vector2(20, 58), Vector2(720, 30), 16, PALE_GOLD)
    season_pass_premium_status = _add_label(frame, "", Vector2(20, 90), Vector2(720, 28), 13, Color(0.82,0.79,0.72))''',
'''    season_pass_progress_label = _add_label(frame, "", Vector2(20, 58), Vector2(720, 30), 16, PALE_GOLD)
    season_pass_progress_label.add_theme_font_size_override("font_size", 17)
    season_pass_premium_status = _add_label(frame, "", Vector2(20, 90), Vector2(720, 28), 13, Color(0.82,0.79,0.72))
    season_pass_premium_status.add_theme_font_size_override("font_size", 14)''',
"season progress")
replace_once(
'''        var level := _add_label(card, "УРОВЕНЬ " + str(i + 1), Vector2(8, 4), Vector2(220, 22), 13, PALE_GOLD)
        var reward: Dictionary = rewards[i]''',
'''        var level := _add_label(card, "УРОВЕНЬ " + str(i + 1), Vector2(8, 4), Vector2(220, 22), 13, PALE_GOLD)
        level.add_theme_font_size_override("font_size", 16)
        var reward: Dictionary = rewards[i]''',
"season level")
replace_once(
'''        var free_label := _add_label(card, free_text, Vector2(8, 28), Vector2(220, 22), 10, Color(0.84,0.87,0.78))
        free_label.clip_text = true''',
'''        var free_label := _add_label(card, free_text, Vector2(8, 28), Vector2(220, 22), 10, Color(0.84,0.87,0.78))
        free_label.add_theme_font_size_override("font_size", 12)
        free_label.clip_text = true''',
"season free reward")
replace_once(
'''        var premium_label := _add_label(card, premium_text, Vector2(8, 51), Vector2(220, 22), 10, Color(0.85,0.77,0.58))
        premium_label.clip_text = true''',
'''        var premium_label := _add_label(card, premium_text, Vector2(8, 51), Vector2(220, 22), 10, Color(0.85,0.77,0.58))
        premium_label.add_theme_font_size_override("font_size", 12)
        premium_label.clip_text = true''',
"season premium reward")

# Research: reduce label sizes to fit the current and next-tier cards.
replace_once(
'''    var title := _add_label(frame, "ИССЛЕДОВАНИЕ ФИГУРЫ", Vector2(20, 12), Vector2(600, 42), 25, PALE_GOLD)
    var close := _ornate_button(frame, "×", 0.925, 0.015, 0.985, 0.105, 18, "nav")''',
'''    var title := _add_label(frame, "ИССЛЕДОВАНИЕ ФИГУРЫ", Vector2(20, 12), Vector2(600, 42), 25, PALE_GOLD)
    title.add_theme_font_size_override("font_size", 26)
    var close := _ornate_button(frame, "×", 0.925, 0.015, 0.985, 0.105, 18, "nav")''',
"research title")
replace_once(
'''    _add_label(main_card, "УРОВЕНЬ 1 • ТЕКУЩИЙ ПЕРСОНАЖ", Vector2(16, 10), Vector2(520, 34), 18, PALE_GOLD)
    progression_piece_label = _add_label(main_card, "ФИГУРА", Vector2(16, 48), Vector2(500, 38), 23, Color(0.94,0.90,0.82))
    progression_stats_label = _add_label(main_card, "", Vector2(18, 92), Vector2(500, 78), 15, Color(0.86,0.84,0.79))''',
'''    var current_level_title := _add_label(main_card, "УРОВЕНЬ 1 • ТЕКУЩИЙ ПЕРСОНАЖ", Vector2(16, 10), Vector2(520, 34), 18, PALE_GOLD)
    current_level_title.add_theme_font_size_override("font_size", 18)
    progression_piece_label = _add_label(main_card, "ФИГУРА", Vector2(16, 48), Vector2(500, 38), 23, Color(0.94,0.90,0.82))
    progression_piece_label.add_theme_font_size_override("font_size", 22)
    progression_stats_label = _add_label(main_card, "", Vector2(18, 92), Vector2(500, 78), 15, Color(0.86,0.84,0.79))
    progression_stats_label.add_theme_font_size_override("font_size", 16)''',
"research current card")
replace_once(
'''        var label := _add_label(row, str(stat["icon"]) + "  " + str(stat["title"]), Vector2(12, 4), Vector2(210, 30), 16, PALE_GOLD)
        var detail := _add_label(row, "УРОВЕНЬ 0/5", Vector2(12, 34), Vector2(210, 25), 13, Color(0.82,0.80,0.75))''',
'''        var label := _add_label(row, str(stat["icon"]) + "  " + str(stat["title"]), Vector2(12, 4), Vector2(210, 30), 16, PALE_GOLD)
        label.add_theme_font_size_override("font_size", 15)
        var detail := _add_label(row, "УРОВЕНЬ 0/5", Vector2(12, 34), Vector2(210, 25), 13, Color(0.82,0.80,0.75))
        detail.add_theme_font_size_override("font_size", 13)''',
"research stat rows")
replace_once(
'''    progression_status_label = _add_label(main_card, "Прокачай три характеристики по 5 ступеней, чтобы открыть следующий уровень.", Vector2(14, 0), Vector2(530, 34), 13, Color(0.92,0.66,0.40))
    progression_status_label.anchor_left = 0.03''',
'''    progression_status_label = _add_label(main_card, "Прокачай три характеристики по 5 ступеней, чтобы открыть следующий уровень.", Vector2(14, 0), Vector2(530, 34), 13, Color(0.92,0.66,0.40))
    progression_status_label.add_theme_font_size_override("font_size", 13)
    progression_status_label.anchor_left = 0.03''',
"research status")
replace_once(
'''    var wallet := _add_label(frame, "ЗЛОТЫЕ  %d     ОПЫТ  %d" % [int(balances["zloty"]), int(balances["xp"])], Vector2(18, 54), Vector2(560, 30), 16, PALE_GOLD)
    wallet.name = "ResearchWalletSummary"''',
'''    var wallet := _add_label(frame, "ЗЛОТЫЕ  %d     ОПЫТ  %d" % [int(balances["zloty"]), int(balances["xp"])], Vector2(18, 54), Vector2(560, 30), 16, PALE_GOLD)
    wallet.add_theme_font_size_override("font_size", 17)
    wallet.name = "ResearchWalletSummary"''',
"research wallet")

# Keep store cards readable and make the screen navigation independently testable by node names.
replace_once(
'''    _add_label(frame, "МАГАЗИН • ШАХМАТНЫЙ ГОРОД", Vector2(20, 12), Vector2(650, 42), 25, PALE_GOLD)
    var back := _ornate_button(frame, "← НАЗАД", 0.82, 0.025, 0.97, 0.12, 13, "nav")''',
'''    var shop_title := _add_label(frame, "МАГАЗИН • ШАХМАТНЫЙ ГОРОД", Vector2(20, 12), Vector2(650, 42), 25, PALE_GOLD)
    shop_title.add_theme_font_size_override("font_size", 26)
    var back := _ornate_button(frame, "← НАЗАД", 0.82, 0.025, 0.97, 0.12, 13, "nav")''',
"shop title")
replace_once(
'''    var wallet := _add_label(frame, "ЗЛОТЫЕ  %d       ОПЫТ  %d       ГАМБИТЫ  %d" % [int(balances["zloty"]), int(balances["xp"]), int(balances["chessmatites"])], Vector2(22, 66), Vector2(850, 32), 17, PALE_GOLD)
    wallet.name = "ShopWalletSummary"''',
'''    var wallet := _add_label(frame, "ЗЛОТЫЕ  %d       ОПЫТ  %d       ГАМБИТЫ  %d" % [int(balances["zloty"]), int(balances["xp"]), int(balances["chessmatites"])], Vector2(22, 66), Vector2(850, 32), 17, PALE_GOLD)
    wallet.add_theme_font_size_override("font_size", 17)
    wallet.name = "ShopWalletSummary"''',
"shop wallet")
replace_once(
'''    var intro := _add_label(frame, "Премиальные покупки не заменяют исследования. Опыт нельзя купить.", Vector2(22, 105), Vector2(850, 28), 14, Color(0.82,0.79,0.72))
    intro.name = "ShopDescription"''',
'''    var intro := _add_label(frame, "Премиальные покупки не заменяют исследования. Опыт нельзя купить.", Vector2(22, 105), Vector2(850, 28), 14, Color(0.82,0.79,0.72))
    intro.add_theme_font_size_override("font_size", 14)
    intro.name = "ShopDescription"''',
"shop intro")
replace_once(
'''        _add_label(card, str(item["title"]), Vector2(14, 12), Vector2(270, 38), 17, PALE_GOLD)
        var desc := _add_label(card, str(item["desc"]), Vector2(14, 58), Vector2(270, 90), 13, Color(0.84,0.81,0.74))
        desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART''',
'''        var card_title := _add_label(card, str(item["title"]), Vector2(14, 12), Vector2(270, 38), 17, PALE_GOLD)
        card_title.add_theme_font_size_override("font_size", 17)
        var desc := _add_label(card, str(item["desc"]), Vector2(14, 58), Vector2(270, 90), 13, Color(0.84,0.81,0.74))
        desc.add_theme_font_size_override("font_size", 13)
        desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART''',
"shop card text")
p.write_text(s, encoding="utf-8")
print("v107 UI typography patch applied")
