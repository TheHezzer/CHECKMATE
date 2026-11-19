from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "scripts" / "main.gd"
source = path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if old not in source:
        raise SystemExit("Patch anchor not found: " + label)
    source = source.replace(old, new, 1)

replace_once(
    "var selected_prep_piece := 0\n",
    "var selected_prep_piece := 0\nvar selected_match_piece := \"Пешка\"\n",
    "remember selected match piece"
)

replace_once(
'''    balances["zloty"] = int(balances["zloty"]) - cost
    _save_economy()
    prep_status.text = piece_name + " выбрана. Списано %d злотых. Запускаем партию." % cost
    _confirm_preparation()''',
'''    selected_match_piece = piece_name
    balances["zloty"] = int(balances["zloty"]) - cost
    _save_economy()
    prep_status.text = piece_name + " выбрана. Списано %d злотых. Запускаем локальную тестовую партию." % cost
    _confirm_preparation()''',
    "remember piece and clarify local test"
)

replace_once(
'''func _confirm_preparation() -> void:
    preparation_panel.visible = false
    _start_game(selected_mode)''',
'''func _confirm_preparation() -> void:
    if selected_mode != "Классика":
        prep_status.text = "Этот режим ещё разрабатывается. Сейчас доступна только классическая тестовая партия."
        return
    preparation_panel.visible = false
    _start_game(selected_mode)''',
    "guard unfinished modes"
)

replace_once(
'''    if action:
        if not unlocked_pieces.has(piece_name):
            action.text = "ОТКРЫТЬ ЗА %d XP" % int(piece_unlock_xp.get(piece_name, 0))
        elif int(match_piece_costs.get(piece_name, 0)) > 0:
            action.text = "КУПИТЬ НА ПАРТИЮ — %d ЗЛОТЫХ" % int(match_piece_costs[piece_name])
        else:
            action.text = "ВЫБРАТЬ ФИГУРУ"''',
'''    if action:
        if not unlocked_pieces.has(piece_name):
            action.text = "ОТКРЫТЬ ЗА %d XP" % int(piece_unlock_xp.get(piece_name, 0))
        elif int(match_piece_costs.get(piece_name, 0)) > 0:
            action.text = "КУПИТЬ И НАЧАТЬ — %d ЗЛОТЫХ" % int(match_piece_costs[piece_name])
        else:
            action.text = "НАЧАТЬ ТЕСТОВУЮ ПАРТИЮ"''',
    "clarify preparation action"
)

replace_once(
'''    for i in range(min(mode_choice_buttons.size(), names.size())):
        var marker := "◆  " if selected_mode == names[i] else ""
        mode_choice_buttons[i].text = marker + "%02d" % (i + 1) + "  |  " + names[i] + "  |  " + ["Свободная командная игра", "Решение всей команды", "Несколько фигур у игрока"][i]
    if mode_description_label:
        var index := names.find(selected_mode)
        if index < 0:
            index = 0
            selected_mode = names[0]
        mode_description_label.text = captions[index]''',
'''    for i in range(min(mode_choice_buttons.size(), names.size())):
        var marker := "◆  " if selected_mode == names[i] else ""
        mode_choice_buttons[i].disabled = i > 0
        var availability := "ДОСТУПНО" if i == 0 else "СКОРО"
        mode_choice_buttons[i].text = marker + "%02d" % (i + 1) + "  |  " + names[i] + "  |  " + availability
    if mode_description_label:
        var index := names.find(selected_mode)
        if index < 0 or index > 0:
            index = 0
            selected_mode = names[0]
        mode_description_label.text = captions[index] + ("\\n\\nОстальные режимы подключим после завершения классики." if index == 0 else "")''',
    "disable unfinished mode cards"
)

replace_once(
'''func _continue_to_preparation() -> void:
    mode_selection_panel.visible = false
    _open_preparation()''',
'''func _continue_to_preparation() -> void:
    if selected_mode != "Классика":
        selected_mode = "Классика"
    mode_selection_panel.visible = false
    _open_preparation()''',
    "only continue with classic"
)

replace_once(
'''    status_label.text = "Режим: " + mode_name + "  |  Партия началась"''',
'''    status_label.text = "ЛОКАЛЬНЫЙ ТЕСТ • " + mode_name + " • ВЫБРАНАЯ ФИГУРА: " + selected_match_piece + " • ОНЛАЙН ПОДКЛЮЧЕНИЕ ЕЩЁ НЕ НАСТРОЕНО"''',
    "make test status explicit"
)

path.write_text(source, encoding="utf-8")
print("CHECKMATE Party flow v26 patch applied.")
