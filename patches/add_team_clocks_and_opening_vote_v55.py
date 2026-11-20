from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing source block: " + label)
    s = s.replace(old, new, 1)

rep("var game_hint_label: Label\n", """var game_hint_label: Label
var team_clock_label: Label
var player_clock_label: Label
var opening_vote_panel: Control
var opening_vote_label: Label
var opening_vote_option: OptionButton
var opening_vote_button: Button
var local_team_clocks := {"white": 600.0, "black": 600.0}
var local_player_seconds := 20.0
var local_opening_vote_seconds := 20.0
var local_opening_vote_active := false
var local_skipped_slots: Array[int] = []
var local_clock_timer: Timer
""", "clock state variables")

rep('''    game_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
''', '''    game_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    team_clock_label = _add_label(game_panel, "БЕЛЫЕ 10:00     ЧЁРНЫЕ 10:00", Vector2.ZERO, Vector2(620, 32), 20, PALE_GOLD)
    team_clock_label.anchor_left = 0.5
    team_clock_label.anchor_right = 0.5
    team_clock_label.anchor_top = 0.215
    team_clock_label.anchor_bottom = 0.215
    team_clock_label.offset_left = -310
    team_clock_label.offset_right = 310
    team_clock_label.offset_top = 0
    team_clock_label.offset_bottom = 32
    team_clock_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    player_clock_label = _add_label(game_panel, "ХОД ИГРОКА: 20 СЕК.", Vector2.ZERO, Vector2(420, 26), 17, Color(0.55, 0.92, 0.98))
    player_clock_label.anchor_left = 0.5
    player_clock_label.anchor_right = 0.5
    player_clock_label.anchor_top = 0.255
    player_clock_label.anchor_bottom = 0.255
    player_clock_label.offset_left = -210
    player_clock_label.offset_right = 210
    player_clock_label.offset_top = 0
    player_clock_label.offset_bottom = 26
    player_clock_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    opening_vote_panel = _panel(game_panel, 0.31, 0.32, 0.69, 0.56)
    opening_vote_panel.visible = false
    opening_vote_label = _add_label(opening_vote_panel, "БЕЛЫЕ ВЫБИРАЮТ ПЕРВОГО ИГРОКА • 20 СЕК.", Vector2(12, 10), Vector2(520, 38), 18, PALE_GOLD)
    opening_vote_option = OptionButton.new()
    opening_vote_option.position = Vector2(20, 62)
    opening_vote_option.size = Vector2(300, 48)
    opening_vote_panel.add_child(opening_vote_option)
    opening_vote_button = _ornate_button(opening_vote_panel, "ОТДАТЬ ГОЛОС", 0.55, 0.48, 0.95, 0.88, 15, "party")
    opening_vote_button.pressed.connect(_cast_opening_first_move_vote)
''', "clock and opening vote UI")

rep('''    _build_world()
    _build_ui()
''', '''    _build_world()
    _build_ui()
    local_clock_timer = Timer.new()
    local_clock_timer.wait_time = 0.1
    local_clock_timer.one_shot = false
    add_child(local_clock_timer)
    local_clock_timer.timeout.connect(_tick_local_game_clock)
''', "local clock timer")

rep('''    first_move_vote_done = true
    first_move_voted = false
    first_move_votes = {"white": 0, "black": 0}
''', '''    first_move_vote_done = false
    first_move_voted = false
    first_move_votes = {"white": 0, "black": 0}
    local_team_clocks = {"white": 600.0, "black": 600.0}
    local_player_seconds = 20.0
    local_opening_vote_seconds = 20.0
    local_opening_vote_active = not online_active
    local_skipped_slots.clear()
    if local_clock_timer:
        local_clock_timer.start()
    if opening_vote_panel:
        opening_vote_panel.visible = not online_active
        opening_vote_option.clear()
        for player_index in range(CLASSIC_TEAM_SIZE):
            opening_vote_option.add_item("Игрок %d" % (player_index + 1), player_index + 1)
        opening_vote_option.select(maxi(0, local_user_slot - 1))
        opening_vote_button.text = "ОТДАТЬ ГОЛОС"
''', "start game clocks and opening vote")

rep('''    _refresh_team_turn_label()
    menu_panel.visible = false
''', '''    _refresh_team_turn_label()
    if team_clock_label:
        team_clock_label.text = "БЕЛЫЕ 10:00     ЧЁРНЫЕ 10:00"
    if player_clock_label:
        player_clock_label.text = "ХОД ИГРОКА: 20 СЕК."
    menu_panel.visible = false
''', "initial clock labels")

# Start local game clock only after opening vote is settled.
marker = "func _refresh_team_turn_label() -> void:\n"
helpers = '''func _format_clock(seconds: float) -> String:
    var total := maxi(0, int(ceil(seconds)))
    return "%02d:%02d" % [int(total / 60), total % 60]

func _cast_opening_first_move_vote() -> void:
    if online_active and not online_match_id.is_empty():
        if local_player_team != "white":
            status_label.text = "Первый ход выбирают белые."
            return
        if opening_vote_option.selected < 0:
            return
        var candidate_index := opening_vote_option.get_item_id(opening_vote_option.selected)
        if candidate_index >= 0 and candidate_index < opening_vote_candidates.size():
            _send_matchmaking_request("game_opening_vote", "/matches/" + online_match_id + "/opening-vote", HTTPClient.METHOD_POST, {"candidatePlayerId": str(opening_vote_candidates[candidate_index].get("playerId", ""))})
        return
    if not local_opening_vote_active:
        return
    var chosen_slot := opening_vote_option.get_item_id(opening_vote_option.selected)
    active_teammate = clampi(chosen_slot, 1, CLASSIC_TEAM_SIZE)
    team_next_player["white"] = (active_teammate % CLASSIC_TEAM_SIZE) + 1
    local_opening_vote_active = false
    first_move_vote_done = true
    local_player_seconds = 20.0
    local_skipped_slots.clear()
    if opening_vote_panel:
        opening_vote_panel.visible = false
    _refresh_team_turn_label()
    _update_turn_highlights()
    status_label.text = "ГОЛОСОВАНИЕ ЗАВЕРШЕНО • ПЕРВЫМ ХОДИТ ИГРОК %d" % active_teammate
    if developer_mode and active_teammate != local_user_slot:
        _schedule_local_bot_turn()

func _schedule_local_bot_turn() -> void:
    if not developer_mode or game_over or local_opening_vote_active:
        return
    if current_team != local_user_team or active_teammate != local_user_slot:
        if bot_turn_timer == null:
            bot_turn_timer = Timer.new()
            bot_turn_timer.one_shot = true
            add_child(bot_turn_timer)
            bot_turn_timer.timeout.connect(_make_bot_move)
        bot_turn_timer.start(0.8)

func _tick_local_game_clock() -> void:
    if not game_panel or not game_panel.visible or game_over or online_active:
        return
    var dt := 0.1
    if local_opening_vote_active:
        local_opening_vote_seconds = maxf(0.0, local_opening_vote_seconds - dt)
        if opening_vote_label:
            opening_vote_label.text = "БЕЛЫЕ ВЫБИРАЮТ ПЕРВОГО ИГРОКА • %d СЕК." % int(ceil(local_opening_vote_seconds))
        if local_opening_vote_seconds <= 0.0:
            opening_vote_option.select(maxi(0, local_user_slot - 1))
            _cast_opening_first_move_vote()
        return
    local_team_clocks[current_team] = maxf(0.0, float(local_team_clocks[current_team]) - dt)
    local_player_seconds = maxf(0.0, local_player_seconds - dt)
    if team_clock_label:
        team_clock_label.text = "БЕЛЫЕ " + _format_clock(float(local_team_clocks.white)) + "     ЧЁРНЫЕ " + _format_clock(float(local_team_clocks.black))
    if player_clock_label:
        player_clock_label.text = "ХОД ИГРОКА: %02d СЕК." % int(ceil(local_player_seconds))
    if local_team_clocks[current_team] <= 0.0:
        _finish_game("ПОБЕДА ПО ВРЕМЕНИ", "Время команды " + ("БЕЛЫХ" if current_team == "black" else "ЧЁРНЫХ") + " закончилось")
        return
    if local_player_seconds <= 0.0:
        local_skipped_slots.append(active_teammate)
        if local_skipped_slots.size() >= CLASSIC_TEAM_SIZE:
            _advance_team_turn()
            local_skipped_slots.clear()
        else:
            active_teammate = (active_teammate % CLASSIC_TEAM_SIZE) + 1
            team_next_player[current_team] = (active_teammate % CLASSIC_TEAM_SIZE) + 1
            selected_game_piece = null
            _refresh_team_turn_label()
            _update_turn_highlights()
            status_label.text = "ВРЕМЯ ИГРОКА ВЫШЛО • ХОД ПЕРЕДАН СЛЕДУЮЩЕМУ"
        local_player_seconds = 20.0
        _schedule_local_bot_turn()

'''
if marker not in s:
    raise SystemExit("Missing turn label helper insertion point")
s = s.replace(marker, helpers + marker, 1)

# Each successful move switches the clock to the opponent and resets their 20-second turn.
rep('''    _advance_team_turn()
    _remember_position()
''', '''    _advance_team_turn()
    local_player_seconds = 20.0
    local_skipped_slots.clear()
    _remember_position()
''', "reset player timer after move")

# Manual pass is now a skip and consumes the current player's 20-second slot.
rep('''    active_teammate = (active_teammate % 8) + 1
    team_next_player[current_team] = (active_teammate % CLASSIC_TEAM_SIZE) + 1
''', '''    local_skipped_slots.append(active_teammate)
    if local_skipped_slots.size() >= CLASSIC_TEAM_SIZE:
        _advance_team_turn()
        local_skipped_slots.clear()
        local_player_seconds = 20.0
        return
    active_teammate = (active_teammate % 8) + 1
    team_next_player[current_team] = (active_teammate % CLASSIC_TEAM_SIZE) + 1
    local_player_seconds = 20.0
''', "manual pass consumes player slot")

# Online response dispatcher includes opening vote.
rep('''        "game_state", "game_move", "game_pass", "game_propose", "game_vote":
''', '''        "game_state", "game_move", "game_pass", "game_propose", "game_vote", "game_opening_vote":
''', "opening vote response action")

# Online clocks and opening-vote overlay are refreshed from authoritative server state.
rep('''    _refresh_team_turn_label()
    if data.get("status", "active") == "finished":
''', '''    _refresh_team_turn_label()
    var clocks: Dictionary = data.get("teamClocks", {})
    if team_clock_label and not clocks.is_empty():
        team_clock_label.text = "БЕЛЫЕ " + _format_clock(float(clocks.get("white", 600000)) / 1000.0) + "     ЧЁРНЫЕ " + _format_clock(float(clocks.get("black", 600000)) / 1000.0)
    if player_clock_label:
        player_clock_label.text = "ХОД ИГРОКА: %02d СЕК." % int(ceil(float(data.get("activeTurnRemainingMs", 20000)) / 1000.0))
    var opening_vote: Dictionary = data.get("openingVote", {})
    if opening_vote_panel:
        opening_vote_panel.visible = not opening_vote.is_empty()
    if not opening_vote.is_empty():
        var remaining := int(ceil(float(opening_vote.get("remainingMs", 0)) / 1000.0))
        if opening_vote_label:
            opening_vote_label.text = "БЕЛЫЕ ВЫБИРАЮТ ПЕРВОГО • %d СЕК. • ГОЛОСОВ: %d/8" % [remaining, int(opening_vote.get("voteCount", 0))]
        if opening_vote_button:
            opening_vote_button.visible = local_player_team == "white" and str(opening_vote.get("viewerVote", "")).is_empty()
        if opening_vote_option:
            opening_vote_option.clear()
            opening_vote_candidates = opening_vote.get("eligiblePlayers", [])
            for index in range(opening_vote_candidates.size()):
                var candidate: Dictionary = opening_vote_candidates[index]
                opening_vote_option.add_item(str(candidate.get("name", "Игрок %d" % (int(candidate.get("slot", 0)) + 1))))
                opening_vote_option.set_item_id(opening_vote_option.item_count - 1, index)
            opening_vote_option.select(0 if opening_vote_option.item_count > 0 else -1)
    if data.get("status", "active") == "finished":
''', "online clock and opening vote HUD")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v55: 10-minute team clocks, 20-second player turns, white opening vote and timeout UI.")
