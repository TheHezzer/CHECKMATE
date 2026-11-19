from pathlib import Path

root = Path(__file__).resolve().parent.parent
script_path = root / "scripts" / "main.gd"
s = script_path.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Patch anchor not found: " + label)
    s = s.replace(old, new, 1)

replace_once(
'''var status_label: Label
''',
'''var status_label: Label
var preparation_panel: Control
var prep_status: Label
var prep_piece_buttons: Array[Button] = []
var selected_prep_piece := 0
var balances := {"zloty": 12750, "xp": 850, "chessmatites": 620}
var unlocked_pieces := ["Пешка"]
var owned_skins := ["Дерево"]
var match_piece_costs := {"Пешка": 0, "Конь": 180, "Слон": 220, "Ладья": 260, "Ферзь": 520, "Король": 0}
var piece_unlock_xp := {"Пешка": 0, "Конь": 300, "Слон": 400, "Ладья": 500, "Ферзь": 1200, "Король": 0}
''', "economy variables")

replace_once(
'''func _ready() -> void:
\t_build_world()
\t_build_ui()
''',
'''func _ready() -> void:
\t_load_economy()
\t_build_world()
\t_build_ui()
''', "load economy")

replace_once(
'''xp.max_value = 2000
\txp.value = 850''',
'''xp.max_value = 1000
\txp.value = int(balances["xp"])''', "profile xp")

replace_once(
'''var gambits := _ornate_button(menu_panel, "✥  ГАМБИТЫ
12 750", 0.285, 0.035, 0.425, 0.125, 14, "nav")
\tgambits.pressed.connect(_show_notice.bind("Гамбиты — игровая валюта за матчи и задания"))
\tvar chessmatites := _ornate_button(menu_panel, "◆  ШАХМАТИТЫ
620   +", 0.432, 0.035, 0.572, 0.125, 14, "nav")
''',
'''var gambits := _ornate_button(menu_panel, "◈  ЗЛОТЫЕ
%d" % int(balances["zloty"]), 0.285, 0.035, 0.425, 0.125, 14, "nav")
\tgambits.name = "ZlotyCounter"
\tgambits.pressed.connect(_show_notice.bind("Злотые — игровая валюта. Фигуры покупаются перед каждой партией."))
\tvar chessmatites := _ornate_button(menu_panel, "◆  ШАХМАТИТЫ
%d   +" % int(balances["chessmatites"]), 0.432, 0.035, 0.572, 0.125, 14, "nav")
\tchessmatites.name = "ChessmatitesCounter"
''', "zloty and chessmatite counters")

replace_once(
'''var experience := _ornate_button(menu_panel, "★  ОПЫТ
850 / 2000", 0.579, 0.035, 0.715, 0.125, 14, "nav")
\texperience.pressed.connect(_show_notice.bind("Опыт повышает уровень игрока"))''',
'''var experience := _ornate_button(menu_panel, "★  XP
%d" % int(balances["xp"]), 0.579, 0.035, 0.715, 0.125, 14, "nav")
\texperience.name = "XPCounter"
\texperience.pressed.connect(_show_notice.bind("XP — расходуемый ресурс для открытия фигур и покупки постоянных скинов."))''', "xp counter")

replace_once(
'''party.pressed.connect(func(): _start_game(selected_mode))''',
'''party.pressed.connect(_open_preparation)''', "party opens preparation")

replace_once(
'''var modes := ["Классика", "Командный", "Своя армия", "Клановая война"]
\tvar subtitles := ["1 на 1", "2 на 2", "Битва с ботами", "Сражение кланов"]
\tvar symbols := ["♞", "♟", "♛", "⚔"]
\tfor i in range(modes.size()):
\t\tvar x := 0.185 + float(i) * 0.158
\t\tvar b := _ornate_button(menu_panel, symbols[i] + "
" + modes[i] + "
" + subtitles[i], x, 0.735, x + 0.150, 0.885, 17, "card")
\t\tb.pressed.connect(_on_mode_pressed.bind(modes[i]))''',
'''var modes := ["Классика", "Командное голосование", "Несколько фигур"]
\tvar subtitles := ["Командная партия", "Голосование за ход", "Несколько фигур на игрока"]
\tvar symbols := ["♞", "♟", "♛"]
\tfor i in range(modes.size()):
\t\tvar x := 0.235 + float(i) * 0.185
\t\tvar b := _ornate_button(menu_panel, symbols[i] + "
" + modes[i] + "
" + subtitles[i], x, 0.735, x + 0.175, 0.885, 15, "card")
\t\tb.pressed.connect(_on_mode_pressed.bind(modes[i]))''', "party modes")

replace_once(
'''b.pressed.connect(_show_notice.bind(nav_names[i] + " — раздел в разработке"))''',
'''if nav_names[i] == "Шахматный город":
\t\t\tb.pressed.connect(func(): _show_notice("ШАХМАТНЫЙ ГОРОД — отдельный режим. Открытые фигуры доступны постоянно, без расхода злотых за вход."))
\t\telse:
\t\t\tb.pressed.connect(_show_notice.bind(nav_names[i] + " — раздел в разработке"))''', "city navigation")

replace_once(
'''status_label.offset_bottom = -8

func _build_piece_preview() -> void:
''',
'''status_label.offset_bottom = -8
\t_build_preparation_screen()

func _build_preparation_screen() -> void:
\tpreparation_panel = Control.new()
\tpreparation_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
\tpreparation_panel.visible = false
\tui.add_child(preparation_panel)
\tvar shade := ColorRect.new()
\tshade.color = Color(0.015, 0.012, 0.010, 0.96)
\tshade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
\tpreparation_panel.add_child(shade)
\tvar frame := _panel(preparation_panel, 0.06, 0.07, 0.94, 0.93)
\t_add_label(frame, "ПОДГОТОВКА К ПАРТИИ", Vector2(24, 16), Vector2(650, 42), 27, PALE_GOLD)
\tvar mode_label := _add_label(frame, "РЕЖИМ: " + selected_mode.to_upper(), Vector2(26, 67), Vector2(500, 28), 16, Color(0.83, 0.77, 0.67))
\tmode_label.name = "PrepModeLabel"
\tvar close := _ornate_button(frame, "← НАЗАД", 0.77, 0.035, 0.97, 0.14, 14, "nav")
\tclose.pressed.connect(_close_preparation)
\t_add_label(frame, "ВЫБЕРИ ФИГУРУ ДЛЯ ЭТОЙ ПАРТИИ", Vector2(26, 112), Vector2(600, 28), 17, PALE_GOLD)
\tvar pieces := ["Пешка", "Конь", "Слон", "Ладья", "Ферзь"]
\tfor i in range(pieces.size()):
\t\tvar y := 0.245 + float(i) * 0.112
\t\tvar piece := pieces[i]
\t\tvar btn := _ornate_button(frame, piece.to_upper(), 0.035, y, 0.30, y + 0.095, 15, "card")
\t\tbtn.pressed.connect(_select_preparation_piece.bind(piece))
\t\tprep_piece_buttons.append(btn)
\tvar info := _panel(frame, 0.35, 0.24, 0.96, 0.72)
\t_add_label(info, "ПРАВИЛА ПОКУПКИ", Vector2(18, 14), Vector2(400, 28), 17, PALE_GOLD)
\t_add_label(info, "Открытие фигуры: XP списывается один раз.
Покупка перед матчем: злотые списываются за каждую партию.
В Шахматном городе открытые фигуры не расходуются.", Vector2(18, 54), Vector2(540, 100), 13, Color(0.84, 0.79, 0.70))
\tvar selected_label := _add_label(info, "ВЫБРАНА: ПЕШКА", Vector2(18, 170), Vector2(500, 30), 18, PALE_GOLD)
\tselected_label.name = "PrepSelectedLabel"
\tprep_status = _add_label(info, "Пешка доступна бесплатно.", Vector2(18, 210), Vector2(540, 55), 13, Color(0.86, 0.81, 0.72))
\tvar action := _ornate_button(info, "ВЫБРАТЬ ФИГУРУ", 0.06, 0.74, 0.92, 0.94, 17, "party")
\taction.name = "PrepActionButton"
\taction.pressed.connect(_purchase_or_unlock_selected)
\t_refresh_preparation_ui()

func _open_preparation() -> void:
\tmenu_panel.visible = false
\tpreparation_panel.visible = true
\tvar mode_label := preparation_panel.find_child("PrepModeLabel", true, false) as Label
\tif mode_label:
\t\tmode_label.text = "РЕЖИМ: " + selected_mode.to_upper()
\t_refresh_preparation_ui()

func _close_preparation() -> void:
\tpreparation_panel.visible = false
\tmenu_panel.visible = true

func _select_preparation_piece(piece_name: String) -> void:
\tselected_prep_piece = PIECES.find(piece_name)
\t_refresh_preparation_ui()

func _refresh_preparation_ui() -> void:
\tif preparation_panel == null:
\t\treturn
\tfor i in range(prep_piece_buttons.size()):
\t\tvar piece: String = ["Пешка", "Конь", "Слон", "Ладья", "Ферзь"][i]
\t\tvar unlocked := unlocked_pieces.has(piece)
\t\tprep_piece_buttons[i].text = ("✓  " if unlocked else "🔒  ") + piece.to_upper()
\tvar piece_name: String = PIECES[selected_prep_piece]
\tvar info := preparation_panel.find_child("PrepSelectedLabel", true, false) as Label
\tvar action := preparation_panel.find_child("PrepActionButton", true, false) as Button
\tif info:
\t\tinfo.text = "ВЫБРАНА: " + piece_name.to_upper()
\tif action:
\t\tif not unlocked_pieces.has(piece_name):
\t\t\taction.text = "ОТКРЫТЬ ЗА %d XP" % int(piece_unlock_xp.get(piece_name, 0))
\t\telif int(match_piece_costs.get(piece_name, 0)) > 0:
\t\t\taction.text = "КУПИТЬ НА ПАРТИЮ — %d ЗЛОТЫХ" % int(match_piece_costs[piece_name])
\t\telse:
\t\t\taction.text = "ВЫБРАТЬ ФИГУРУ"
\tif prep_status:
\t\tif not unlocked_pieces.has(piece_name):
\t\t\tprep_status.text = "Для открытия нужно %d XP. Сейчас: %d XP." % [int(piece_unlock_xp.get(piece_name, 0)), int(balances["xp"])]
\t\telif int(match_piece_costs.get(piece_name, 0)) > 0:
\t\t\tprep_status.text = "Фигура открыта. Покупка на одну партию стоит %d злотых." % int(match_piece_costs[piece_name])
\t\telse:
\t\t\tprep_status.text = "Фигура доступна. Стоимость на эту партию: бесплатно."
\t_save_economy()

func _purchase_or_unlock_selected() -> void:
\tvar piece_name: String = PIECES[selected_prep_piece]
\tif not unlocked_pieces.has(piece_name):
\t\tvar xp_cost := int(piece_unlock_xp.get(piece_name, 0))
\t\tif int(balances["xp"]) < xp_cost:
\t\t\tprep_status.text = "Недостаточно XP. Нужно ещё %d." % (xp_cost - int(balances["xp"]))
\t\t\treturn
\t\tbalances["xp"] = int(balances["xp"]) - xp_cost
\t\tunlocked_pieces.append(piece_name)
\t\tprep_status.text = piece_name + " открыта навсегда. XP списан."
\t\t_save_economy()
\t\t_refresh_preparation_ui()
\t\treturn
\tvar cost := int(match_piece_costs.get(piece_name, 0))
\tif int(balances["zloty"]) < cost:
\t\tprep_status.text = "Недостаточно злотых. Нужно ещё %d." % (cost - int(balances["zloty"]))
\t\treturn
\tbalances["zloty"] = int(balances["zloty"]) - cost
\t_save_economy()
\tprep_status.text = piece_name + " выбрана. Списано %d злотых. Запускаем партию." % cost
\t_confirm_preparation()

func _confirm_preparation() -> void:
\tpreparation_panel.visible = false
\t_start_game(selected_mode)

func _load_economy() -> void:
\tvar cfg := ConfigFile.new()
\tif cfg.load("user://checkmate_economy.cfg") == OK:
\t\tbalances["zloty"] = int(cfg.get_value("wallet", "zloty", balances["zloty"]))
\t\tbalances["xp"] = int(cfg.get_value("wallet", "xp", balances["xp"]))
\t\tbalances["chessmatites"] = int(cfg.get_value("wallet", "chessmatites", balances["chessmatites"]))
\t\tunlocked_pieces = cfg.get_value("progress", "unlocked_pieces", unlocked_pieces)
\t\towned_skins = cfg.get_value("progress", "owned_skins", owned_skins)

func _save_economy() -> void:
\tvar cfg := ConfigFile.new()
\tcfg.set_value("wallet", "zloty", balances["zloty"])
\tcfg.set_value("wallet", "xp", balances["xp"])
\tcfg.set_value("wallet", "chessmatites", balances["chessmatites"])
\tcfg.set_value("progress", "unlocked_pieces", unlocked_pieces)
\tcfg.set_value("progress", "owned_skins", owned_skins)
\tcfg.save("user://checkmate_economy.cfg")

func _build_piece_preview() -> void:
''', "preparation screen and economy logic")

replace_once(
'''func _on_mode_pressed(mode_name: String) -> void:
\tselected_mode = mode_name
\t_start_game(mode_name)''',
'''func _on_mode_pressed(mode_name: String) -> void:
\tselected_mode = mode_name
\t_show_notice("Выбран режим: " + selected_mode + ". Нажми ПАРТИЯ для подготовки.")''', "mode select behavior")

replace_once(
'''func _return_to_menu() -> void:
\tgame_panel.visible = false
\tmenu_panel.visible = true''',
'''func _return_to_menu() -> void:
\tgame_panel.visible = false
\tmenu_panel.visible = true
\t_refresh_wallet_labels()''', "refresh wallet on return")

s += '''
func _refresh_wallet_labels() -> void:
\tvar zloty := menu_panel.find_child("ZlotyCounter", true, false) as Button
\tvar chessmatites := menu_panel.find_child("ChessmatitesCounter", true, false) as Button
\tvar xp := menu_panel.find_child("XPCounter", true, false) as Button
\tif zloty:
\t\tzloty.text = "◈  ЗЛОТЫЕ
%d" % int(balances["zloty"])
\tif chessmatites:
\t\tchessmatites.text = "◆  ШАХМАТИТЫ
%d   +" % int(balances["chessmatites"])
\tif xp:
\t\txp.text = "★  XP
%d" % int(balances["xp"])
'''
script_path.write_text(s, encoding="utf-8")

readme = root / "README_RU.txt"
readme.write_text("""CHECKMATE — Castle Lobby / подготовка к партии

Импортируйте project.godot в Godot 4 и запустите проект.

Изменения:
- Кнопка «ПАРТИЯ» открывает экран подготовки.
- Доступны три типа партии: классика, командное голосование, несколько фигур.
- Открытие фигур расходует XP один раз.
- Покупка фигуры перед партией расходует злотые за каждую партию.
- Злотые, XP, шахматиты и открытые фигуры сохраняются локально.
- «Шахматный город» остаётся отдельным пунктом меню.

Это локальный прототип. Онлайн-матчмейкинг, серверные награды и полноценные режимы ещё не подключены.
""", encoding="utf-8")
