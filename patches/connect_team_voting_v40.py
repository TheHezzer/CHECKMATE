from pathlib import Path

root = Path(__file__).resolve().parent.parent
script_path = root / "scripts" / "main.gd"
s = script_path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    s = s.replace(old, new, 1)

replace_once(
'''var prep_status: Label
var prep_piece_buttons: Array[Button] = []''',
'''var prep_status: Label
var pass_turn_button: Button
var end_turn_button: Button
var vote_approve_button: Button
var vote_reject_button: Button
var prep_piece_buttons: Array[Button] = []''',
"vote button references")

replace_once(
'''    var pass_turn := _ornate_button(game_panel, "ПЕРЕДАТЬ ХОД СОЮЗНИКУ", 0.27, 0.88, 0.49, 0.98, 13, "nav")
    pass_turn.pressed.connect(_pass_to_teammate)
    var end_turn := _ornate_button(game_panel, "ЗАВЕРШИТЬ ХОД", 0.51, 0.88, 0.73, 0.98, 13, "party")
    end_turn.pressed.connect(_manual_end_turn)''',
'''    pass_turn_button = _ornate_button(game_panel, "ПЕРЕДАТЬ ХОД СОЮЗНИКУ", 0.27, 0.88, 0.49, 0.98, 13, "nav")
    pass_turn_button.pressed.connect(_pass_to_teammate)
    end_turn_button = _ornate_button(game_panel, "ЗАВЕРШИТЬ ХОД", 0.51, 0.88, 0.73, 0.98, 13, "party")
    end_turn_button.pressed.connect(_manual_end_turn)
    vote_approve_button = _ornate_button(game_panel, "ЗА  •  ПОДДЕРЖАТЬ", 0.27, 0.88, 0.49, 0.98, 13, "party")
    vote_approve_button.visible = false
    vote_approve_button.pressed.connect(_cast_team_vote.bind("approve"))
    vote_reject_button = _ornate_button(game_panel, "ПРОТИВ  •  ОТКЛОНИТЬ", 0.51, 0.88, 0.73, 0.98, 13, "nav")
    vote_reject_button.visible = false
    vote_reject_button.pressed.connect(_cast_team_vote.bind("reject"))''',
"voting controls")

replace_once(
'''        mode_choice_buttons[i].disabled = i > 0
        var availability := "ДОСТУПНО" if i == 0 else "СКОРО"''',
'''        mode_choice_buttons[i].disabled = i > 1
        var availability := "ДОСТУПНО" if i <= 1 else "СКОРО"''',
"enable voting mode")

replace_once(
'''        "Игрок предлагает ход, а союзники обсуждают и голосуют. За правильное командное решение предусмотрен бонус к наградам. Голосование ограничено временем.",''',
'''        "Игрок предлагает ход, а союзники обсуждают и голосуют. Большинство принимает решение; точные голоса влияют на бонус к награде.",''',
"accurate voting description")

old_condition = "if index < 0 or index > 0:"
if old_condition in s:
    s = s.replace(old_condition, "if index < 0 or index > 1:", 1)
elif "if index < 0 or index > 1:" not in s:
    raise SystemExit("mode selection index guard not found")
s = s.replace(
    "Игрок предлагает ход, а союзники обсуждают и голосуют. За правильное командное решение предусмотрен бонус к наградам. Голосование ограничено временем.",
    "Игрок предлагает ход, а союзники обсуждают и голосуют. Большинство принимает решение; точные голоса влияют на бонус к награде.",
    1
)

replace_once(
'''func _continue_to_preparation() -> void:
    if selected_mode != "Классика":
        selected_mode = "Классика"
    mode_selection_panel.visible = false''',
'''func _continue_to_preparation() -> void:
    mode_selection_panel.visible = false''',
"preserve selected mode")

replace_once(
'''    if selected_mode != "Классика":
        status_label.text = "Сетевое подключение пока доступно только для классики."
        return''',
'''    if selected_mode == "Несколько фигур":
        status_label.text = "Режим нескольких фигур подключим следующим этапом."
        return''',
"allow vote mode board input")

replace_once(
'''        _send_matchmaking_request("game_move", "/matches/" + online_match_id + "/move", HTTPClient.METHOD_POST, {"fromFile": from_col, "fromRow": from_row, "toFile": col, "toRow": row})
        status_label.text = "Ход отправлен. Ждём подтверждения сервера…"''',
'''        var move_payload := {"fromFile": from_col, "fromRow": from_row, "toFile": col, "toRow": row}
        if selected_mode == "Командное голосование":
            _send_matchmaking_request("game_propose", "/matches/" + online_match_id + "/propose", HTTPClient.METHOD_POST, move_payload)
            status_label.text = "Предложение отправлено команде. Ждём голосов…"
        else:
            _send_matchmaking_request("game_move", "/matches/" + online_match_id + "/move", HTTPClient.METHOD_POST, move_payload)
            status_label.text = "Ход отправлен. Ждём подтверждения сервера…"''',
"send proposed move")

replace_once(
'''        "game_state", "game_move", "game_pass":
            _apply_server_game_state(payload)''',
'''        "game_state", "game_move", "game_pass", "game_propose", "game_vote":
            _apply_server_game_state(payload)''',
"handle vote responses")

replace_once(
'''    _start_game("Классика")
    status_label.text = "Команды собраны. Белые ходят первыми. Сервер синхронизирует партию для всех 16 игроков."''',
'''    _start_game(selected_mode)
    status_label.text = "Команды собраны. Белые ходят первыми. Сервер синхронизирует партию для всех 16 игроков."''',
"start selected online mode")

replace_once(
'''    if queue_status_label:
        queue_status_label.text = "Входим в очередь классического режима…"''',
'''    if queue_status_label:
        queue_status_label.text = "Входим в очередь: " + selected_mode + "…"''',
"queue status mode")

replace_once(
'''        "mode": "classic",
        "piece": selected_match_piece,''',
'''        "mode": "team_vote" if selected_mode == "Командное голосование" else "classic",
        "piece": selected_match_piece,''',
"queue mode field")

replace_once(
'''    elif online_active_player_id == online_player_id:
        status_label.text = "ТВОЯ ОЧЕРЕДЬ • выбери одну из своих фигур и сделай ход."
    else:
        status_label.text = "ХОД: " + ("БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ") + " • " + active_name
    var chat_lines := PackedStringArray()''',
'''    elif online_active_player_id == online_player_id:
        status_label.text = "ТВОЯ ОЧЕРЕДЬ • выбери одну из своих фигур и сделай ход."
    else:
        status_label.text = "ХОД: " + ("БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ") + " • " + active_name
    var pending_vote: Dictionary = data.get("pendingVote", {})
    var voting_active := selected_mode == "Командное голосование" and not pending_vote.is_empty()
    if vote_approve_button:
        var already_voted := not str(pending_vote.get("viewerVote", "")).is_empty()
        var can_vote := voting_active and not _server_viewer_eliminated and not already_voted
        vote_approve_button.visible = can_vote
        vote_reject_button.visible = can_vote
        if voting_active:
            vote_approve_button.text = "ЗА  •  %d" % int(pending_vote.get("approveCount", 0))
            vote_reject_button.text = "ПРОТИВ  •  %d" % int(pending_vote.get("rejectCount", 0))
        if pass_turn_button: pass_turn_button.visible = not voting_active
        if end_turn_button: end_turn_button.visible = not voting_active
    if voting_active:
        var vote_text := "ГОЛОСОВАНИЕ • ЗА %d / ПРОТИВ %d • нужно %d" % [int(pending_vote.get("approveCount", 0)), int(pending_vote.get("rejectCount", 0)), int(pending_vote.get("requiredVotes", 5))]
        if not str(pending_vote.get("viewerVote", "")).is_empty():
            vote_text += "\nТВОЙ ГОЛОС: " + ("ЗА" if str(pending_vote.get("viewerVote")) == "approve" else "ПРОТИВ")
        status_label.text = vote_text
    var chat_lines := PackedStringArray()''',
"render vote status")

replace_once(
'''func _send_team_chat() -> void:
    if online_match_id.is_empty() or team_chat_input == null: return''',
'''func _cast_team_vote(choice: String) -> void:
    if online_match_id.is_empty() or not online_active:
        return
    if _server_viewer_eliminated:
        status_label.text = "Выбывшие игроки не голосуют."
        return
    _send_matchmaking_request("game_vote", "/matches/" + online_match_id + "/vote", HTTPClient.METHOD_POST, {"vote": choice})

func _send_team_chat() -> void:
    if online_match_id.is_empty() or team_chat_input == null: return''',
"vote callback")

script_path.write_text(s, encoding="utf-8")
print("CHECKMATE v40 client voting patch applied")
