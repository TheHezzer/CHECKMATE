from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing: " + label)
    s = s.replace(old, new, 1)

rep('var developer_mode := false\n', 'var developer_mode := false\nvar local_bot_test_active := false\n', 'temporary local bot flag')
rep('''    bot_test.visible = developer_mode
    bot_test.pressed.connect(_developer_test_local_game)''', '''    bot_test.text = "ПАРТИЯ С БОТАМИ • ВРЕМЕННО"
    bot_test.visible = true
    bot_test.pressed.connect(_developer_test_local_game)''', 'always visible temporary bot button')
rep('''    active_teammate = local_user_slot if developer_mode else randi_range(1, CLASSIC_TEAM_SIZE)''', '''    active_teammate = local_user_slot if (developer_mode or local_bot_test_active) else randi_range(1, CLASSIC_TEAM_SIZE)''', 'local player turn slot')
rep('''    local_opening_vote_active = not online_active''', '''    local_opening_vote_active = not online_active and not local_bot_test_active''', 'skip local bot opening vote')
rep('''        opening_vote_panel.visible = not online_active''', '''        opening_vote_panel.visible = not online_active and not local_bot_test_active''', 'hide local bot opening vote panel')
rep('''    if developer_mode and game_hint_label:''', '''    if (developer_mode or local_bot_test_active) and game_hint_label:''', 'local bot player hint')
rep('''            if developer_mode and (current_team != local_user_team or active_teammate != local_user_slot or int(target_piece.get_meta("owner_slot", 0)) != local_user_slot):''', '''            if (developer_mode or local_bot_test_active) and (current_team != local_user_team or active_teammate != local_user_slot or int(target_piece.get_meta("owner_slot", 0)) != local_user_slot):''', 'local bot ownership check')
rep('''        if developer_mode and int(target_piece.get_meta("owner_slot", 0)) != local_user_slot:''', '''        if (developer_mode or local_bot_test_active) and int(target_piece.get_meta("owner_slot", 0)) != local_user_slot:''', 'local bot teammate ownership check')
rep('''        var is_my_piece := developer_mode and str(piece.get_meta("team")) == local_user_team and int(piece.get_meta("owner_slot", 0)) == local_user_slot''', '''        var is_my_piece := (developer_mode or local_bot_test_active) and str(piece.get_meta("team")) == local_user_team and int(piece.get_meta("owner_slot", 0)) == local_user_slot''', 'local bot highlight rings')
rep('''    if developer_mode and active_teammate != local_user_slot:''', '''    if (developer_mode or local_bot_test_active) and active_teammate != local_user_slot:''', 'local bot pass turn trigger')
rep('''    if developer_mode and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):''', '''    if (developer_mode or local_bot_test_active) and not game_over and (current_team != local_user_team or active_teammate != local_user_slot):''', 'local bot team switch trigger')
rep('''    if developer_mode and active_teammate != local_user_slot:
        _schedule_local_bot_turn()''', '''    if (developer_mode or local_bot_test_active) and active_teammate != local_user_slot:
        _schedule_local_bot_turn()''', 'local bot opening turn trigger')
rep('''    if not developer_mode or game_over or local_opening_vote_active:''', '''    if not (developer_mode or local_bot_test_active) or game_over or local_opening_vote_active:''', 'local bot scheduler gate')
rep('''    if developer_mode:
        for entry in local_bot_roster:''', '''    if developer_mode or local_bot_test_active:
        for entry in local_bot_roster:''', 'bot names in turn label')
rep('''    if not developer_mode or not online_panel or not online_panel.visible:
        return
    local_bot_roster.clear()''', '''    if not (developer_mode or local_bot_test_active) or not online_panel or not online_panel.visible:
        return
    local_bot_roster.clear()''', 'local bot queue gate')
rep('''func _developer_test_local_game() -> void:
    if not developer_mode:
        return
    selected_mode = "Классика"''', '''func _developer_test_local_game() -> void:
    local_bot_test_active = true
    selected_mode = "Классика"''', 'allow guest local bot start')
rep('''func _launch_local_bot_match() -> void:
    if not developer_mode or not online_panel or not online_panel.visible:''', '''func _launch_local_bot_match() -> void:
    if not (developer_mode or local_bot_test_active) or not online_panel or not online_panel.visible:''', 'local bot match launch gate')
rep('''func _make_bot_move() -> void:
    if not developer_mode or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:''', '''func _make_bot_move() -> void:
    if not (developer_mode or local_bot_test_active) or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:''', 'local bot move gate')
rep('''    menu_panel.visible = true
    _refresh_wallet_labels()
    world_root.visible = false''', '''    menu_panel.visible = true
    local_bot_test_active = false
    local_bot_roster.clear()
    if bot_match_timer:
        bot_match_timer.stop()
    if bot_turn_timer:
        bot_turn_timer.stop()
    _refresh_wallet_labels()
    world_root.visible = false''', 'clear temporary bot mode on menu exit')

p.write_text(s, encoding="utf-8")
print("CHECKMATE temporary offline bot mode patch applied")
