from pathlib import Path
p=Path(__file__).resolve().parent.parent/'scripts'/'main.gd'
s=p.read_text(encoding='utf-8')
def rep(a,b,n):
 global s
 if a not in s: raise SystemExit('Missing anchor: '+n)
 s=s.replace(a,b,1)

# All chess pieces are selectable in Classic; XP unlock progression is kept separate for Chess City.
rep('var unlocked_pieces := ["Пешка"]\nvar owned_skins := ["Дерево"]','var unlocked_pieces := ["Пешка", "Ладья", "Конь", "Слон", "Ферзь", "Король"]\nvar city_unlocked_pieces := ["Пешка"]\nvar owned_skins := ["Дерево"]','classic/city inventory')
rep('        unlocked_pieces = cfg.get_value("progress", "unlocked_pieces", unlocked_pieces)\n        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)\n        competitive_rating = clampi(int(cfg.get_value("ranked", "rating", 1000)), 0, 100000)\n        persistent_player_id = str(cfg.get_value("identity", "player_id", ""))\n        onboarding_completed = bool(cfg.get_value("onboarding", "completed", false))','        city_unlocked_pieces = cfg.get_value("progress", "city_unlocked_pieces", city_unlocked_pieces)\n        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)\n        competitive_rating = clampi(int(cfg.get_value("ranked", "rating", 1000)), 0, 100000)\n        persistent_player_id = str(cfg.get_value("identity", "player_id", ""))\n        onboarding_completed = bool(cfg.get_value("onboarding", "completed", false))\n    unlocked_pieces = PIECES.duplicate()','load progression')
rep('    cfg.set_value("progress", "unlocked_pieces", unlocked_pieces)\n    cfg.set_value("progress", "owned_skins", owned_skins)','    cfg.set_value("progress", "unlocked_pieces", PIECES)\n    cfg.set_value("progress", "city_unlocked_pieces", city_unlocked_pieces)\n    cfg.set_value("progress", "owned_skins", owned_skins)','save progression')
rep('b.pressed.connect(func(): _show_notice("ШАХМАТНЫЙ ГОРОД — отдельный режим. Открытые фигуры доступны постоянно, без расхода злотых за вход."))','b.pressed.connect(func(): _show_notice("ШАХМАТНЫЙ ГОРОД: фигуры открываются за XP и покупаются отдельно внутри режима. Все фигуры классической партии доступны сразу. Скины и косметика пока закрыты."))','city rules')
rep('        var unlocked := unlocked_pieces.has(piece)\n        prep_piece_buttons[i].text = ("✓  " if unlocked else "🔒  ") + piece.to_upper()','        prep_piece_buttons[i].text = "✓  " + piece.to_upper()','prep all figures')
rep('        elif not unlocked_pieces.has(piece_name):\n            action.text = "ОТКРЫТЬ ЗА %d XP" % int(piece_unlock_xp.get(piece_name, 0))\n        elif int(match_piece_costs.get(piece_name, 0)) > 0:','        elif int(match_piece_costs.get(piece_name, 0)) > 0:','no classic XP unlock')
rep('        if not unlocked_pieces.has(piece_name):\n            var need_xp := int(piece_unlock_xp.get(piece_name, 0))\n            var have_xp := int(balances["xp"])\n            prep_status.text = "НЕ ХВАТАЕТ XP: нужно %d, есть %d, не хватает %d." % [need_xp, have_xp, maxi(0, need_xp - have_xp)]\n        elif int(match_piece_costs.get(piece_name, 0)) > 0:','        if int(match_piece_costs.get(piece_name, 0)) > 0:','prep XP status')
a=s.index('func _purchase_or_unlock_selected() -> void:')
b=s.index('\nfunc _confirm_preparation() -> void:',a)
s=s[:a]+'''func _purchase_or_unlock_selected() -> void:
    var piece_name: String = PIECES[selected_prep_piece]
    if piece_name == "Пешка":
        prep_status.text = "Пешка обязательна и уже входит в комплект. Выбери дополнительную фигуру."
        return
    if pending_match_purchase and pending_match_purchase_piece == piece_name:
        selected_match_piece = piece_name
        _confirm_preparation()
        return
    var cost := int(match_piece_costs.get(piece_name, 0))
    if int(balances["zloty"]) < cost:
        prep_status.text = "НЕ ХВАТАЕТ ЗЛОТЫХ: нужно %d, есть %d, не хватает %d." % [cost, int(balances["zloty"]), cost - int(balances["zloty"])]
        return
    selected_match_piece = piece_name
    balances["zloty"] = int(balances["zloty"]) - cost
    pending_match_purchase = true
    pending_match_purchase_cost = cost
    pending_match_purchase_piece = piece_name
    _save_economy()
    prep_status.text = piece_name + " подготовлена. Зарезервировано %d злотых. Подтверди поиск. При отмене деньги вернутся." % cost
    _refresh_preparation_ui()
''' + s[b:]

rep('var team_turn_label: Label\nvar prep_status: Label','var team_turn_label: Label\nvar first_move_vote_panel: Control\nvar first_move_vote_label: Label\nvar first_move_vote_done := false\nvar first_move_votes := {"white": 0, "black": 0}\nvar team_next_player := {"white": 1, "black": 1}\nvar first_move_voted := false\nvar queue_change_piece_button: Button\nvar prep_status: Label','vote/queue state')
rep('    _build_onboarding_screen()\n    if not onboarding_completed:','    _build_onboarding_screen()\n    _build_first_move_vote_panel()\n    if not onboarding_completed:','build vote UI')
rep('    queue_cancel_button.pressed.connect(_close_online_panel)','    queue_cancel_button.pressed.connect(_close_online_panel)\n    queue_change_piece_button = _ornate_button(frame, "СМЕНИТЬ ФИГУРУ", 0.48, 0.855, 0.72, 0.975, 13, "card")\n    queue_change_piece_button.pressed.connect(_change_queued_piece)','queue change button')
rep('            elif not online_ticket.is_empty():\n                if queue_status_label:\n                    queue_status_label.text = "Ищем 16 игроков с близким рейтингом. Не закрывай экран."\n                online_poll_timer.start()','            elif not online_ticket.is_empty():\n                if queue_status_label:\n                    queue_status_label.text = "Ищем 8 игроков в каждую команду. Если выбранная фигура занята, можно подождать или сменить её."\n                online_poll_timer.start()','queue help')
rep('            elif str(payload.get("status", "")) == "cancelled":\n                online_poll_timer.stop()\n                if queue_status_label:\n                    queue_status_label.text = "Поиск отменён."','            elif str(payload.get("status", "")) == "waiting_piece_slot":\n                if queue_status_label:\n                    queue_status_label.text = "МЕСТО ДЛЯ ФИГУРЫ «%s» ЗАНЯТО. Подожди освобождения места или нажми «СМЕНИТЬ ФИГУРУ»." % selected_match_piece.to_upper()\n            elif str(payload.get("status", "")) == "cancelled":\n                online_poll_timer.stop()\n                if queue_status_label:\n                    queue_status_label.text = "Поиск отменён."','waitlist UI')
rep('        "queue_cancel":\n            if queue_status_label:\n                queue_status_label.text = "Поиск отменён."','        "queue_cancel":\n            if queue_status_label:\n                queue_status_label.text = "Поиск отменён."\n        "queue_change_piece":\n            online_ticket = ""\n            if online_poll_timer: online_poll_timer.stop()\n            online_panel.visible = false\n            preparation_panel.visible = true\n            _refresh_preparation_ui()','queue change callback')
anchor='func _start_quick_match() -> void:'
s=s.replace(anchor,'''func _change_queued_piece() -> void:
    if online_ticket.is_empty():
        online_panel.visible = false
        preparation_panel.visible = true
        _refresh_preparation_ui()
        return
    _send_matchmaking_request("queue_change_piece", "/matchmaking/queue/" + online_ticket + "/cancel", HTTPClient.METHOD_POST)

'''+anchor,1)

anchor='func _start_game(mode_name: String) -> void:'
vote='''func _build_first_move_vote_panel() -> void:
    first_move_vote_panel = Control.new()
    first_move_vote_panel.name = "FirstMoveVote"
    first_move_vote_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    first_move_vote_panel.visible = false
    first_move_vote_panel.mouse_filter = Control.MOUSE_FILTER_STOP
    game_panel.add_child(first_move_vote_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.94)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    first_move_vote_panel.add_child(shade)
    var frame := _panel(first_move_vote_panel, 0.18, 0.24, 0.82, 0.76)
    _add_label(frame, "ГОЛОСОВАНИЕ ЗА ПЕРВЫЙ ХОД", Vector2(18,22), Vector2(680,48), 26, PALE_GOLD)
    first_move_vote_label = _add_label(frame, "Команды выбирают, какая сторона начнёт. После голосования система случайно назначит игрока №1–8.", Vector2(22,88), Vector2(650,90), 16, Color(0.88,0.83,0.75))
    var white_vote := _ornate_button(frame, "ГОЛОС ЗА БЕЛЫХ", 0.06,0.48,0.47,0.68,16,"card")
    white_vote.pressed.connect(_cast_first_move_vote.bind("white"))
    var black_vote := _ornate_button(frame, "ГОЛОС ЗА ЧЁРНЫХ", 0.53,0.48,0.94,0.68,16,"card")
    black_vote.pressed.connect(_cast_first_move_vote.bind("black"))
    var finish_vote := _ornate_button(frame, "ЗАВЕРШИТЬ ГОЛОСОВАНИЕ", 0.24,0.76,0.76,0.94,15,"party")
    finish_vote.pressed.connect(_finish_first_move_vote)

func _cast_first_move_vote(team: String) -> void:
    if first_move_vote_done or first_move_voted or not first_move_votes.has(team):
        return
    first_move_votes[team] = int(first_move_votes[team]) + 1
    first_move_voted = true
    first_move_vote_label.text = "Голоса: белые %d • чёрные %d. Нажми завершить голосование." % [int(first_move_votes["white"]), int(first_move_votes["black"])]

func _finish_first_move_vote() -> void:
    if first_move_vote_done:
        return
    var starting_team := "white"
    if int(first_move_votes["black"]) > int(first_move_votes["white"]):
        starting_team = "black"
    elif int(first_move_votes["black"]) == int(first_move_votes["white"]):
        starting_team = "white" if randi_range(0,1) == 0 else "black"
    current_team = starting_team
    active_teammate = randi_range(1, CLASSIC_TEAM_SIZE)
    var other_team := "black" if starting_team == "white" else "white"
    team_next_player[starting_team] = (active_teammate % CLASSIC_TEAM_SIZE) + 1
    team_next_player[other_team] = randi_range(1, CLASSIC_TEAM_SIZE)
    first_move_vote_done = true
    first_move_vote_panel.visible = false
    _refresh_team_turn_label()
    status_label.text = "Первый ход: %s, случайно выбран игрок №%d. Далее ход передаётся по порядку." % ["белые" if current_team == "white" else "чёрные", active_teammate]
    _update_turn_highlights()

'''
if anchor not in s: raise SystemExit('Missing start-game anchor')
s=s.replace(anchor,vote+anchor,1)
rep('    current_team = "white"\n    active_teammate = 1','    current_team = "white"\n    active_teammate = 1\n    first_move_vote_done = false\n    first_move_voted = false\n    first_move_votes = {"white": 0, "black": 0}\n    team_next_player = {"white": 1, "black": 1}','reset opening vote')
rep('    _update_turn_highlights()\n    _remember_position()','    _update_turn_highlights()\n    if first_move_vote_panel:\n        first_move_vote_panel.visible = true\n    _remember_position()','show vote before board input')
rep('    if game_panel != null and game_panel.visible and world_root.visible:\n        if event is InputEventScreenTouch','    if game_panel != null and game_panel.visible and world_root.visible:\n        if not first_move_vote_done:\n            return\n        if event is InputEventScreenTouch','block moves before vote')
rep('    active_teammate = (active_teammate % 8) + 1\n    selected_game_piece = null','    active_teammate = (active_teammate % 8) + 1\n    team_next_player[current_team] = (active_teammate % CLASSIC_TEAM_SIZE) + 1\n    selected_game_piece = null','pass turn sequence')
rep('    current_team = "black" if current_team == "white" else "white"\n    active_teammate = 1','    current_team = "black" if current_team == "white" else "white"\n    active_teammate = int(team_next_player[current_team])\n    team_next_player[current_team] = (active_teammate % CLASSIC_TEAM_SIZE) + 1','alternate team sequence')
rep('"В команде 8 игроков. У каждого две фигуры: своя пешка и одна выбранная дополнительная фигура. Всего на стороне 16 фигур. После обучения открыты пешка и конь; остальные фигуры нужно открыть."','"В команде 8 игроков. У каждого две фигуры: обязательная пешка и одна дополнительная на выбор. Все типы фигур доступны в классике. В Шахматном городе фигуры открываются за XP и покупаются отдельно; скины остаются закрытыми до получения."','tutorial rules')
rep('_show_notice("Обучение завершено! Пешка и конь открыты. Награда: 500 злотых и 100 XP.")','_show_notice("Обучение завершено! Все типы фигур доступны в классике. Награда: 500 злотых и 100 XP.")','tutorial reward')
rep('    if not unlocked_pieces.has("Конь"): unlocked_pieces.append("Конь")','    unlocked_pieces = PIECES.duplicate()','all classic pieces after tutorial')

p.write_text(s,encoding='utf-8')
print('CHECKMATE v34 patch applied')
