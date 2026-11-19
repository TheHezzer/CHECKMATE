from pathlib import Path
p=Path(__file__).resolve().parent.parent/'scripts'/'main.gd'
s=p.read_text(encoding='utf-8')
def rep(a,b,n):
 global s
 if a not in s: raise SystemExit('Missing anchor: '+n)
 s=s.replace(a,b,1)
rep('var menu_panel: Control\n','var menu_panel: Control\nvar onboarding_panel: Control\nvar onboarding_title: Label\nvar onboarding_body: Label\nvar onboarding_progress: Label\nvar onboarding_next_button: Button\nvar onboarding_step := 0\nvar onboarding_completed := false\n','tutorial state')
rep('        persistent_player_id = str(cfg.get_value("identity", "player_id", ""))\n','        persistent_player_id = str(cfg.get_value("identity", "player_id", ""))\n        onboarding_completed = bool(cfg.get_value("onboarding", "completed", false))\n','load tutorial flag')
rep('    cfg.set_value("identity", "player_id", persistent_player_id)\n','    cfg.set_value("identity", "player_id", persistent_player_id)\n    cfg.set_value("onboarding", "completed", onboarding_completed)\n','save tutorial flag')
rep('    _build_preparation_screen()\n    _build_online_panel_screen()\n','    _build_preparation_screen()\n    _build_online_panel_screen()\n    _build_onboarding_screen()\n    if not onboarding_completed:\n        _open_onboarding()\n','launch tutorial')
rep('const CLASSIC_TEAM_SIZE := 16','const CLASSIC_TEAM_SIZE := 8','8 players per team')
rep('var selected_match_piece := "Пешка"','var selected_match_piece := "Конь"','default extra piece')
rep('var selected_prep_piece := 0','var selected_prep_piece := 2','default prep knight')
rep('var pieces := ["Пешка", "Конь", "Слон", "Ладья", "Ферзь"]','var pieces := ["Конь", "Слон", "Ладья", "Ферзь", "Король"]','extra piece choices')
rep('var piece: String = ["Пешка", "Конь", "Слон", "Ладья", "Ферзь"][i]','var piece: String = ["Конь", "Слон", "Ладья", "Ферзь", "Король"][i]','prep piece labels')
rep('16 НА 16','8 НА 8','queue heading')
rep('Ищем 32 игроков с близким рейтингом.','Ищем 16 игроков с близким рейтингом.','queue size')
rep('найдено %d из 32','найдено %d из 16','queue count')
rep('32 игрока подобраны.','16 игроков подобраны.','match count')
rep('var line := "%s   •   %s   •   %d" % [str(player.get("name", "Игрок")), str(player.get("piece", "Пешка")), int(player.get("rating", 1000))]','var line := "%s   •   Пешка + %s   •   %d" % [str(player.get("name", "Игрок")), str(player.get("secondPiece", player.get("piece", "Конь"))), int(player.get("rating", 1000))]','roster pieces')
rep('    var name: String = PIECES[index]\n    _build_preview_piece(name)','    var name: String = PIECES[index]\n    if name == "Пешка":\n        _show_notice("Пешка всегда входит в комплект. Выбери дополнительную фигуру.")\n        return\n    _build_preview_piece(name)','pawn not second figure')
rep('"ХОД: БЕЛЫЕ • ИГРОК 1/4"','"ХОД: БЕЛЫЕ • ИГРОК 1/8"','turn heading')
rep('(active_teammate % 4) + 1','(active_teammate % 8) + 1','8 player turn order')
rep(' + "/4"',' + "/8"','turn count')
s += r"""

func _build_onboarding_screen() -> void:
    onboarding_panel = Control.new()
    onboarding_panel.name = "FirstLaunchTutorial"
    onboarding_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    onboarding_panel.visible = false
    ui.add_child(onboarding_panel)
    var shade := ColorRect.new()
    shade.color = Color(0.008, 0.007, 0.006, 0.985)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_STOP
    onboarding_panel.add_child(shade)
    var frame := _panel(onboarding_panel, 0.10, 0.105, 0.90, 0.895)
    _add_label(frame, "CHECKMATE • ПЕРВОЕ ОБУЧЕНИЕ", Vector2(28,22), Vector2(700,42), 27, PALE_GOLD)
    onboarding_progress = _add_label(frame, "ШАГ 1 ИЗ 5", Vector2(30,78), Vector2(300,28), 15, Color(0.80,0.73,0.62))
    onboarding_title = _add_label(frame, "ДОБРО ПОЖАЛОВАТЬ", Vector2(30,145), Vector2(820,52), 28, PALE_GOLD)
    onboarding_body = _add_label(frame, "", Vector2(34,220), Vector2(820,210), 19, Color(0.90,0.86,0.78))
    onboarding_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _add_label(frame, "Обучение проходит один раз. Его можно будет повторить в разделе помощи.", Vector2(32,455), Vector2(800,35), 13, Color(0.70,0.65,0.57))
    onboarding_next_button = _ornate_button(frame, "ПРОДОЛЖИТЬ →", 0.63,0.82,0.96,0.96,17,"party")
    onboarding_next_button.pressed.connect(_advance_onboarding)
    _refresh_onboarding_step()

func _open_onboarding() -> void:
    onboarding_step = 0
    menu_panel.visible = false
    if preparation_panel: preparation_panel.visible = false
    if mode_selection_panel: mode_selection_panel.visible = false
    if online_panel: online_panel.visible = false
    onboarding_panel.visible = true
    _refresh_onboarding_step()

func _refresh_onboarding_step() -> void:
    var titles := ["ТВОЁ ГЛАВНОЕ МЕНЮ","ПРОФИЛЬ, РЕЙТИНГ И РЕСУРСЫ","МАГАЗИН И ОТКРЫТИЕ ФИГУР","ТВОЯ КОМАНДА И ДВЕ ФИГУРЫ","ПОИСК ПАРТИИ И ВЫБЫВАНИЕ"]
    var bodies := [
        "Здесь начинается CHECKMATE. Кнопка ПАРТИЯ ведёт к выбору режима и подготовке. Внизу находятся магазин, рейтинг, кланы, шахматный город, коллекция и пропуск.",
        "Слева расположен профиль. Вверху показаны злотые, премиальная валюта и опыт XP. Рейтинг отражает результат в соревновательных матчах. Часть разделов пока в разработке.",
        "Фигуры открываются за XP. Дополнительная боевая фигура покупается за злотые перед классической партией. Скины после покупки остаются навсегда. Закрытые фигуры отмечены замком.",
        "В команде 8 игроков. У каждого две фигуры: своя пешка и одна выбранная дополнительная фигура. Всего на стороне 16 фигур. После обучения открыты пешка и конь; остальные фигуры нужно открыть.",
        "Игра ищет соперников: 8 на 8, с подбором по рейтингу. Если обе твои фигуры выбиты, ты становишься зрителем: смотришь партию и пишешь в командный чат, но не ходишь. Для новой игры выйди в меню и запишись снова."
    ]
    onboarding_progress.text = "ШАГ %d ИЗ %d" % [onboarding_step+1,titles.size()]
    onboarding_title.text = titles[onboarding_step]
    onboarding_body.text = bodies[onboarding_step]
    onboarding_next_button.text = "ЗАВЕРШИТЬ ОБУЧЕНИЕ ✓" if onboarding_step == 4 else "ПРОДОЛЖИТЬ →"

func _advance_onboarding() -> void:
    if onboarding_step < 4:
        onboarding_step += 1
        _refresh_onboarding_step()
        return
    onboarding_completed = true
    if not unlocked_pieces.has("Пешка"): unlocked_pieces.append("Пешка")
    if not unlocked_pieces.has("Конь"): unlocked_pieces.append("Конь")
    balances["zloty"] = int(balances["zloty"]) + 500
    balances["xp"] = int(balances["xp"]) + 100
    _save_economy()
    _refresh_wallet_labels()
    _refresh_main_piece_shelf()
    onboarding_panel.visible = false
    menu_panel.visible = true
    _show_notice("Обучение завершено! Пешка и конь открыты. Награда: 500 злотых и 100 XP.")
"""

p.write_text(s, encoding='utf-8')
print('CHECKMATE v33 tutorial and 8v8 two-piece client patch applied')
