from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

start = s.index("func _advance_team_turn() -> void:")
end = s.index("\nfunc _format_clock(", start)
new = '''func _advance_team_turn() -> void:
    if game_over:
        return
    current_team = "black" if current_team == "white" else "white"
    if standard_chess_mode_active:
        # In 1v1 chess one human controls every piece of their color and one bot
        # controls every piece of the opposite color. Never rotate team slots.
        active_teammate = local_user_slot if current_team == local_user_team else 1
    else:
        active_teammate = int(team_next_player[current_team])
        team_next_player[current_team] = (active_teammate % CLASSIC_TEAM_SIZE) + 1
    selected_game_piece = null
    _refresh_team_turn_label()
    _update_turn_highlights()
    if not local_self_play_active and (developer_mode or local_bot_test_active or local_offline_mode_active) and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):
        if bot_turn_timer == null:
            bot_turn_timer = Timer.new()
            bot_turn_timer.one_shot = true
            add_child(bot_turn_timer)
            bot_turn_timer.timeout.connect(_make_bot_move)
        bot_turn_timer.start(1.0)
'''
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("CHECKMATE v112: standard 1v1 keeps one controller per color")
