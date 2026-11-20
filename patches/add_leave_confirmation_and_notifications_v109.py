from pathlib import Path
p = Path(__file__).resolve().parents[1] / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing: " + label)
    s = s.replace(old, new, 1)

rep('var match_result_team: Label\n','var match_result_team: Label\nvar leave_confirmation_panel: Control\nvar leave_match_confirmed := false\n','leave confirmation variables')
rep('''    _build_match_result_screen()
    _build_match_history_screen()''','''    _build_match_result_screen()
    _build_leave_confirmation_panel()
    _build_match_history_screen()''','build leave confirmation screen')
rep('''    _build_ui()
    local_clock_timer = Timer.new()''','''    _build_ui()
    if not account_token.is_empty():
        _send_matchmaking_request("city_profile", "/city/profile", HTTPClient.METHOD_GET)
    local_clock_timer = Timer.new()''','fetch saved account notifications on startup')
anchor='''func _build_match_history_screen() -> void:'''
insert='''func _build_leave_confirmation_panel() -> void:
    leave_confirmation_panel = Control.new()
    leave_confirmation_panel.name = "LeaveMatchConfirmation"
    leave_confirmation_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    leave_confirmation_panel.visible = false
    ui.add_child(leave_confirmation_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.006, 0.005, 0.94)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    leave_confirmation_panel.add_child(shade)
    var frame := _panel(leave_confirmation_panel, 0.24, 0.30, 0.76, 0.72)
    var title := _add_label(frame, "НЕЗАВЕРШЁННАЯ ПАРТИЯ", Vector2(18, 20), Vector2(620, 48), 25, PALE_GOLD)
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    var warning := _add_label(frame, "Выходить из незавершённой партии запрещено правилами CHECKMATE.\n\nЕсли покинуть матч, команда продолжит игру, а после окончания ты получишь результат и уведомление. За досрочный выход снимается дополнительный рейтинг.", Vector2(28, 90), Vector2(580, 170), 17, Color(0.91, 0.84, 0.72))
    warning.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var stay := _ornate_button(frame, "ОСТАТЬСЯ В ПАРТИИ", 0.06, 0.76, 0.48, 0.94, 15, "party")
    stay.pressed.connect(func(): leave_confirmation_panel.visible = false)
    var leave := _ornate_button(frame, "ПОКИНУТЬ МАТЧ", 0.52, 0.76, 0.94, 0.94, 15, "nav")
    leave.pressed.connect(_confirm_leave_online_match)

func _confirm_leave_online_match() -> void:
    if leave_confirmation_panel:
        leave_confirmation_panel.visible = false
    if online_match_id.is_empty() or online_session_token.is_empty():
        leave_match_confirmed = true
        _return_to_menu()
        return
    _send_matchmaking_request("match_leave", "/matches/" + online_match_id + "/leave", HTTPClient.METHOD_POST)

'''
if not s.__contains__(anchor):
    raise SystemExit("Missing: history screen insertion anchor")
s=s.replace(anchor,insert+anchor,1)
rep('''func _return_to_menu() -> void:
    selected_game_piece = null
    if online_active:
        _stop_online()''','''func _return_to_menu() -> void:
    if online_active and not game_over and not leave_match_confirmed and not online_match_id.is_empty():
        if leave_confirmation_panel:
            leave_confirmation_panel.visible = true
        return
    leave_match_confirmed = false
    selected_game_piece = null
    if online_active:
        _stop_online()''','intercept active match exit')
rep('''        "game_chat":
            if status_label: status_label.text = "Сообщение отправлено команде."
        "account_register", "account_login":''','''        "game_chat":
            if status_label: status_label.text = "Сообщение отправлено команде."
        "match_leave":
            leave_match_confirmed = true
            _show_notice(str(payload.get("warning", "Выход из незавершённой партии зафиксирован.")) + "\\nКоманда продолжит матч. Итог появится в уведомлениях после завершения.")
            _return_to_menu()
        "notifications_get":
            var notifications: Array = payload.get("notifications", [])
            var unread: Array = []
            var ids: Array = []
            for item in notifications:
                if item is Dictionary and not bool(item.get("read", false)):
                    unread.append(item)
                    ids.append(str(item.get("id", "")))
            if not unread.is_empty():
                var newest: Dictionary = unread[0]
                _show_notice(str(newest.get("title", "Уведомление")) + "\\n" + str(newest.get("message", "")))
                _send_matchmaking_request("notifications_read", "/notifications/read", HTTPClient.METHOD_POST, {"ids": ids})
        "notifications_read":
            pass
        "account_register", "account_login":''','notification actions')
rep('''        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))''','''        "city_profile", "city_unlock_piece", "city_purchase_piece", "city_purchase_skin":
            _apply_city_profile(payload.get("city", {}))
            if action == "city_profile" and not account_token.is_empty():
                _send_matchmaking_request("notifications_get", "/notifications", HTTPClient.METHOD_GET)''','fetch inbox after profile sync')
# Handle a server that has not yet been redeployed without trapping the user on the confirmation dialog.
rep('''        if action == "account_login" and response_code == 401:
            _set_account_error("Неверный логин и/или пароль.")''','''        if action == "match_leave":
            leave_match_confirmed = true
            _show_notice("Сервер не подтвердил выход из партии. Если связь пропала, матч отметит отсутствие по тайм-ауту.")
            _return_to_menu()
        elif action == "account_login" and response_code == 401:
            _set_account_error("Неверный логин и/или пароль.")''','leave request error fallback')
p.write_text(s, encoding="utf-8")
print("CHECKMATE v109: leave confirmation and result inbox client integration applied")
