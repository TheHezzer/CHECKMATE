from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "scripts" / "main.gd"
s = path.read_text(encoding="utf-8")

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one match, found {n}")
    s = s.replace(old, new, 1)

once(
'''var vote_approve_button: Button
var vote_reject_button: Button
var prep_piece_buttons: Array[Button] = []''',
'''var vote_approve_button: Button
var vote_reject_button: Button
var match_result_panel: Control
var match_result_title: Label
var match_result_subtitle: Label
var match_result_stats: Label
var match_result_rewards: Label
var match_result_votes: Label
var prep_piece_buttons: Array[Button] = []''',
"result references")

once(
'''    _build_city_screen()
    _build_onboarding_screen()
    if not onboarding_completed:''',
'''    _build_city_screen()
    _build_onboarding_screen()
    _build_match_result_screen()
    if not onboarding_completed:''',
"result screen call")

anchor = "func _build_preparation_screen() -> void:"
functions = '''func _build_match_result_screen() -> void:
    match_result_panel = Control.new()
    match_result_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    match_result_panel.visible = false
    ui.add_child(match_result_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.006, 0.005, 0.94)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    match_result_panel.add_child(shade)
    var frame := _panel(match_result_panel, 0.07, 0.055, 0.93, 0.945)
    match_result_title = _add_label(frame, "ПОБЕДА", Vector2(24, 14), Vector2(700, 52), 30, PALE_GOLD)
    match_result_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    match_result_subtitle = _add_label(frame, "КЛАССИЧЕСКАЯ КОМАНДНАЯ ПАРТИЯ", Vector2(24, 66), Vector2(700, 28), 14, Color(0.82, 0.75, 0.63))
    match_result_subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    var stats_card := _panel(frame, 0.025, 0.19, 0.485, 0.69)
    _add_label(stats_card, "ЛИЧНАЯ СТАТИСТИКА", Vector2(16, 12), Vector2(360, 32), 18, PALE_GOLD)
    match_result_stats = _add_label(stats_card, "Ходы: 0", Vector2(18, 54), Vector2(360, 220), 14, Color(0.88, 0.83, 0.74))
    var rewards_card := _panel(frame, 0.515, 0.19, 0.975, 0.69)
    _add_label(rewards_card, "НАГРАДА ЗА ПАРТИЮ", Vector2(16, 12), Vector2(360, 32), 18, PALE_GOLD)
    match_result_rewards = _add_label(rewards_card, "Злотые: +0", Vector2(18, 54), Vector2(360, 220), 14, Color(0.88, 0.83, 0.74))
    var voting_card := _panel(frame, 0.025, 0.715, 0.975, 0.855)
    _add_label(voting_card, "КОМАНДНОЕ ГОЛОСОВАНИЕ", Vector2(16, 8), Vector2(360, 28), 16, PALE_GOLD)
    match_result_votes = _add_label(voting_card, "Голосов: 0 • Бонус: не получен", Vector2(18, 36), Vector2(680, 46), 12, Color(0.88, 0.83, 0.74))
    var back := _ornate_button(frame, "ВЕРНУТЬСЯ В МЕНЮ", 0.34, 0.88, 0.66, 0.98, 16, "party")
    back.pressed.connect(_return_to_menu)

func _show_match_result_screen(data: Dictionary) -> void:
    if match_result_panel == null:
        return
    var winner := str(data.get("winnerTeam", ""))
    var result := str(data.get("result", "finished"))
    var headline := "НИЧЬЯ" if winner == "draw" else "ПОБЕДА!" if winner == local_player_team else "ПОРАЖЕНИЕ"
    match_result_title.text = headline
    match_result_title.add_theme_color_override("font_color", Color(0.88, 0.76, 0.52) if headline != "ПОРАЖЕНИЕ" else Color(0.82, 0.62, 0.53))
    var team_name := "БЕЛЫЕ" if local_player_team == "white" else "ЧЁРНЫЕ"
    var finish_name := "МАТ" if result == "checkmate" else "ПАТ" if result == "stalemate" else "ЗАВЕРШЕНИЕ ПАРТИИ"
    match_result_subtitle.text = "КЛАССИЧЕСКИЙ РЕЖИМ • ТВОЯ КОМАНДА: %s • %s" % [team_name, finish_name]
    var personal: Dictionary = {}
    for player in data.get("players", []):
        if str(player.get("playerId", "")) == online_player_id:
            personal = player
            break
    var stats: Dictionary = personal.get("stats", {})
    var moves := int(stats.get("moves", 0))
    var captures := int(stats.get("captures", 0))
    var checks := int(stats.get("checks", 0))
    var mates := int(stats.get("checkmates", 0))
    var promotions := int(stats.get("promotions", 0))
    var castlings := int(stats.get("castlings", 0))
    var passes := int(stats.get("passes", 0))
    match_result_stats.text = "Ходы: %d\\nВзятия: %d\\nШахи: %d\\nМатующие ходы: %d\\nПревращения пешки: %d\\nРокировки: %d\\nПередачи хода: %d" % [moves, captures, checks, mates, promotions, castlings, passes]
    var reward: Dictionary = data.get("reward", {})
    var breakdown: Dictionary = reward.get("breakdown", {})
    var voting: Dictionary = breakdown.get("voting", {})
    var vote_count := int(stats.get("votes", 0))
    var correct_votes := int(stats.get("correctVotes", 0))
    var vote_accuracy := int(reward.get("voteAccuracy", 0))
    var bonus_xp := int(voting.get("xp", 0))
    var bonus_zloty := int(voting.get("zloty", 0))
    if not reward.is_empty():
        match_result_rewards.text = "ЗЛОТЫЕ\\n+%d\\n\\nОПЫТ (XP)\\n+%d\\n\\nКачество ходов: %d%%\\nТактика и участие учтены в награде." % [int(reward.get("zloty", 0)), int(reward.get("xp", 0)), int(reward.get("accuracy", 0))]
        match_result_votes.text = "Отдано голосов: %d • Совпало с решением команды: %d • Точность: %d%%\\nБонус за голосование: +%d XP и +%d злотых" % [vote_count, correct_votes, vote_accuracy, bonus_xp, bonus_zloty]
        var reward_city: Dictionary = reward.get("city", {})
        if not reward_city.is_empty():
            _apply_city_profile(reward_city)
    else:
        match_result_rewards.text = "Награда появится после авторизации.\\nВойди в аккаунт, чтобы сохранять злотые и опыт."
        match_result_votes.text = "Отдано голосов: %d • Совпало с решением команды: %d • Точность: %d%%" % [vote_count, correct_votes, vote_accuracy]
    if selected_mode != "Командное голосование":
        match_result_votes.text = "Обычная классическая партия — голосование в этом матче не использовалось."
    elif vote_count < 3 or vote_accuracy < 75:
        match_result_votes.text += "\\nУсловие бонуса: минимум 3 голоса и точность от 75%."
    game_panel.visible = false
    match_result_panel.visible = true

'''
if s.count(anchor) != 1:
    raise SystemExit("result functions insertion point not found")
s = s.replace(anchor, functions + anchor, 1)

once(
'''    if game_over_panel:
        game_over_panel.visible = false
    _refresh_team_turn_label()''',
'''    if game_over_panel:
        game_over_panel.visible = false
    if match_result_panel:
        match_result_panel.visible = false
    _refresh_team_turn_label()''',
"hide old result overlay")

once(
'''    if data.get("status", "active") == "finished":
        game_over = true
        if game_state_poll_timer: game_state_poll_timer.stop()
        var result := str(data.get("result", ""))
        status_label.text = "ПАРТИЯ ЗАВЕРШЕНА • " + ("ПОБЕДА БЕЛЫХ" if data.get("winnerTeam", "") == "white" else "ПОБЕДА ЧЁРНЫХ" if data.get("winnerTeam", "") == "black" else "НИЧЬЯ") + " • " + result
        var reward: Variant = data.get("reward", null)
        if reward is Dictionary:
            status_label.text += "\\nТВОЯ НАГРАДА: +%d XP • +%d ЗЛОТЫХ • КАЧЕСТВО %d%%" % [int(reward.get("xp", 0)), int(reward.get("zloty", 0)), int(reward.get("accuracy", 0))]
            if not account_token.is_empty():
                _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)''',
'''    if data.get("status", "active") == "finished":
        game_over = true
        if game_state_poll_timer: game_state_poll_timer.stop()
        _show_match_result_screen(data)''',
"open results after online match")

once(
'''    game_panel.visible = false
    menu_panel.visible = true
    _refresh_wallet_labels()''',
'''    game_panel.visible = false
    if match_result_panel:
        match_result_panel.visible = false
    menu_panel.visible = true
    _refresh_wallet_labels()''',
"close result screen on menu")

path.write_text(s, encoding="utf-8")
print("CHECKMATE v43 Classic match result screen applied")
