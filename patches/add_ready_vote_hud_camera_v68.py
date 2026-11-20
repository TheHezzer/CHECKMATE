from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
main_path = ROOT / "scripts" / "main.gd"
s = main_path.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing main.gd anchor: " + label)
    s = s.replace(old, new, 1)

# A distinct 20-second ready phase before opening selection / first action.
rep("var local_opening_vote_seconds := 20.0\n", "var local_opening_vote_seconds := 20.0\nvar local_ready_seconds := 20.0\nvar local_ready_active := false\nvar team_vote_side_panel: Control\nvar team_vote_side_label: Label\n", "ready and vote panel state")

rep('''    vote_reject_button.pressed.connect(_cast_team_vote.bind("reject"))''', '''    vote_reject_button.pressed.connect(_cast_team_vote.bind("reject"))
    team_vote_side_panel = _panel(game_panel, 0.765, 0.31, 0.985, 0.79)
    team_vote_side_panel.name = "TeamVoteRightColumn"
    team_vote_side_panel.visible = false
    team_vote_side_label = _add_label(team_vote_side_panel, "ПРЕДЛОЖЕНИЕ КОМАНДЫ", Vector2(10, 10), Vector2(260, 42), 16, PALE_GOLD)
    team_vote_side_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    team_vote_side_label.size = Vector2(260, 250)
    team_vote_side_label.add_theme_font_size_override("font_size", 17)
    team_vote_side_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP''', "right vote panel")

# Local game: 20 sec gathering/loading, then the existing opening first-player vote.
rep('''    local_opening_vote_seconds = 20.0
    local_opening_vote_active = not online_active and not local_bot_test_active''', '''    local_opening_vote_seconds = 20.0
    local_ready_seconds = 20.0
    local_ready_active = not online_active
    local_opening_vote_active = not online_active''', "local ready timer initialization")
rep('''        opening_vote_panel.visible = not online_active and not local_bot_test_active''', '''        opening_vote_panel.visible = false''', "hide opening vote during ready countdown")
rep('''    if local_opening_vote_active:
        local_opening_vote_seconds = maxf(0.0, local_opening_vote_seconds - dt)''', '''    if local_ready_active:
        local_ready_seconds = maxf(0.0, local_ready_seconds - dt)
        if player_clock_label:
            player_clock_label.text = "ИГРОКИ ГОТОВЯТСЯ: %02d СЕК." % int(ceil(local_ready_seconds))
        if opening_vote_label:
            opening_vote_label.text = "ПОДГОТОВКА К ПАРТИИ • %02d СЕК." % int(ceil(local_ready_seconds))
        if local_ready_seconds <= 0.0:
            local_ready_active = false
            if opening_vote_panel:
                opening_vote_panel.visible = true
            if player_clock_label:
                player_clock_label.text = "ВЫБОР ПЕРВОГО ХОДА"
        return
    if local_opening_vote_active:
        local_opening_vote_seconds = maxf(0.0, local_opening_vote_seconds - dt)''', "local ready countdown phase")
# Online ready countdown comes from the authoritative match server.
rep('''    var opening_vote: Dictionary = data.get("openingVote", {})
    if opening_vote_panel:
        opening_vote_panel.visible = not opening_vote.is_empty()
    if not opening_vote.is_empty():''', '''    var ready_remaining := int(data.get("readyCountdownMs", 0))
    if ready_remaining > 0:
        if player_clock_label:
            player_clock_label.text = "ИГРОКИ ГОТОВЯТСЯ: %02d СЕК." % int(ceil(float(ready_remaining) / 1000.0))
        if opening_vote_label:
            opening_vote_label.text = "ПОДГОТОВКА К ПАРТИИ • %02d СЕК." % int(ceil(float(ready_remaining) / 1000.0))
    var opening_vote: Dictionary = data.get("openingVote", {})
    if opening_vote_panel:
        opening_vote_panel.visible = not opening_vote.is_empty() and ready_remaining <= 0
    if not opening_vote.is_empty() and ready_remaining <= 0:''', "online ready countdown display")

# Right-side team vote column: show the proposed figure, coordinates, discussion and tally.
rep('''    var pending_vote: Dictionary = data.get("pendingVote", {})
    var voting_active := selected_mode == "Командное голосование" and not pending_vote.is_empty()''', '''    var pending_vote: Dictionary = data.get("pendingVote", {})
    var voting_active := selected_mode == "Командное голосование" and not pending_vote.is_empty()
    if team_vote_side_panel:
        team_vote_side_panel.visible = voting_active
    if voting_active and team_vote_side_label:
        var move_data: Dictionary = pending_vote.get("move", {})
        var from_file := int(move_data.get("fromFile", 0))
        var from_row := int(move_data.get("fromRow", 0))
        var to_file := int(move_data.get("toFile", 0))
        var to_row := int(move_data.get("toRow", 0))
        var files := ["A","B","C","D","E","F","G","H"]
        var piece_name := "Фигура"
        for board_piece in data.get("board", []):
            if int(board_piece.get("file", -1)) == to_file and int(board_piece.get("row", -1)) == to_row:
                piece_name = str(board_piece.get("kind", piece_name))
                break
        var phase_end := int(pending_vote.get("discussionEndsAt", 0))
        var is_discussion := int(Time.get_unix_time_from_system() * 1000.0) < phase_end
        var seconds_left := int(ceil(float((phase_end if is_discussion else int(pending_vote.get("expiresAt", 0))) - int(Time.get_unix_time_from_system() * 1000.0)) / 1000.0))
        team_vote_side_label.text = "ГОЛОСОВАНИЕ\n\nПРЕДЛОЖЕННЫЙ ХОД\n%s\n%s%d  →  %s%d\n\n%s • %d сек.\n\nЗА: %d\nПРОТИВ: %d\n\nГОЛОСОВ НУЖНО: %d" % [
            piece_name, files[clampi(from_file,0,7)], 8-from_row, files[clampi(to_file,0,7)], 8-to_row,
            "ОБСУЖДЕНИЕ" if is_discussion else "ГОЛОСОВАНИЕ", maxi(0,seconds_left),
            int(pending_vote.get("approveCount",0)), int(pending_vote.get("rejectCount",0)), int(pending_vote.get("requiredVotes",5))
        ]''', "right-side vote details")

# Make game labels larger but give them separate vertical lanes; increase left menu card text.
rep('''    team_turn_label.anchor_top = 0.12
    team_turn_label.anchor_bottom = 0.12''', '''    team_turn_label.anchor_top = 0.105
    team_turn_label.anchor_bottom = 0.105''', "move turn label upward")
rep('''    game_hint_label.anchor_top = 0.17
    game_hint_label.anchor_bottom = 0.17''', '''    game_hint_label.anchor_top = 0.145
    game_hint_label.anchor_bottom = 0.145''', "move hint into separate lane")
rep('''    team_clock_label.anchor_top = 0.215
    team_clock_label.anchor_bottom = 0.215''', '''    team_clock_label.anchor_top = 0.185
    team_clock_label.anchor_bottom = 0.185''', "move team clock")
rep('''    player_clock_label.anchor_top = 0.255
    player_clock_label.anchor_bottom = 0.255''', '''    player_clock_label.anchor_top = 0.225
    player_clock_label.anchor_bottom = 0.225''', "move player clock")
# Board view: slightly lower camera, centered 45-degree elevated perspective, keeping all 64 squares in frame.
s = s.replace("camera.position = Vector3(0, 13.2, 11.9)", "camera.position = Vector3(0, 12.4, 12.4)", 1)
s = s.replace("camera.fov = 47.0", "camera.fov = 49.0", 1)
# Rotate central preview figure to a 45-degree Y angle whenever it is recreated.
if "preview_pawn.rotation.y = deg_to_rad(45.0)" not in s:
    anchor = "    _build_preview_piece(name)"
    if anchor in s:
        s = s.replace(anchor, anchor + "\n    if is_instance_valid(preview_pawn):\n        preview_pawn.rotation.y = deg_to_rad(45.0)", 1)

# Improve left menu panel labels and actions without changing their layout.
for old, new in [
    ('task_title.add_theme_font_size_override("font_size", 21)', 'task_title.add_theme_font_size_override("font_size", 24)'),
    ('task_desc.add_theme_font_size_override("font_size", 17)', 'task_desc.add_theme_font_size_override("font_size", 19)'),
    ('pass_title.add_theme_font_size_override("font_size", 21)', 'pass_title.add_theme_font_size_override("font_size", 24)'),
    ('pass_desc.add_theme_font_size_override("font_size", 17)', 'pass_desc.add_theme_font_size_override("font_size", 19)'),
    ('event_title.add_theme_font_size_override("font_size", 21)', 'event_title.add_theme_font_size_override("font_size", 24)'),
    ('event_desc.add_theme_font_size_override("font_size", 17)', 'event_desc.add_theme_font_size_override("font_size", 19)'),
]:
    s = s.replace(old, new, 1)

main_path.write_text(s, encoding="utf-8")

# Server authoritative 20-second ready phase before the existing opening vote and first move.
gameplay_path = ROOT / "server" / "gameplay.js"
if not gameplay_path.exists():
    gameplay_path = ROOT.parent.parent / "server" / "gameplay.js"
g = gameplay_path.read_text(encoding="utf-8")
def grep(old, new, label):
    global g
    if old not in g:
        raise SystemExit("Missing gameplay.js anchor: " + label)
    g = g.replace(old, new, 1)

grep('''    openingVote:{createdAt:now,expiresAt:now+OPENING_VOTE_MS,defaultPlayerId:whiteStart?.playerId||"",votes:{}},''',
     '''    readyUntil:now+20_000,
    openingVote:{createdAt:now+20_000,expiresAt:now+20_000+OPENING_VOTE_MS,defaultPlayerId:whiteStart?.playerId||"",votes:{}},''',
     "create ready countdown")
grep('''    activeTurnRemainingMs:state.openingVote?0:Math.max(0,(state.playerTurnEndsAt||0)-Date.now()),
    openingVote:''',
     '''    activeTurnRemainingMs:state.openingVote?0:Math.max(0,(state.playerTurnEndsAt||0)-Date.now()),
    readyCountdownMs:Math.max(0,(state.readyUntil||0)-Date.now()),
    openingVote:''',
     "sanitize ready countdown")
grep('''  if(state.openingVote){if(now>=state.openingVote.expiresAt)resolveOpeningVote(match,now);return state;}''',
     '''  if(state.readyUntil && now < state.readyUntil){state.updatedAt=now;return state;}
  if(state.readyUntil && now >= state.readyUntil)state.readyUntil=0;
  if(state.openingVote){if(now>=state.openingVote.expiresAt)resolveOpeningVote(match,now);return state;}''',
     "clock waits for ready phase")
grep('''  if(!state.openingVote)return{status:409,error:"OPENING_VOTE_CLOSED",state:sanitizeState(state,playerId)};''',
     '''  if(state.readyUntil && now < state.readyUntil)return{status:409,error:"PLAYERS_GETTING_READY",state:sanitizeState(state,playerId)};
  if(!state.openingVote)return{status:409,error:"OPENING_VOTE_CLOSED",state:sanitizeState(state,playerId)};''',
     "block early opening vote")
gameplay_path.write_text(g, encoding="utf-8")
print("CHECKMATE v68: 20-second ready phase, separated HUD lanes, right-side vote summary, 45-degree board and menu-piece view.")
