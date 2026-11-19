from pathlib import Path

root = Path(__file__).resolve().parent.parent
main_path = root / "scripts" / "main.gd"
source = main_path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if old not in source:
        raise SystemExit("Patch anchor not found: " + label)
    source = source.replace(old, new, 1)

replace_once(
    "var preparation_panel: Control\n",
    "var preparation_panel: Control\nvar mode_selection_panel: Control\nvar mode_choice_buttons: Array[Button] = []\nvar mode_description_label: Label\n",
    "mode selection variables"
)

replace_once(
    "party.pressed.connect(_open_preparation)",
    "party.pressed.connect(_open_mode_selection)",
    "party opens mode selection"
)

source += '''

func _open_mode_selection() -> void:
    if mode_selection_panel == null:
        _build_mode_selection_screen()
    menu_panel.visible = false
    preparation_panel.visible = false
    mode_selection_panel.visible = true
    _refresh_mode_selection()

func _build_mode_selection_screen() -> void:
    mode_selection_panel = Control.new()
    mode_selection_panel.name = "ModeSelectionScreen"
    mode_selection_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mode_selection_panel.visible = false
    ui.add_child(mode_selection_panel)

    var shade := ColorRect.new()
    shade.color = Color(0.012, 0.010, 0.009, 0.97)
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    mode_selection_panel.add_child(shade)

    var frame := _panel(mode_selection_panel, 0.045, 0.055, 0.955, 0.945)
    _add_label(frame, "ВЫБОР ИГРОВОГО РЕЖИМА", Vector2(24, 18), Vector2(680, 42), 27, PALE_GOLD)
    _add_label(frame, "Выбери правила командной партии", Vector2(26, 62), Vector2(580, 26), 15, Color(0.78, 0.72, 0.63))

    var back := _ornate_button(frame, "← НАЗАД", 0.80, 0.035, 0.97, 0.135, 14, "nav")
    back.pressed.connect(_close_mode_selection)

    var names := ["Классика", "Командное голосование", "Несколько фигур"]
    var symbols := ["01", "02", "03"]
    var captions := [
        "Свободная командная игра",
        "Решение всей команды",
        "Несколько фигур у игрока"
    ]
    for i in range(names.size()):
        var left := 0.035 + float(i) * 0.315
        var card_text := symbols[i] + "\\n" + names[i] + "\\n" + captions[i]
        var card := _ornate_button(frame, card_text, left, 0.235, left + 0.285, 0.57, 16, "card")
        card.pressed.connect(_select_mode_card.bind(names[i]))
        mode_choice_buttons.append(card)

    var details := _panel(frame, 0.035, 0.625, 0.965, 0.835)
    _add_label(details, "КАК ПРОХОДИТ РЕЖИМ", Vector2(18, 12), Vector2(500, 26), 16, PALE_GOLD)
    mode_description_label = _add_label(details, "", Vector2(18, 47), Vector2(760, 66), 14, Color(0.86, 0.81, 0.72))
    var next_button := _ornate_button(frame, "ПРОДОЛЖИТЬ  →", 0.67, 0.865, 0.965, 0.975, 17, "party")
    next_button.pressed.connect(_continue_to_preparation)

    _refresh_mode_selection()

func _select_mode_card(mode_name: String) -> void:
    selected_mode = mode_name
    _refresh_mode_selection()

func _refresh_mode_selection() -> void:
    var names := ["Классика", "Командное голосование", "Несколько фигур"]
    var captions := [
        "Каждый участник управляет своей фигурой. В свой ход игрок может сделать допустимый ход или передать очередь союзнику. Команда играет против другой команды.",
        "Игрок предлагает ход, а союзники обсуждают и голосуют. За правильное командное решение предусмотрен бонус к наградам. Голосование ограничено временем.",
        "У каждого участника может быть несколько фигур. Игрок выбирает, какой фигурой ходить, или передаёт очередь союзнику. Система подсказывает, кому лучше передать ход."
    ]
    for i in range(min(mode_choice_buttons.size(), names.size())):
        var marker := "◆  " if selected_mode == names[i] else ""
        mode_choice_buttons[i].text = marker + "%02d" % (i + 1) + "\\n" + names[i] + "\\n" + ["Свободная командная игра", "Решение всей команды", "Несколько фигур у игрока"][i]
    if mode_description_label:
        var index := names.find(selected_mode)
        if index < 0:
            index = 0
            selected_mode = names[0]
        mode_description_label.text = captions[index]

func _continue_to_preparation() -> void:
    mode_selection_panel.visible = false
    _open_preparation()

func _close_mode_selection() -> void:
    if mode_selection_panel:
        mode_selection_panel.visible = false
    menu_panel.visible = true
'''
main_path.write_text(source, encoding="utf-8")
print("Mode selection screen patch applied.")
