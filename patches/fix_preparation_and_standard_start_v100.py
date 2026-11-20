from pathlib import Path
import re

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v100 anchor: " + label)
    s = s.replace(old, new, 1)

# Fit the preparation screen headings and explanatory text to their actual containers.
rep('_add_label(frame, "ВЫБЕРИ ФИГУРУ ДЛЯ ЭТОЙ ПАРТИИ", Vector2(26, 112), Vector2(600, 28), 17, PALE_GOLD)',
    '_add_label(frame, "ВЫБЕРИ ФИГУРУ ДЛЯ ЭТОЙ ПАРТИИ", Vector2(26, 112), Vector2(900, 40), 10, PALE_GOLD)',
    "preparation heading")
rep('_add_label(info, "ТВОЙ КОМПЛЕКТ: ПЕШКА + ОДНА ФИГУРА", Vector2(18, 10), Vector2(620, 28), 18, PALE_GOLD)',
    '_add_label(info, "ТВОЙ КОМПЛЕКТ: ПЕШКА + ОДНА ФИГУРА", Vector2(18, 10), Vector2(880, 34), 11, PALE_GOLD)',
    "preparation info heading")
rep('_add_label(info, "ВЫБРАНА: КОНЬ", Vector2(18, 48), Vector2(420, 30), 18, PALE_GOLD)',
    '_add_label(info, "ВЫБРАНА: КОНЬ", Vector2(18, 48), Vector2(850, 32), 10, PALE_GOLD)',
    "preparation selected label")
rep('prep_status = _add_label(info, "Выбери дополнительную фигуру.", Vector2(18, 82), Vector2(570, 35), 15, Color(0.86, 0.81, 0.72))',
    'prep_status = _add_label(info, "Выбери дополнительную фигуру.", Vector2(18, 88), Vector2(900, 76), 9, Color(0.86, 0.81, 0.72))',
    "preparation status label")
rep('var action := _ornate_button(info, "КУПИТЬ КОМПЛЕКТ", 0.70, 0.70, 0.97, 0.95, 16, "party")',
    'var action := _ornate_button(info, "КУПИТЬ КОМПЛЕКТ", 0.66, 0.70, 0.97, 0.95, 10, "party")',
    "preparation action button")

# The price is already shown in the details text; keep the action caption short enough to fit.
rep('action.text = "КУПИТЬ КОМПЛЕКТ — %d ЗЛОТЫХ" % cost',
    'action.text = "КУПИТЬ КОМПЛЕКТ"',
    "short purchase caption")

# Standard 1v1 must not enter the team-piece purchase flow. Launch a local bot match directly.
old = """func _continue_to_preparation() -> void:
    mode_selection_panel.visible = false
    _open_preparation()
"""
new = """func _continue_to_preparation() -> void:
    mode_selection_panel.visible = false
    if selected_mode == "Стандартные шахматы":
        local_bot_test_active = true
        local_self_play_active = false
        local_offline_mode_active = false
        local_bot_roster.clear()
        local_user_team = "white" if randi_range(0, 1) == 0 else "black"
        local_user_slot = 1
        online_active = false
        online_match_id = ""
        online_session_token = ""
        if online_panel:
            online_panel.visible = false
        _start_game("Стандартные шахматы")
        standard_chess_mode_active = true
        local_ready_active = false
        local_opening_vote_active = false
        if player_clock_label:
            player_clock_label.visible = false
        if team_clock_label:
            team_clock_label.visible = true
            team_clock_label.text = "ТЫ ЗА " + ("БЕЛЫХ" if local_user_team == "white" else "ЧЁРНЫХ") + " • БОТ СОПЕРНИК"
        if game_hint_label:
            game_hint_label.text = "СТАНДАРТНЫЕ ШАХМАТЫ • ВЫБИРАЙ ФИГУРУ И ДОПУСТИМУЮ КЛЕТКУ"
        _refresh_team_turn_label()
        _update_turn_highlights()
        status_label.text = "Ты играешь за " + ("белых" if local_user_team == "white" else "чёрных") + ". Цвет выбран случайно."
        if current_team != local_user_team:
            _schedule_local_bot_turn()
        return
    _open_preparation()
"""
rep(old, new, "standard chess direct start")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v100: preparation layout repaired; Standard Chess starts directly against a bot with random side.")
