from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "scripts" / "main.gd"
source = path.read_text(encoding="utf-8").replace("\t", "    ")

def replace_func(name: str, replacement: str) -> None:
    global source
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        raise SystemExit("Function not found: " + name)
    end = source.find("\nfunc ", start + len(marker))
    if end < 0:
        end = len(source)
    source = source[:start] + replacement.rstrip() + "\n" + source[end:]

# Matchmaking room state.
anchor = 'var online_ticket := ""\n'
extra = 'var matchmaking_info_label: Label\nvar matchmaking_started_at := 0\n'
if "var matchmaking_info_label:" not in source:
    if anchor not in source:
        raise SystemExit("Matchmaking state anchor missing")
    source = source.replace(anchor, anchor + extra, 1)

# Rename the online panel so it is clearly the matchmaking room.
source = source.replace('"СЕТЕВАЯ ПАРТИЯ"', '"КОМНАТА ПОДБОРА СОПЕРНИКОВ"', 1)
source = source.replace('"Комнаты и быстрый подбор соперника"', '"Классический режим • поиск соперника по рейтингу"', 1)
source = source.replace('"БЫСТРЫЙ ПОИСК"', '"НАЧАТЬ ПОИСК"', 1)
status_anchor = '    online_status_label = _add_label(frame, "Укажи адрес сервера подбора. Порт игровой сессии: " + str(online_port), Vector2(28, 410), Vector2(680, 46), 14, PALE_GOLD)\n'
if status_anchor not in source:
    raise SystemExit("Matchmaking room status anchor missing")
source = source.replace(status_anchor, status_anchor + '    matchmaking_info_label = _add_label(frame, "ТВОЙ РЕЙТИНГ: %d • НАЧАЛЬНЫЙ ДИАПАЗОН: ±100" % competitive_rating, Vector2(28, 452), Vector2(680, 28), 14, PALE_GOLD)\n', 1)

replace_func("_confirm_preparation", r'''func _confirm_preparation() -> void:
    if selected_mode != "Классика":
        prep_status.text = "Этот режим ещё разрабатывается. Сейчас доступна только классическая тестовая партия."
        _refund_pending_match_purchase()
        return
    preparation_panel.visible = false
    _open_online_panel()
    online_status_label.text = "Фигура подтверждена. Нажми «НАЧАТЬ ПОИСК», чтобы войти в рейтинговую очередь."
    if matchmaking_info_label:
        matchmaking_info_label.text = "ТВОЙ РЕЙТИНГ: %d • ПОДБОР: ±100 → ±500" % competitive_rating''')

replace_func("_start_quick_match", r'''func _start_quick_match() -> void:
    var base_url := online_server_url_input.text.strip_edges().trim_suffix("/")
    if not base_url.begins_with("https://") and not base_url.begins_with("http://"):
        online_status_label.text = "Сначала укажи адрес сервера подбора."
        return
    if base_url.contains("YOUR-SERVER-URL"):
        online_status_label.text = "Сервер подбора ещё не размещён. Адрес появится после публикации сервера."
        return
    _host_online_room()
    if not online_active:
        return
    online_player_id = _make_online_player_id()
    matchmaking_started_at = Time.get_ticks_msec()
    if matchmaking_info_label:
        matchmaking_info_label.text = "ТВОЙ РЕЙТИНГ: %d • ИЩЕМ СОПЕРНИКА В ДИАПАЗОНЕ ±100" % competitive_rating
    _send_matchmaking_request("queue_start", "/matchmaking/queue", HTTPClient.METHOD_POST, {
        "playerId": online_player_id,
        "port": online_port,
        "mode": "classic",
        "rating": competitive_rating
    })''')

replace_func("_poll_matchmaking_ticket", r'''func _poll_matchmaking_ticket() -> void:
    if online_ticket.is_empty():
        online_poll_timer.stop()
        return
    var waited_ms := maxi(0, Time.get_ticks_msec() - matchmaking_started_at)
    var allowed_gap := mini(500, 100 + int(waited_ms / 15000) * 50)
    if matchmaking_info_label:
        matchmaking_info_label.text = "ТВОЙ РЕЙТИНГ: %d • ПОИСК: ±%d • ОЖИДАНИЕ: %d СЕК." % [competitive_rating, allowed_gap, int(waited_ms / 1000)]
    _send_matchmaking_request("queue_poll", "/matchmaking/queue/" + online_ticket, HTTPClient.METHOD_GET)''')

replace_func("_handle_matchmaking_result", r'''func _handle_matchmaking_result(payload: Dictionary) -> void:
    # Charge the selected figure only after a real opponent has been found.
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _save_economy()
    var role := str(payload.get("role", ""))
    var code := str(payload.get("code", ""))
    var opponent_rating := int(payload.get("opponentRating", 0))
    var rating_difference := int(payload.get("ratingDifference", 0))
    if not code.is_empty():
        online_room_code_input.text = code
    if matchmaking_info_label:
        matchmaking_info_label.text = "СОПЕРНИК НАЙДЕН • РЕЙТИНГ: %d • РАЗНИЦА: %d" % [opponent_rating, rating_difference]
    if role == "host":
        online_status_label.text = "Соперник найден! Комната " + code + ". Подключаем игрока…"
    elif role == "guest":
        online_status_label.text = "Соперник найден! Подключаемся к комнате…"
        _connect_to_online_host(str(payload.get("host", "")), int(payload.get("port", online_port)))
    else:
        online_status_label.text = "Неизвестный ответ подбора."''')

replace_func("_close_online_panel", r'''func _close_online_panel() -> void:
    if online_poll_timer:
        online_poll_timer.stop()
    if not online_ticket.is_empty():
        var base_url := online_server_url_input.text.strip_edges().trim_suffix("/")
        if online_http and online_http.get_http_client_status() == HTTPClient.STATUS_DISCONNECTED and (base_url.begins_with("https://") or base_url.begins_with("http://")):
            _send_matchmaking_request("queue_cancel", "/matchmaking/queue/" + online_ticket + "/cancel", HTTPClient.METHOD_POST)
    online_ticket = ""
    if online_active:
        _stop_online()
    _refund_pending_match_purchase()
    online_panel.visible = false
    menu_panel.visible = true''')

# Handle server cancellation responses without leaving a ghost queue state.
source = source.replace('''        "queue_poll":
            if str(payload.get("status", "")) == "matched":
                online_poll_timer.stop()
                _handle_matchmaking_result(payload)''',
'''        "queue_poll":
            if str(payload.get("status", "")) == "matched":
                online_poll_timer.stop()
                _handle_matchmaking_result(payload)
            elif str(payload.get("status", "")) == "cancelled":
                online_poll_timer.stop()
                online_status_label.text = "Поиск отменён."
        "queue_cancel":
            online_status_label.text = "Поиск отменён."''', 1)

path.write_text(source, encoding="utf-8")
print("CHECKMATE v29: confirmation opens rating-based matchmaking room; search shows rating range and waits for a matched opponent.")
