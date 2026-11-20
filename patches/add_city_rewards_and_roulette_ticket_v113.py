from pathlib import Path

p = Path(__file__).resolve().parents[1] / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("CHECKMATE v113 missing anchor: " + label)
    s = s.replace(old, new, 1)

rep('var balances := {"zloty": 12750, "xp": 850, "chessmatites": 620}\n',
    'var balances := {"zloty": 12750, "xp": 850, "chessmatites": 620}\nvar roulette_spins := 0\n',
    "roulette spin wallet")
rep('        balances["chessmatites"] = int(cfg.get_value("wallet", "chessmatites", balances["chessmatites"]))\n',
    '        balances["chessmatites"] = int(cfg.get_value("wallet", "chessmatites", balances["chessmatites"]))\n        roulette_spins = maxi(0, int(cfg.get_value("wallet", "roulette_spins", roulette_spins)))\n',
    "load roulette spins")
rep('    cfg.set_value("wallet", "chessmatites", balances["chessmatites"])\n',
    '    cfg.set_value("wallet", "chessmatites", balances["chessmatites"])\n    cfg.set_value("wallet", "roulette_spins", roulette_spins)\n',
    "save roulette spins")

old = '''func _city_offline_end_battle(player_won: bool) -> void:
    city_offline_active = false
    city_offline_busy = false
    city_offline_status.text = "ПОБЕДА • ТРЕНИРОВКА" if player_won else "ПОРАЖЕНИЕ • ТРЕНИРОВКА"
    _city_offline_log("Бой завершён. Это офлайн-тест: злотые, XP и рейтинг не начисляются.")
    _city_offline_refresh()
    _show_notice("ПОБЕДА!" if player_won else "ПОРАЖЕНИЕ" + "\\nТренировочный бой завершён. Награды не начисляются.")
'''
new = '''func _city_offline_end_battle(player_won: bool) -> void:
    if not city_offline_active:
        return
    city_offline_active = false
    city_offline_busy = false
    var reward_zloty := 300 if player_won else 150
    var reward_xp := 120 if player_won else 60
    balances["zloty"] = int(balances.get("zloty", 0)) + reward_zloty
    balances["xp"] = int(balances.get("xp", 0)) + reward_xp
    if player_won:
        roulette_spins += 1
    _save_economy()
    city_offline_status.text = "ПОБЕДА • НАГРАДА" if player_won else "ПОРАЖЕНИЕ • НАГРАДА"
    var reward_text := "Награда: %d злотых и %d XP." % [reward_zloty, reward_xp]
    if player_won:
        reward_text += " Рулетка: +1 бесплатное вращение."
    _city_offline_log("Бой завершён. " + reward_text)
    _city_offline_refresh()
    _show_notice(("ПОБЕДА!\\n" if player_won else "ПОРАЖЕНИЕ\\n") + reward_text)
'''
rep(old, new, "Chess City battle reward settlement")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v113 Chess City rewards and persistent roulette ticket counter applied")
