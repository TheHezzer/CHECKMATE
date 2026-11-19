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

state_anchor = "var game_over_detail: Label\n"
network_state = '''var online_active := false
var online_game_started := false
var online_role := "offline"
var online_peer: ENetMultiplayerPeer
var online_panel: Control
var online_status_label: Label
var online_ip_input: LineEdit
var online_port := 24567
'''
if "var online_active :=" not in source:
    if state_anchor not in source:
        raise SystemExit("Network state anchor missing")
    source = source.replace(state_anchor, state_anchor + network_state, 1)

# Add a clear online entry point beside the main party button.
party_line = '    party.pressed.connect(_open_mode_selection)\n'
online_button = '''    party.pressed.connect(_open_mode_selection)
    var online_button := _ornate_button(menu_panel, "🌐  ОНЛАЙН", 0.655, 0.145, 0.835, 0.255, 16, "nav")
    online_button.pressed.connect(_open_online_panel)
'''
if 'online_button.pressed.connect(_open_online_panel)' not in source:
    if party_line not in source:
        raise SystemExit("Main menu party button anchor missing")
    source = source.replace(party_line, online_button, 1)

# Prevent UI from changing the turn locally in network games.
source = source.replace('    end_turn.pressed.connect(_advance_team_turn)\n',
                        '    end_turn.pressed.connect(_manual_end_turn)\n', 1)

# Build online lobby after the game screen.
ui_anchor = '    _build_preparation_screen()\n'
if "    _build_online_panel_screen()\n" not in source:
    if ui_anchor not in source:
        raise SystemExit("UI screen anchor missing")
    source = source.replace(ui_anchor, ui_anchor + '    _build_online_panel_screen()\n', 1)

# Replace click handler and extract one authoritative move pipeline.
replace_func("_handle_game_board_click", r'''func _handle_game_board_click(screen_position: Vector2) -> void:
    if game_over:
        return
    if selected_mode != "Классика":
        status_label.text = "Сетевое подключение пока доступно только для классики."
        return
    if team_turn_label and team_turn_label.get_global_rect().has_point(screen_position):
        return
    var ray_origin: Vector3 = camera.project_ray_origin(screen_position)
    var ray_direction: Vector3 = camera.project_ray_normal(screen_position)
    var hit = Plane(Vector3.UP, 0.59).intersects_ray(ray_origin, ray_direction)
    if hit == null:
        return
    var col: int = roundi(hit.x / 1.05 + 3.5)
    var row: int = roundi((hit.z + 0.4) / 0.88 + 3.5)
    if col < 0 or col > 7 or row < 0 or row > 7:
        return
    var local_team := _local_team()
    if current_team != local_team:
        status_label.text = "Сейчас ход соперника."
        return
    var target_piece: Node3D = _get_game_piece_at(col, row)
    if selected_game_piece == null:
        if target_piece != null and str(target_piece.get_meta("team")) == local_team:
            selected_game_piece = target_piece
            status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + ". Выбери клетку."
        else:
            status_label.text = "Выбери свою фигуру."
        return
    if target_piece == selected_game_piece:
        selected_game_piece = null
        status_label.text = "Выбор отменён."
        return
    if target_piece != null and str(target_piece.get_meta("team")) == local_team:
        selected_game_piece = target_piece
        status_label.text = "Выбрана фигура: " + str(target_piece.get_meta("kind")) + "."
        return
    var from_col := int(selected_game_piece.get_meta("col"))
    var from_row := int(selected_game_piece.get_meta("row"))
    if online_active and not multiplayer.is_server():
        rpc_id(1, "_rpc_request_move", from_col, from_row, col, row)
        status_label.text = "Ход отправлен серверу. Ожидаем подтверждения…"
        selected_game_piece = null
        return
    _process_classic_move(from_col, from_row, col, row)

func _process_classic_move(from_col: int, from_row: int, to_col: int, to_row: int) -> void:
    if game_over or current_team != _local_team() and not multiplayer.is_server():
        return
    var piece := _get_game_piece_at(from_col, from_row)
    if piece == null or str(piece.get_meta("team")) != current_team:
        return
    var target_piece := _get_game_piece_at(to_col, to_row)
    selected_game_piece = piece
    var kind := str(piece.get_meta("kind"))
    if not _is_valid_classic_move(kind, current_team, from_col, from_row, to_col, to_row, target_piece):
        status_label.text = "Недопустимый ход."
        return
    if not _move_keeps_king_safe(piece, to_col, to_row, target_piece):
        status_label.text = "Нельзя оставлять своего короля под шахом."
        return
    _apply_classic_move(from_col, from_row, to_col, to_row, true)

func _apply_classic_move(from_col: int, from_row: int, col: int, row: int, broadcast: bool) -> void:
    var piece := _get_game_piece_at(from_col, from_row)
    if piece == null:
        return
    var target_piece := _get_game_piece_at(col, row)
    var moving_team := current_team
    var kind := str(piece.get_meta("kind"))
    var is_castle: bool = kind == "K" and abs(col - from_col) == 2
    var is_en_passant: bool = kind == "P" and abs(col - from_col) == 1 and target_piece == null
    var ep_victim: Node3D = _en_passant_victim(piece, col, row) if is_en_passant else null
    var captured := target_piece != null or ep_victim != null
    if target_piece != null:
        game_piece_nodes.erase(target_piece)
        target_piece.queue_free()
    if ep_victim != null:
        game_piece_nodes.erase(ep_victim)
        ep_victim.queue_free()
    piece.position = Vector3((col - 3.5) * 1.05, 0.64, (row - 3.5) * 0.88 - 0.4)
    piece.set_meta("col", col)
    piece.set_meta("row", row)
    piece.set_meta("has_moved", true)
    if is_castle:
        var rook_from_col := 7 if col > from_col else 0
        var rook_to_col := col - 1 if col > from_col else col + 1
        var rook := _get_game_piece_at(rook_from_col, from_row)
        if rook != null:
            rook.position = Vector3((rook_to_col - 3.5) * 1.05, 0.64, (from_row - 3.5) * 0.88 - 0.4)
            rook.set_meta("col", rook_to_col)
            rook.set_meta("has_moved", true)
    var promoted := kind == "P" and ((moving_team == "white" and row == 0) or (moving_team == "black" and row == 7))
    if promoted:
        piece.set_meta("kind", "Q")
        _rebuild_promoted_piece(piece)
    last_move = {
        "team": moving_team,
        "kind": kind,
        "from_col": from_col,
        "from_row": from_row,
        "to_col": col,
        "to_row": row,
        "double_pawn": kind == "P" and abs(row - from_row) == 2
    }
    if kind == "P" or captured:
        halfmove_clock = 0
    else:
        halfmove_clock += 1
    selected_game_piece = null
    _advance_team_turn()
    _remember_position()
    _evaluate_classic_position(moving_team, promoted, is_castle, is_en_passant)
    if broadcast and online_active and multiplayer.is_server():
        for peer_id in multiplayer.get_peers():
            rpc_id(peer_id, "_rpc_sync_move", from_col, from_row, col, row)

@rpc("any_peer", "call_remote", "reliable")
func _rpc_request_move(from_col: int, from_row: int, to_col: int, to_row: int) -> void:
    if not online_active or not multiplayer.is_server() or game_over:
        return
    var sender_id := multiplayer.get_remote_sender_id()
    if sender_id != 2 or current_team != "black":
        return
    var piece := _get_game_piece_at(from_col, from_row)
    if piece == null or str(piece.get_meta("team")) != "black":
        return
    _process_classic_move(from_col, from_row, to_col, to_row)

@rpc("authority", "call_remote", "reliable")
func _rpc_sync_move(from_col: int, from_row: int, to_col: int, to_row: int) -> void:
    if not online_active or multiplayer.is_server() or game_over:
        return
    _apply_classic_move(from_col, from_row, to_col, to_row, false)

func _local_team() -> String:
    if not online_active:
        return current_team
    return "white" if multiplayer.is_server() else "black"

func _manual_end_turn() -> void:
    if online_active:
        status_label.text = "В онлайн-партии ход меняется только после допустимого хода."
        return
    _advance_team_turn()''')

# Guard team pass in online mode.
replace_func("_pass_to_teammate", r'''func _pass_to_teammate() -> void:
    if game_over:
        return
    if online_active:
        status_label.text = "В сетевой классике каждый игрок управляет своей стороной."
        return
    if selected_mode != "Классика":
        status_label.text = "Передача хода будет доступна после подключения правил этого режима."
        return
    active_teammate = (active_teammate % 4) + 1
    selected_game_piece = null
    _refresh_team_turn_label()
    status_label.text = "Очередь передана союзнику. Ход всё ещё за вашей командой."''')

# Online room lifecycle and UI.
insert_at = source.find("func _pass_to_teammate(")
if insert_at < 0:
    raise SystemExit("Cannot find online helper insertion point")
helpers = r'''func _build_online_panel_screen() -> void:
    online_panel = Control.new()
    online_panel.name = "OnlineRoomScreen"
    online_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    online_panel.visible = false
    ui.add_child(online_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.012, 0.010, 0.009, 0.96)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    online_panel.add_child(shade)
    var frame := _panel(online_panel, 0.14, 0.15, 0.86, 0.86)
    _add_label(frame, "СЕТЕВАЯ ПАРТИЯ", Vector2(26, 22), Vector2(600, 42), 28, PALE_GOLD)
    _add_label(frame, "Создай комнату или подключись к уже запущенной игре", Vector2(28, 70), Vector2(660, 30), 15, Color(0.82, 0.76, 0.66))
    var host_button := _ornate_button(frame, "СОЗДАТЬ КОМНАТУ", 0.06, 0.23, 0.48, 0.39, 17, "party")
    host_button.pressed.connect(_host_online_room)
    _add_label(frame, "АДРЕС ХОСТА", Vector2(28, 225), Vector2(250, 24), 14, PALE_GOLD)
    online_ip_input = LineEdit.new()
    online_ip_input.placeholder_text = "Например: 192.168.1.25"
    online_ip_input.text = "127.0.0.1"
    online_ip_input.position = Vector2(28, 255)
    online_ip_input.size = Vector2(400, 48)
    online_ip_input.add_theme_font_size_override("font_size", 18)
    frame.add_child(online_ip_input)
    var join_button := _ornate_button(frame, "ПОДКЛЮЧИТЬСЯ", 0.54, 0.47, 0.94, 0.62, 17, "party")
    join_button.pressed.connect(_join_online_room)
    online_status_label = _add_label(frame, "Ожидание подключения. Порт: 24567", Vector2(28, 330), Vector2(660, 48), 15, PALE_GOLD)
    var note := _add_label(frame, "Для одной Wi-Fi сети укажи локальный IP хоста. Для игры через интернет хосту нужен публичный IP и открытый UDP-порт 24567. Автоматического поиска соперника пока нет.", Vector2(28, 390), Vector2(690, 105), 13, Color(0.78, 0.72, 0.63))
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var back := _ornate_button(frame, "← НАЗАД", 0.70, 0.84, 0.94, 0.96, 14, "nav")
    back.pressed.connect(_close_online_panel)

func _open_online_panel() -> void:
    if online_panel == null:
        _build_online_panel_screen()
    menu_panel.visible = false
    online_panel.visible = true
    if online_status_label:
        online_status_label.text = "Ожидание подключения. Порт: " + str(online_port)

func _close_online_panel() -> void:
    if online_active:
        _stop_online()
    online_panel.visible = false
    menu_panel.visible = true

func _host_online_room() -> void:
    _stop_online(false)
    online_peer = ENetMultiplayerPeer.new()
    var result := online_peer.create_server(online_port, 1)
    if result != OK:
        online_status_label.text = "Не удалось открыть порт. Код: " + str(result)
        return
    multiplayer.multiplayer_peer = online_peer
    online_active = true
    online_role = "host"
    online_game_started = false
    if not multiplayer.peer_connected.is_connected(_on_online_peer_connected):
        multiplayer.peer_connected.connect(_on_online_peer_connected)
    if not multiplayer.peer_disconnected.is_connected(_on_online_peer_disconnected):
        multiplayer.peer_disconnected.connect(_on_online_peer_disconnected)
    online_status_label.text = "КОМНАТА СОЗДАНА. Передай свой IP сопернику. Ожидаем игрока…"

func _join_online_room() -> void:
    _stop_online(false)
    var address := online_ip_input.text.strip_edges()
    if address.is_empty():
        online_status_label.text = "Введи IP-адрес хоста."
        return
    online_peer = ENetMultiplayerPeer.new()
    var result := online_peer.create_client(address, online_port)
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
    online_status_label.text = "Подключаемся к " + address + ":" + str(online_port) + "…"

func _on_online_peer_connected(peer_id: int) -> void:
    if peer_id != 2:
        return
    online_status_label.text = "Соперник подключён. Запускаем партию…"
    if not online_game_started:
        online_game_started = true
        selected_mode = "Классика"
        _start_game("Классика")
        status_label.text = "Онлайн-партия началась. Вы играете белыми."

func _on_online_connected() -> void:
    online_status_label.text = "Подключено. Запускаем партию…"
    online_game_started = true
    selected_mode = "Классика"
    _start_game("Классика")
    status_label.text = "Онлайн-партия началась. Вы играете чёрными."

func _on_online_connection_failed() -> void:
    online_status_label.text = "Подключение не удалось. Проверь IP, порт и сеть."
    _stop_online(false)

func _on_online_server_disconnected() -> void:
    online_status_label.text = "Соединение с хостом потеряно."
    _stop_online(false)
    if game_panel:
        status_label.text = "Связь с соперником потеряна."

func _on_online_peer_disconnected(peer_id: int) -> void:
    if peer_id == 2:
        online_status_label.text = "Соперник отключился."
        if game_panel and game_panel.visible:
            status_label.text = "Соперник отключился. Вернись в меню онлайн-комнаты."

func _stop_online(return_peer: bool = true) -> void:
    online_active = false
    online_game_started = false
    online_role = "offline"
    if return_peer:
        multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()
    elif online_peer != null:
        online_peer.close()
        multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()
    online_peer = null

'''
source = source[:insert_at] + helpers + source[insert_at:]

# The host and client need a clean online state when starting or leaving a match.
start_anchor = 'func _start_game(mode_name: String) -> void:\n'
if start_anchor not in source:
    raise SystemExit("Start game function missing")
# Keep network flags intact during network-started matches; reset only the chess state.
source = source.replace('    _refresh_team_turn_label()\n    menu_panel.visible = false\n',
                        '    _refresh_team_turn_label()\n    menu_panel.visible = false\n    if online_panel:\n        online_panel.visible = false\n', 1)

# Stop network when returning to menu from a match, but not when the lobby is merely closed.
return_anchor = 'func _return_to_menu() -> void:\n    selected_game_piece = null\n'
source = source.replace(return_anchor, return_anchor + '    if online_active:\n        _stop_online()\n', 1)

# Show online ownership in the turn label.
old_turn = '        team_turn_label.text = "ХОД: " + team_name + " • ИГРОК " + str(active_teammate) + "/4"'
new_turn = '''        team_turn_label.text = "ХОД: " + team_name + " • ИГРОК " + str(active_teammate) + "/4"
        if online_active:
            team_turn_label.text += "  |  " + ("ВЫ БЕЛЫЕ" if _local_team() == "white" else "ВЫ ЧЁРНЫЕ")'''
if old_turn in source:
    source = source.replace(old_turn, new_turn, 1)

main_path.write_text(source, encoding="utf-8")
print("Online v21 patch applied: host/join lobby, ENet connection, server-authoritative moves, client sync.")
