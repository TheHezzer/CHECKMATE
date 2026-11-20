from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def replace_func(source: str, name: str, replacement: str) -> str:
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        raise SystemExit("Function not found: " + name)
    next_func = source.find("\nfunc ", start + len(marker))
    if next_func < 0:
        return source[:start] + replacement.rstrip() + "\n"
    return source[:start] + replacement.rstrip() + "\n" + source[next_func + 1:]

# Make the small upper-right card actionable: it represents the next character tier.
anchor = '    next_progress.name = "NextResearchProgress"\n'
if anchor not in s:
    raise SystemExit("Next-tier progress label anchor missing")
if 'NextTierUnlockButton' not in s:
    s = s.replace(anchor, anchor + '''    var next_unlock := _ornate_button(progression_next_card, "ОТКРЫТЬ УРОВЕНЬ", 0.08, 0.79, 0.92, 0.97, 12, "party")
    next_unlock.name = "NextTierUnlockButton"
    next_unlock.pressed.connect(_unlock_next_piece_tier)
''', 1)

refresh = r'''func _refresh_piece_progression() -> void:
    if selected_piece < 0 or selected_piece >= PIECES.size():
        return
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var tier := clampi(int(data.get("tier", 1)), 1, 5)
    var levels: Dictionary = data.get("levels", {})
    var base := _piece_progress_defaults(piece, tier)
    var health_level := int(levels.get("health", 0))
    var shield_level := int(levels.get("shield", 0))
    var damage_level := int(levels.get("damage", 0))
    var total := health_level + shield_level + damage_level
    var tier_names := ["ДЕРЕВО", "СТРАЖ", "ВОИН", "РЫЦАРЬ", "ЛЕГЕНДА"]
    progression_piece_label.text = "%s • ПЕРСОНАЖ %d/5 — %s" % [piece.to_upper(), tier, tier_names[tier - 1]]
    progression_stats_label.text = "ЗДОРОВЬЕ  %d     ЩИТ  %d     АТАКА  %d" % [
        int(base["health"]) + health_level * 20,
        int(base["shield"]) + shield_level * 10,
        int(base["damage"]) + damage_level * 8
    ]
    var titles := {"health":"ЗДОРОВЬЕ", "shield":"ЩИТ", "damage":"АТАКА"}
    for stat in ["health","shield","damage"]:
        var level := int(levels.get(stat, 0))
        var cost := _piece_upgrade_cost(stat, level)
        var detail: Label = progression_upgrade_buttons[stat]["detail"]
        var button: Button = progression_upgrade_buttons[stat]["button"]
        detail.text = "СТУПЕНЬ %d/5 • %d XP + %d ЗЛОТЫХ" % [level, int(cost["xp"]), int(cost["gold"])]
        button.text = "МАКСИМУМ" if level >= 5 else "УЛУЧШИТЬ"
        button.disabled = level >= 5
    var next_progress := progression_next_card.find_child("NextResearchProgress", true, false) as Label
    var next_unlock := progression_next_card.find_child("NextTierUnlockButton", true, false) as Button
    var lock_label := progression_next_card.find_child("NextResearchLock", true, false) as Label
    var next_desc := progression_next_card.find_child("NextResearchDescription", true, false) as Label
    var unlocked := total >= 15
    var max_tier := tier >= 5
    var xp_costs := [400, 800, 1400, 2200]
    var gold_costs := [900, 1800, 3200, 5000]
    if next_progress:
        next_progress.text = "15 / 15 улучшений" if unlocked else "%d / 15 улучшений" % total
    if max_tier:
        progression_next_card.modulate = Color(1,1,1,1)
        if lock_label:
            lock_label.text = "★"
        if next_desc:
            next_desc.text = "МАКСИМАЛЬНЫЙ ПЕРСОНАЖ\nВсе пять уровней этой фигуры открыты."
        if next_unlock:
            next_unlock.text = "МАКСИМУМ"
            next_unlock.disabled = true
    else:
        progression_next_card.modulate = Color(1,1,1,1) if unlocked else Color(0.72,0.72,0.72,0.92)
        if lock_label:
            lock_label.text = "🔓" if unlocked else "🔒"
        if next_desc:
            next_desc.text = "ПЕРСОНАЖ %d/5\n%s\nОткроется после исследования текущего персонажа." % [tier + 1, tier_names[tier]]
        if next_unlock:
            next_unlock.text = "ОТКРЫТЬ • %d XP / %d ЗЛ" % [xp_costs[tier - 1], gold_costs[tier - 1]]
            next_unlock.disabled = not unlocked
    progression_status_label.text = "Пятый уровень открыт. Это максимум для данной фигуры." if max_tier else ("Все характеристики исследованы. Теперь можно открыть следующего персонажа." if unlocked else "До следующего персонажа: %d из 15 улучшений. Прокачай все три характеристики до 5/5." % total)
    var wallet := progression_panel.find_child("ResearchWalletSummary", true, false) as Label
    if wallet:
        wallet.text = "ЗЛОТЫЕ  %d     ОПЫТ  %d" % [int(balances["zloty"]), int(balances["xp"])]
'''

s = replace_func(s, "_refresh_piece_progression", refresh)

unlock = r'''func _unlock_next_piece_tier() -> void:
    if selected_piece < 0 or selected_piece >= PIECES.size():
        return
    var piece: String = str(PIECES[selected_piece])
    var data := _piece_progress_data(piece)
    var tier := clampi(int(data.get("tier", 1)), 1, 5)
    var levels: Dictionary = data.get("levels", {})
    if tier >= 5:
        progression_status_label.text = "Это максимальный, пятый персонаж."
        return
    if _piece_total_level(levels) < 15:
        progression_status_label.text = "Сначала прокачай здоровье, щит и атаку до 5/5."
        return
    var xp_costs := [400, 800, 1400, 2200]
    var gold_costs := [900, 1800, 3200, 5000]
    var xp_required: int = xp_costs[tier - 1]
    var gold_required: int = gold_costs[tier - 1]
    if int(balances.get("xp", 0)) < xp_required:
        progression_status_label.text = "Для нового персонажа нужно %d XP." % xp_required
        return
    if int(balances.get("zloty", 0)) < gold_required:
        progression_status_label.text = "Для нового персонажа нужно %d злотых." % gold_required
        return
    balances["xp"] = int(balances["xp"]) - xp_required
    balances["zloty"] = int(balances["zloty"]) - gold_required
    data["tier"] = tier + 1
    data["levels"] = {"health":0,"shield":0,"damage":0}
    piece_progression[piece] = data
    _save_economy()
    progression_status_label.text = "Открыт персонаж %d/5 для фигуры %s." % [tier + 1, piece]
    _refresh_piece_progression()
'''
s = replace_func(s, "_unlock_next_piece_tier", unlock)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v80: unlockable five-tier character cards, costs and persistent tier transitions.")
