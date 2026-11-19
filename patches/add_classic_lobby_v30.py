from pathlib import Path

path = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
source = path.read_text(encoding="utf-8").replace("\t", "    ")

def replace_func(name, replacement):
    global source
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        raise SystemExit("Function missing: " + name)
    end = source.find("\nfunc ", start + len(marker))
    if end < 0:
        end = len(source)
    source = source[:start] + replacement.rstrip() + "\n" + source[end:]

source = source.replace('const DEFAULT_MATCHMAKING_RATING := 1000\n',
    'const DEFAULT_MATCHMAKING_RATING := 1000\nconst MATCHMAKING_SERVER_URL := "https://YOUR-MATCHMAKING-SERVER"\nconst CLASSIC_TEAM_SIZE := 16\n', 1)
anchor = "var matchmaking_started_at := 0\n"
extra = """var queue_timer_label: Label
var queue_status_label: Label
var queue_rating_label: Label
var queue_white_roster_label: Label
var queue_black_roster_label: Label
var queue_cancel_button: Button
var queue_last_roster: Array = []
"""
if "var queue_timer_label:" not in source:
    if anchor not in source:
        raise SystemExit("Queue state anchor missing")
    source = source.replace(anchor, anchor + extra, 1)

source = source.replace('''    var online_button := _ornate_button(menu_panel, "🌐  ОНЛАЙН", 0.655, 0.145, 0.835, 0.255, 16, "nav")
    online_button.pressed.connect(_open_online_panel)
''', "", 1)

replace_func("_confirm_preparation", r'''func _confirm_preparation() -> void:
    if selected_mode != "Классика":
        prep_status.text = "Сейчас доступна только классика."
        return
    preparation_panel.visible = false
    menu_panel.visible = false
    _open_online_panel()
    _start_quick_match()''')

replace_func("_build_online_panel_screen", r'''func _build_online_panel_screen() -> void:
    online_panel = Control.new()
    online_panel.name = "MatchmakingWaitingRoom"
    online_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    online_panel.visible = false
    ui.add_child(online_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.97)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    online_panel.add_child(shade)
    var frame := _panel(online_panel, 0.025, 0.035, 0.975, 0.965)
    _add_label(frame, "ПОИСК СОПЕРНИКОВ", Vector2(20, 10), Vector2(620, 42), 28, PALE_GOLD)
    _add_label(frame, "КЛАССИКА  •  16 НА 16  •  ПОДБОР ПО РЕЙТИНГУ", Vector2(22, 52), Vector2(850, 28), 14, Color(0.82, 0.76, 0.66))
    queue_rating_label = _add_label(frame, "ВАШ РЕЙТИНГ: %d  •  %s" % [competitive_rating, _rating_division()], Vector2(22, 92), Vector2(420, 30), 17, PALE_GOLD)
    queue_timer_label = _add_label(frame, "ВРЕМЯ ПОИСКА  00:00", Vector2(500, 92), Vector2(300, 30), 19, PALE_GOLD)
    queue_timer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    var white_panel := _panel(frame, 0.025, 0.235, 0.485, 0.835)
    var black_panel := _panel(frame, 0.515, 0.235, 0.975, 0.835)
    _add_label(white_panel, "БЕЛАЯ КОМАНДА", Vector2(12, 8), Vector2(330, 30), 18, PALE_GOLD)
    _add_label(black_panel, "ЧЁРНАЯ КОМАНДА", Vector2(12, 8), Vector2(330, 30), 18, PALE_GOLD)
    queue_white_roster_label = _add_label(white_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 430), 15, Color(0.88, 0.85, 0.78))
    queue_black_roster_label = _add_label(black_panel, "Ожидаем игроков…", Vector2(14, 46), Vector2(350, 430), 15, Color(0.88, 0.85, 0.78))
    queue_status_label = _add_label(frame, "Подключаемся к рейтинговой очереди…", Vector2(24, 520), Vector2(650, 42), 15, PALE_GOLD)
    queue_cancel_button = _ornate_button(frame, "ОТМЕНИТЬ ПОИСК", 0.73, 0.855, 0.97, 0.975, 14, "nav")
    queue_cancel_button.pressed.connect(_close_online_panel)
    if online_http == null:
        online_http = HTTPRequest.new()
        online_http.timeout = 12.0
        add_child(online_http)
        online_http.request_completed.connect(_on_online_http_completed)
    if online_poll_timer == null:
        online_poll_timer = Timer.new()
        online_poll_timer.wait_time = 1.5
        online_poll_timer.one_shot = false
        add_child(online_poll_timer)
        online_poll_timer.timeout.connect(_poll_matchmaking_ticket)

func _update_queue_roster(players: Array) -> void:
    queue_last_roster = players
    var white := PackedStringArray()
    var black := PackedStringArray()
    for i in range(CLASSIC_TEAM_SIZE):
        white.append("%02d  — свободно" % (i + 1))
        black.append("%02d  — свободно" % (i + 1))
    for player in players:
        if not (player is Dictionary):
            continue
        var slot := int(player.get("slot", -1))
        var team := str(player.get("team", ""))
        var line := "%s   •   %d" % [str(player.get("name", "Игрок")), int(player.get("rating", 1000))]
        if team == "white" and slot >= 0 and slot < CLASSIC_TEAM_SIZE:
            white[slot] = "%02d  %s" % [slot + 1, line]
        elif team == "black" and slot >= 0 and slot < CLASSIC_TEAM_SIZE:
            black[slot] = "%02d  %s" % [slot + 1, line]
    if queue_white_roster_label:
        queue_white_roster_label.text = "\n".join(white)
    if queue_black_roster_label:
        queue_black_roster_label.text = "\n".join(black)

func _open_matchmaking_queue() -> void:
    if online_panel == null:
        _build_online_panel_screen()
    online_panel.visible = true
    if queue_rating_label:
        queue_rating_label.text = "ВАШ РЕЙТИНГ: %d  •  %s" % [competitive_rating, _rating_division()]
    if queue_status_label:
        queue_status_label.text = "Входим в рейтинговую очередь…"
    if queue_timer_label:
        queue_timer_label.text = "ВРЕМЯ ПОИСКА  00:00"
    _update_queue_roster([])''')

replace_func("_close_online_panel", r'''func _close_online_panel() -> void:
    if online_poll_timer:
        online_poll_timer.stop()
    if not online_ticket.is_empty() and online_http and online_http.get_http_client_status() == HTTPClient.STATUS_DISCONNECTED:
        _send_matchmaking_request("queue_cancel", "/matchmaking/queue/" + online_ticket + "/cancel", HTTPClient.METHOD_POST)
    online_ticket = ""
    _refund_pending_match_purchase()
    if online_active:
        _stop_online()
    if online_panel:
        online_panel.visible = false
    if menu_panel:
        menu_panel.visible = true''')

replace_func("_send_matchmaking_request", r'''func _send_matchmaking_request(action: String, path: String, method: int, payload: Dictionary = {}) -> void:
    if online_http == null:
        if queue_status_label:
            queue_status_label.text = "Ошибка: HTTP-клиент не создан."
        return
    if MATCHMAKING_SERVER_URL.contains("YOUR-MATCHMAKING-SERVER"):
        if queue_status_label:
            queue_status_label.text = "Сервер ещё не опубликован. Адрес будет прописан в коде перед выпуском."
        return
    if online_http.get_http_client_status() != HTTPClient.STATUS_DISCONNECTED:
        return
    online_http_action = action
    var headers := PackedStringArray(["Content-Type: application/json"])
    var result := online_http.request(MATCHMAKING_SERVER_URL.trim_suffix("/") + path, headers, method, JSON.stringify(payload))
    if result != OK and queue_status_label:
        queue_status_label.text = "Не удалось отправить запрос. Код: " + str(result)''')

replace_func("_on_online_http_completed", r'''func _on_online_http_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
    var payload: Variant = JSON.parse_string(body.get_string_from_utf8())
    if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300 or not (payload is Dictionary):
        if queue_status_label:
            queue_status_label.text = "Ошибка сервера подбора (" + str(response_code) + ")."
        online_http_action = ""
        return
    var action := online_http_action
    online_http_action = ""
    match action:
        "queue_start":
            online_ticket = str(payload.get("ticket", ""))
            _update_queue_roster(payload.get("players", []))
            if str(payload.get("status", "")) == "matched":
                online_poll_timer.stop()
                _handle_matchmaking_result(payload)
            elif not online_ticket.is_empty():
                if queue_status_label:
                    queue_status_label.text = "Ищем 32 игроков с близким рейтингом. Не закрывай экран."
                online_poll_timer.start()
        "queue_poll":
            _update_queue_roster(payload.get("players", []))
            if str(payload.get("status", "")) == "matched":
                online_poll_timer.stop()
                _handle_matchmaking_result(payload)
            elif str(payload.get("status", "")) == "cancelled":
                online_poll_timer.stop()
                if queue_status_label:
                    queue_status_label.text = "Поиск отменён."
        "queue_cancel":
            if queue_status_label:
                queue_status_label.text = "Поиск отменён."
        _:
            if queue_status_label:
                queue_status_label.text = "Ответ сервера получен."''')

replace_func("_poll_matchmaking_ticket", r'''func _poll_matchmaking_ticket() -> void:
    if online_ticket.is_empty():
        online_poll_timer.stop()
        return
    var waited_ms := maxi(0, Time.get_ticks_msec() - matchmaking_started_at)
    var total_seconds := int(waited_ms / 1000)
    if queue_timer_label:
        queue_timer_label.text = "ВРЕМЯ ПОИСКА  %02d:%02d" % [int(total_seconds / 60), total_seconds % 60]
    var allowed_gap := mini(500, 100 + int(waited_ms / 15000) * 50)
    if queue_status_label:
        queue_status_label.text = "Поиск игроков • диапазон ±%d • найдено %d из 32" % [allowed_gap, queue_last_roster.size()]
    _send_matchmaking_request("queue_poll", "/matchmaking/queue/" + online_ticket, HTTPClient.METHOD_GET)''')

replace_func("_handle_matchmaking_result", r'''func _handle_matchmaking_result(payload: Dictionary) -> void:
    _update_queue_roster(payload.get("players", []))
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _save_economy()
    var team := str(payload.get("team", ""))
    if queue_status_label:
        queue_status_label.text = "СОСТАВ СОБРАН • ВЫ ИГРАЕТЕ ЗА " + ("БЕЛЫХ" if team == "white" else "ЧЁРНЫХ")
    if queue_cancel_button:
        queue_cancel_button.text = "СОСТАВ СОБРАН"
        queue_cancel_button.disabled = true
    var host := str(payload.get("gameServerHost", ""))
    if host.is_empty():
        if queue_status_label:
            queue_status_label.text += "\n32 игрока подобраны. Игровой сервер ещё не настроен — автоматический старт матча пока недоступен."
        return
    _connect_to_online_host(host, int(payload.get("gameServerPort", 24567)))''')

replace_func("_start_quick_match", r'''func _start_quick_match() -> void:
    if not online_ticket.is_empty():
        return
    if queue_cancel_button:
        queue_cancel_button.disabled = false
        queue_cancel_button.text = "ОТМЕНИТЬ ПОИСК"
    online_player_id = _make_online_player_id()
    matchmaking_started_at = Time.get_ticks_msec()
    _update_queue_roster([])
    if queue_status_label:
        queue_status_label.text = "Входим в очередь классического режима…"
    if queue_timer_label:
        queue_timer_label.text = "ВРЕМЯ ПОИСКА  00:00"
    _send_matchmaking_request("queue_start", "/matchmaking/queue", HTTPClient.METHOD_POST, {
        "playerId": online_player_id,
        "playerName": "Игрок-" + online_player_id.substr(0, 5).to_upper(),
        "mode": "classic",
        "rating": competitive_rating
    })''')

# Remove the legacy Online entry point entirely; the preparation confirmation opens the queue screen.
source = source.replace("_open_online_panel()", "_open_matchmaking_queue()")
import re
while re.search(r"(?m)^func _open_online_panel\\(", source):
    match = re.search(r"(?m)^func _open_online_panel\\([^\\n]*\\n", source)
    if not match:
        break
    start = match.start()
    end = source.find("\\nfunc ", match.end())
    if end < 0:
        source = source[:start]
    else:
        source = source[:start] + source[end + 1:]

path.write_text(source, encoding="utf-8")
print("CHECKMATE v30 automatic lobby client patch ready.")
