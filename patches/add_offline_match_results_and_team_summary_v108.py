from pathlib import Path
p = Path(__file__).resolve().parents[1] / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing: " + label)
    s = s.replace(old, new, 1)

rep('var match_result_votes: Label\n','var match_result_votes: Label\nvar match_result_team: Label\n','result team label variable')
rep('''    match_result_stats = _add_label(stats_card, "Ходы: 0", Vector2(18, 54), Vector2(360, 220), 14, Color(0.88, 0.83, 0.74))
    var rewards_card := _panel(frame, 0.515, 0.19, 0.975, 0.69)''','''    match_result_stats = _add_label(stats_card, "Ходы: 0", Vector2(18, 54), Vector2(360, 220), 14, Color(0.88, 0.83, 0.74))
    _add_label(stats_card, "РЕЗУЛЬТАТ КОМАНДЫ", Vector2(16, 286), Vector2(360, 26), 15, PALE_GOLD)
    match_result_team = _add_label(stats_card, "Командная статистика появится после завершения матча.", Vector2(18, 318), Vector2(360, 150), 12, Color(0.84, 0.81, 0.74))
    match_result_team.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var rewards_card := _panel(frame, 0.515, 0.19, 0.975, 0.69)''','result team panel')
rep('''    if not reward.is_empty():
        match_result_rewards.text = "ЗЛОТЫЕ\\n+%d\\n\\nОПЫТ (XP)\\n+%d\\n\\nКачество ходов: %d%%\\nТактика и участие учтены в награде." % [int(reward.get("zloty", 0)), int(reward.get("xp", 0)), int(reward.get("accuracy", 0))]''','''    var rating_delta := int(reward.get("ratingDelta", 0))
    if not reward.is_empty():
        match_result_rewards.text = "ЗЛОТЫЕ\\n+%d\\n\\nОПЫТ (XP)\\n+%d\\n\\nРЕЙТИНГ\\n%s%d\\n\\nКачество ходов: %d%%" % [int(reward.get("zloty", 0)), int(reward.get("xp", 0)), "+" if rating_delta >= 0 else "", rating_delta, int(reward.get("accuracy", 0))]''','result reward includes rating')
rep('''    if selected_mode != "Командное голосование":
        match_result_votes.text = "Обычная классическая партия — голосование в этом матче не использовалось."''','''    var team_lines: Array[String] = []
    for player in data.get("players", []):
        if str(player.get("team", "")) != local_player_team:
            continue
        var player_stats: Dictionary = player.get("stats", {})
        var player_name := str(player.get("name", player.get("playerId", "Игрок")))
        var abandoned_tag := " • ВЫШЕЛ" if bool(player.get("abandoned", false)) else ""
        team_lines.append("%s • %d ходов • %d взятий%s" % [player_name, int(player_stats.get("moves", 0)), int(player_stats.get("captures", 0)), abandoned_tag])
    match_result_team.text = "\\n".join(team_lines) if not team_lines.is_empty() else "Нет данных о составе команды."
    if selected_mode != "Командное голосование":
        match_result_votes.text = "Обычная классическая партия — голосование в этом матче не использовалось."''','team stats list')
rep('''func _finish_game(title_text: String, detail_text: String) -> void:
    game_over = true
    selected_game_piece = null
    status_label.text = title_text + " — " + detail_text
    _show_game_over(title_text, detail_text)
''','''func _finish_game(title_text: String, detail_text: String) -> void:
    game_over = true
    selected_game_piece = null
    status_label.text = title_text + " — " + detail_text
    if local_bot_test_active or local_offline_mode_active or local_self_play_active:
        _show_local_match_result_screen(title_text, detail_text)
    else:
        _show_game_over(title_text, detail_text)

func _show_local_match_result_screen(title_text: String, detail_text: String) -> void:
    if match_result_panel == null:
        _show_game_over(title_text, detail_text)
        return
    var winner := "white" if detail_text.contains("БЕЛЫХ") else "black" if detail_text.contains("ЧЁРНЫХ") else "draw"
    var headline := "ПАРТИЯ ЗАВЕРШЕНА" if local_self_play_active else "ПОБЕДА!" if winner == local_user_team else "ПОРАЖЕНИЕ" if winner != "draw" else "НИЧЬЯ"
    match_result_title.text = headline
    match_result_title.add_theme_color_override("font_color", PALE_GOLD)
    match_result_subtitle.text = "ОФЛАЙН-ТЕСТ • " + selected_mode.to_upper() + " • " + title_text
    match_result_stats.text = detail_text + "\\n\\nПартия завершена локально. Ходы и правила проверены без подключения к серверу."
    match_result_team.text = "ТЕСТОВЫЙ СОСТАВ\\n" + ("Ты управлял обеими сторонами." if local_self_play_active else "Игрок: " + ("БЕЛЫЕ" if local_user_team == "white" else "ЧЁРНЫЕ") + "\\nОстальные участники: боты.")
    match_result_rewards.text = "ОФЛАЙН-ТЕСТ\\nНаграды и рейтинг не начисляются, чтобы нельзя было накручивать экономику без сервера."
    match_result_votes.text = "Режим проверки: локальная партия. Для теста голосования и серверных наград используется встроенный автоматический набор тестов."
    game_panel.visible = false
    match_result_panel.visible = true
''','offline results summary')
p.write_text(s, encoding="utf-8")
print("CHECKMATE v108: offline match results and team/rating summary applied")
