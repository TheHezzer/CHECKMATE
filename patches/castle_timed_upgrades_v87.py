from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

if "var castle_hub_upgrade_status: Label" not in s:
    anchor = "var castle_hub_castle_level_label: Label"
    if anchor not in s:
        raise SystemExit("v87: castle level label variable missing")
    s = s.replace(anchor, anchor + "\nvar castle_hub_upgrade_status: Label\nvar castle_hub_upgrade_button: Button\nvar castle_hub_speedup_button: Button", 1)

# Give the castle screen a visible timer and a separate premium speed-up control.
anchor = '''    var upgrade := _ornate_button(frame, "УЛУЧШИТЬ ЗАМОК", 0.20, 0.72, 0.80, 0.82, 15, "nav")
    upgrade.name = "CityCastleUpgradeButton"
    upgrade.pressed.connect(_upgrade_castle_hub_castle)

    var attack := _ornate_button(frame, "⚔  НАПАСТЬ  •  10 ЭНЕРГИИ", 0.12, 0.86, 0.88, 0.97, 19, "party")'''
replacement = '''    castle_hub_upgrade_button = _ornate_button(frame, "УЛУЧШИТЬ ЗАМОК", 0.10, 0.72, 0.54, 0.82, 13, "nav")
    castle_hub_upgrade_button.name = "CityCastleUpgradeButton"
    castle_hub_upgrade_button.pressed.connect(_upgrade_castle_hub_castle)

    castle_hub_speedup_button = _ornate_button(frame, "УСКОРИТЬ ЗА ГАМБИТЫ", 0.57, 0.72, 0.90, 0.82, 12, "party")
    castle_hub_speedup_button.name = "CityCastleSpeedupButton"
    castle_hub_speedup_button.pressed.connect(_speedup_castle_hub_upgrade)

    castle_hub_upgrade_status = _add_label(frame, "Улучшение замка", Vector2(18, 0), Vector2(850, 25), 12, Color(0.84,0.81,0.74))
    castle_hub_upgrade_status.anchor_left = 0.10
    castle_hub_upgrade_status.anchor_right = 0.90
    castle_hub_upgrade_status.anchor_top = 0.82
    castle_hub_upgrade_status.anchor_bottom = 0.86
    castle_hub_upgrade_status.offset_left = 0
    castle_hub_upgrade_status.offset_right = 0
    castle_hub_upgrade_status.offset_top = 0
    castle_hub_upgrade_status.offset_bottom = 0

    var attack := _ornate_button(frame, "⚔  НАПАСТЬ  •  10 ЭНЕРГИИ", 0.12, 0.87, 0.88, 0.98, 19, "party")'''
if anchor not in s:
    raise SystemExit("v87: castle upgrade UI anchor missing")
s = s.replace(anchor, replacement, 1)

# Replace the instant castle level purchase with a persistent timed construction order.
start = s.find("func _upgrade_castle_hub_castle() -> void:")
if start < 0:
    raise SystemExit("v87: _upgrade_castle_hub_castle missing")
end = s.find("\nfunc _castle_hub_attack_pressed(", start)
if end < 0:
    raise SystemExit("v87: cannot locate end of castle upgrade function")
new_functions = r'''func _castle_hub_upgrade_duration(level: int) -> int:
    var hours: Array = [2, 6, 12, 24]
    return int(hours[clampi(level - 1, 0, 3)]) * 3600

func _castle_hub_upgrade_gambit_cost(remaining_seconds: int) -> int:
    # One Gambit removes ten minutes; a partial ten-minute block is rounded up.
    return maxi(1, int(ceil(float(maxi(0, remaining_seconds)) / 600.0)))

func _castle_hub_complete_upgrade_if_ready() -> void:
    if not castle_hub_state.has("upgrade_finish_at"):
        return
    var finish_at := int(castle_hub_state.get("upgrade_finish_at", 0))
    if int(Time.get_unix_time_from_system()) < finish_at:
        return
    var target := clampi(int(castle_hub_state.get("upgrade_target_level", 1)), 1, 5)
    castle_hub_state["castle_level"] = maxi(int(castle_hub_state.get("castle_level", 1)), target)
    castle_hub_state.erase("upgrade_finish_at")
    castle_hub_state.erase("upgrade_target_level")
    _castle_hub_save_state()
    _show_notice("Строительство завершено! Замок достиг %d уровня." % target)

func _upgrade_castle_hub_castle() -> void:
    _castle_hub_ensure_state()
    _castle_hub_complete_upgrade_if_ready()
    if castle_hub_state.has("upgrade_finish_at"):
        _show_notice("Замок уже улучшается. Дождись завершения или ускорь строительство за гамбиты.")
        _refresh_castle_hub_battle_screen()
        return
    var level := int(castle_hub_state.get("castle_level",1))
    if level >= 5:
        return
    var xp_cost: int = [500,1200,2500,5000][level-1]
    var gold_cost: int = [1500,3500,7000,14000][level-1]
    if int(balances.get("xp",0)) < xp_cost or int(balances.get("zloty",0)) < gold_cost:
        _show_notice("Для начала строительства нужно %d XP и %d злотых." % [xp_cost,gold_cost])
        return
    balances["xp"] = int(balances["xp"]) - xp_cost
    balances["zloty"] = int(balances["zloty"]) - gold_cost
    var duration := _castle_hub_upgrade_duration(level)
    castle_hub_state["upgrade_target_level"] = level + 1
    castle_hub_state["upgrade_finish_at"] = int(Time.get_unix_time_from_system()) + duration
    _castle_hub_save_state()
    _refresh_wallet_labels()
    _refresh_castle_hub_battle_screen()
    _show_notice("Строительство замка %d уровня началось. Время: %d ч. Можно ускорить за гамбиты." % [level + 1, int(duration / 3600)])

func _speedup_castle_hub_upgrade() -> void:
    _castle_hub_ensure_state()
    _castle_hub_complete_upgrade_if_ready()
    if not castle_hub_state.has("upgrade_finish_at"):
        _show_notice("Сейчас замок не улучшается.")
        _refresh_castle_hub_battle_screen()
        return
    var now := int(Time.get_unix_time_from_system())
    var finish_at := int(castle_hub_state.get("upgrade_finish_at", now))
    var remaining := maxi(0, finish_at - now)
    if remaining <= 0:
        _castle_hub_complete_upgrade_if_ready()
        _refresh_castle_hub_battle_screen()
        return
    var cost := _castle_hub_upgrade_gambit_cost(remaining)
    var gambits := int(balances.get("chessmatites", 0))
    if gambits < cost:
        _show_notice("Для мгновенного завершения нужно %d гамбитов. У тебя: %d." % [cost, gambits])
        return
    balances["chessmatites"] = gambits - cost
    _save_economy()
    castle_hub_state["upgrade_finish_at"] = now
    _castle_hub_complete_upgrade_if_ready()
    _refresh_wallet_labels()
    _refresh_castle_hub_battle_screen()
    _show_notice("Строительство ускорено! Замок улучшен.")

'''
s = s[:start] + new_functions + s[end:]

# Replace the refresh routine so it shows construction state, countdown, and the exact Gambit cost.
start = s.find("func _refresh_castle_hub_battle_screen() -> void:")
if start < 0:
    raise SystemExit("v87: _refresh_castle_hub_battle_screen missing")
end = s.find("\nfunc _castle_hub_upgrade_duration(", start)
if end < 0:
    raise SystemExit("v87: cannot locate refresh function end")
new_refresh = r'''func _refresh_castle_hub_battle_screen() -> void:
    if castle_hub_battle_panel == null:
        return
    _castle_hub_ensure_state()
    _castle_hub_complete_upgrade_if_ready()
    var level := int(castle_hub_state.get("castle_level",1))
    var energy := int(castle_hub_state.get("energy",150))
    castle_hub_energy_label.text = "ЭНЕРГИЯ  %d / 150   •   +150 КАЖДЫЙ ДЕНЬ" % energy
    castle_hub_castle_level_label.text = "ЗАМОК • УРОВЕНЬ %d" % level
    castle_hub_army_power_label.text = "СИЛА АРМИИ  %d   •   ФИГУР: %d" % [_castle_hub_army_power(), castle_hub_army.size()]
    var castle := castle_hub_battle_panel.find_child("CityCastleButton",true,false) as Button
    if castle:
        castle.text = "ЗАМОК %s\nНАЖМИ, ЧТОБЫ РАССТАВИТЬ АРМИЮ" % ["I","II","III","IV","V"][level-1]
    var running := castle_hub_state.has("upgrade_finish_at")
    var upgrade := castle_hub_upgrade_button
    if upgrade:
        if level >= 5:
            upgrade.text = "МАКСИМАЛЬНЫЙ УРОВЕНЬ"
            upgrade.disabled = true
        elif running:
            upgrade.text = "СТРОИТЕЛЬСТВО ИДЁТ"
            upgrade.disabled = true
        else:
            var xp_cost: int = [500,1200,2500,5000][level-1]
            var gold_cost: int = [1500,3500,7000,14000][level-1]
            upgrade.text = "УЛУЧШИТЬ • %d XP / %d ЗЛОТЫХ" % [xp_cost,gold_cost]
            upgrade.disabled = false
    if castle_hub_speedup_button:
        if running:
            var remaining := maxi(0, int(castle_hub_state.get("upgrade_finish_at",0)) - int(Time.get_unix_time_from_system()))
            var gambit_cost := _castle_hub_upgrade_gambit_cost(remaining)
            castle_hub_speedup_button.text = "ЗАВЕРШИТЬ • %d ГАМБИТОВ" % gambit_cost
            castle_hub_speedup_button.disabled = remaining <= 0
        else:
            castle_hub_speedup_button.text = "УСКОРЕНИЕ ЗА ГАМБИТЫ"
            castle_hub_speedup_button.disabled = true
    if castle_hub_upgrade_status:
        if running:
            var seconds_left := maxi(0, int(castle_hub_state.get("upgrade_finish_at",0)) - int(Time.get_unix_time_from_system()))
            var hours_left := int(seconds_left / 3600)
            var minutes_left := int((seconds_left % 3600) / 60)
            castle_hub_upgrade_status.text = "СТРОИТЕЛЬСТВО ДО УРОВНЯ %d • ОСТАЛОСЬ %02d Ч %02d М" % [int(castle_hub_state.get("upgrade_target_level",level+1)), hours_left, minutes_left]
        elif level >= 5:
            castle_hub_upgrade_status.text = "ЗАМОК ДОСТИГ МАКСИМАЛЬНОГО УРОВНЯ"
        else:
            var hours: Array = [2,6,12,24]
            castle_hub_upgrade_status.text = "ВРЕМЯ СЛЕДУЮЩЕГО УЛУЧШЕНИЯ: %d ЧАСА • УСКОРЕНИЕ: 1 ГАМБИТ ЗА 10 МИНУТ" % int(hours[level-1])
    var attack := castle_hub_battle_panel.find_child("CityAttackButton",true,false) as Button
    if attack:
        attack.disabled = energy < 10 or castle_hub_army.is_empty()
'''
s = s[:start] + new_refresh + s[end:]

p.write_text(s, encoding="utf-8")
print("CHECKMATE v87: castle upgrades now take real time, persist while offline, complete automatically, and can be instantly accelerated with Gambits.")
