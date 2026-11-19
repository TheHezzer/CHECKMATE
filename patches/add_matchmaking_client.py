from pathlib import Path

root = Path(__file__).resolve().parent.parent
main_path = root / "scripts" / "main.gd"
source = main_path.read_text(encoding="utf-8").replace("\t", "    ")

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

anchor = "var online_port := 24567\n"
extra = '''var online_server_url_input: LineEdit
var online_room_code_input: LineEdit
var online_http: HTTPRequest
var online_poll_timer: Timer
var online_http_action := ""
var online_ticket := ""
var online_player_id := ""
'''
if "var online_server_url_input:" not in source:
    if anchor not in source:
        raise SystemExit("Online state anchor missing")
    source = source.replace(anchor, anchor + extra, 1)

replace_func("_build_online_panel_screen", r'''func _build_online_panel_screen() -> void:
    online_panel = Control.new()
    online_panel.name = "OnlineRoomScreen"
    online_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    online_panel.visible = false
    ui.add_child(online_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.012, 0.010, 0.009, 0.96)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    online_panel.add_child(shade)
    var frame := _panel(online_panel, 0.10, 0.10, 0.90, 0.90)
    _add_label(frame, "СЕТЕВАЯ ПАРТИЯ", Vector2(26, 18), Vector2(620, 42), 28, PALE_GOLD)
    _add_label(frame, "Комнаты и быстрый подбор соперника", Vector2(28, 62), Vector2(660, 28), 15, Color(0.82, 0.76, 0.66))
    _add_label(frame, "АДРЕС СЕРВЕРА ПОДБОРА", Vector2(28, 105), Vector2(400, 22), 13, PALE_GOLD)
    online_server_url_input = LineEdit.new()
    online_server_url_input.placeholder_text = "https://адрес-сервера"
    online_server_url_input.text = "https://YOUR-SERVER-URL"
    online_server_url_input.position = Vector2(28, 130)
    online_server_url_input.size = Vector2(650, 42)
    online_server_url_input.add_theme_font_size_override("font_size", 16)
    frame.add_child(online_server_url_input)
    var host_button := _ornate_button(frame, "СОЗДАТЬ КОМНАТУ", 0.05, 0.28, 0.47, 0.40, 16, "party")
    host_button.pressed.connect(_create_private_room)
    var quick_button := _ornate_button(frame, "БЫСТРЫЙ ПОИСК", 0.53, 0.28, 0.95, 0.40, 16, "party")
    quick_button.pressed.connect(_start_quick_match)
    _add_label(frame, "КОД КОМНАТЫ", Vector2(28, 230), Vector2(260, 22), 13, PALE_GOLD)
    online_room_code_input = LineEdit.new()
    online_room_code_input.placeholder_text = "Например: A7K9PQ"
    online_room_code_input.position = Vector2(28, 255)
    online_room_code_input.size = Vector2(300, 44)
    online_room_code_input.add_theme_font_size_override("font_size", 20)
    online_room_code_input.max_length = 6
    frame.add_child(online_room_code_input)
    var join_button := _ornate_button(frame, "ВОЙТИ ПО КОДУ", 0.53, 0.47, 0.95, 0.60, 16, "party")
    join_button.pressed.connect(_join_private_room)
    _add_label(frame, "ИЛИ ПОДКЛЮЧИТЬСЯ ПО IP (ОДНА СЕТЬ / РУЧНОЙ РЕЖИМ)", Vector2(28, 325), Vector2(600, 22), 12, PALE_GOLD)
    online_ip_input = LineEdit.new()
    online_ip_input.placeholder_text = "Локальный или публичный IP хоста"
    online_ip_input.position = Vector2(28, 350)
    online_ip_input.size = Vector2(400, 42)
    online_ip_input.add_theme_font_size_override("font_size", 16)
    frame.add_child(online_ip_input)
    var ip_button := _ornate_button(frame, "ПО IP", 0.62, 0.68, 0.95, 0.80, 15, "nav")
    ip_button.pressed.connect(_join_online_room)
    online_status_label = _add_label(frame, "Укажи адрес сервера подбора. Порт игровой сессии: " + str(online_port), Vector2(28, 410), Vector2(680, 46), 14, PALE_GOLD)
    var note := _add_label(frame, "Сервер подбора должен быть заранее размещён в интернете. Для прямой игры хосту нужен доступный UDP-порт 24567; если телефон за мобильным NAT, прямое подключение может не пройти.", Vector2(28, 462), Vector2(680, 72), 12, Color(0.78, 0.72, 0.63))
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var back := _ornate_button(frame, "← НАЗАД", 0.72, 0.87, 0.95, 0.97, 13, "nav")
    back.pressed.connect(_close_online_panel)
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
        online_poll_timer.timeout.connect(_poll_matchmaking_ticket)''')

replace_func("_create_private_room", r'''func _create_private_room() -> void:
    _host_online_room()
    if not online_active:
        return
    online_player_id = _make_online_player_id()
    _send_matchmaking_request("create_room", "/rooms", HTTPClient.METHOD_POST, {
        "playerId": online_player_id,
        "port": online_port,
        "mode": "classic",
        "rating": 0
    })''')

replace_func("_host_online_room", r'''func _host_online_room() -> void:
    _stop_online(false)
    online_peer = ENetMultiplayerPeer.new()
    var result := online_peer.create_server(online_port, 1)
    if result != OK:
        online_status_label.text = "Не удалось открыть игровой порт. Код: " + str(result)
        return
    multiplayer.multiplayer_peer = online_peer
    online_active = true
    online_role = "host"
    online_game_started = false
    if not multiplayer.peer_connected.is_connected(_on_online_peer_connected):
        multiplayer.peer_connected.connect(_on_online_peer_connected)
    if not multiplayer.peer_disconnected.is_connected(_on_online_peer_disconnected):
        multiplayer.peer_disconnected.connect(_on_online_peer_disconnected)
    online_status_label.text = "Игровой порт открыт. Обращаемся к серверу комнат…"''')

replace_func("_join_private_room", r'''func _join_private_room() -> void:
    var code := online_room_code_input.text.strip_edges().to_upper()
    if code.length() != 6:
        online_status_label.text = "Введи шестизначный код комнаты."
        return
    online_player_id = _make_online_player_id()
    _send_matchmaking_request("join_room", "/rooms/" + code + "/join", HTTPClient.METHOD_POST, {
        "playerId": online_player_id
    })''')

replace_func("_start_quick_match", r'''func _start_quick_match() -> void:
    _host_online_room()
    if not online_active:
        return
    online_player_id = _make_online_player_id()
    _send_matchmaking_request("queue_start", "/matchmaking/queue", HTTPClient.METHOD_POST, {
        "playerId": online_player_id,
        "port": online_port,
        "mode": "classic",
        "rating": 0
    })''')

# Replace the existing direct-IP join function, retaining it as a manual fallback.
replace_func("_join_online_room", r'''func _join_online_room() -> void:
    var address := online_ip_input.text.strip_edges()
    if address.is_empty():
        online_status_label.text = "Введи IP-адрес хоста."
        return
    _connect_to_online_host(address, online_port)

func _connect_to_online_host(address: String, port: int) -> void:
    _stop_online(false)
    online_peer = ENetMultiplayerPeer.new()
    var result := online_peer.create_client(address, port)
    if result != OK:
        online_status_label.text = "Не удалось подключиться. Код: " + str(result)
        return
    multiplayer.multiplayer_peer = online_peer
    online_active = true
    online_role = "client"
    online_game_started = false
    if not multiplayer.connected_to_server.is_connected(_on_online_connected):
        multiplayer.connected_to_server.connect(_on_online_connected)
    if not multiplayer.connection_failed.is_connected(_on_online_connection_failed):
        multiplayer.connection_failed.connect(_on_online_connection_failed)
    if not multiplayer.server_disconnected.is_connected(_on_online_server_disconnected):
        multiplayer.server_disconnected.connect(_on_online_server_disconnected)
    online_status_label.text = "Подключаемся к " + address + ":" + str(port) + "…"

func _make_online_player_id() -> String:
    return str(Time.get_unix_time_from_system()) + "-" + str(randi()) + "-" + str(OS.get_process_id())

func _send_matchmaking_request(action: String, path: String, method: int, payload: Dictionary = {}) -> void:
    if online_http == null:
        online_status_label.text = "HTTP-клиент не создан. Открой экран онлайн ещё раз."
        return
    var base_url := online_server_url_input.text.strip_edges().trim_suffix("/")
    if not base_url.begins_with("https://") and not base_url.begins_with("http://"):
        online_status_label.text = "Укажи полный адрес сервера, начиная с https://"
        return
    if base_url.contains("YOUR-SERVER-URL"):
        online_status_label.text = "Сначала нужно разместить сервер и указать его адрес."
        return
    if online_http.get_http_client_status() != HTTPClient.STATUS_DISCONNECTED:
        online_status_label.text = "Предыдущий запрос ещё выполняется."
        return
    online_http_action = action
    var headers := PackedStringArray(["Content-Type: application/json"])
    var result := online_http.request(base_url + path, headers, method, JSON.stringify(payload))
    if result != OK:
        online_status_label.text = "Не удалось отправить запрос. Код: " + str(result)

func _on_online_http_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
    var payload: Variant = JSON.parse_string(body.get_string_from_utf8())
    if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300 or not (payload is Dictionary):
        var error_text := "Ошибка сервера комнат (" + str(response_code) + ")."
        if payload is Dictionary and payload.has("error"):
            error_text += " " + str(payload["error"])
        online_status_label.text = error_text
        online_http_action = ""
        return
    var action := online_http_action
    online_http_action = ""
    match action:
        "create_room":
            var code := str(payload.get("code", ""))
            online_room_code_input.text = code
            online_status_label.text = "КОМНАТА " + code + " СОЗДАНА. Передай код сопернику."
        "join_room":
            online_status_label.text = "Код принят. Подключаемся к хосту…"
            _connect_to_online_host(str(payload.get("host", "")), int(payload.get("port", online_port)))
        "queue_start":
            online_ticket = str(payload.get("ticket", ""))
            if str(payload.get("status", "")) == "matched":
                _handle_matchmaking_result(payload)
            else:
                online_status_label.text = "Ищем соперника… Не закрывай экран."
                online_poll_timer.start()
        "queue_poll":
            if str(payload.get("status", "")) == "matched":
                online_poll_timer.stop()
                _handle_matchmaking_result(payload)
        _:
            online_status_label.text = "Ответ сервера получен."

func _poll_matchmaking_ticket() -> void:
    if online_ticket.is_empty():
        online_poll_timer.stop()
        return
    _send_matchmaking_request("queue_poll", "/matchmaking/queue/" + online_ticket, HTTPClient.METHOD_GET)

func _handle_matchmaking_result(payload: Dictionary) -> void:
    var role := str(payload.get("role", ""))
    var code := str(payload.get("code", ""))
    if not code.is_empty():
        online_room_code_input.text = code
    if role == "host":
        online_status_label.text = "Соперник найден! Комната " + code + ". Ожидаем подключение…"
    elif role == "guest":
        online_status_label.text = "Соперник найден! Подключаемся…"
        _connect_to_online_host(str(payload.get("host", "")), int(payload.get("port", online_port)))
    else:
        online_status_label.text = "Неизвестный ответ подбора."

''')

# Stop polling on disconnect and when leaving the lobby.
source = source.replace('func _stop_online(return_peer: bool = true) -> void:\n    online_active = false\n',
'''func _stop_online(return_peer: bool = true) -> void:
    if online_poll_timer:
        online_poll_timer.stop()
    online_ticket = ""
    online_active = false
''', 1)

main_path.write_text(source, encoding="utf-8")
print("Integrated private room codes and quick matchmaking HTTP client into Godot online lobby.")
