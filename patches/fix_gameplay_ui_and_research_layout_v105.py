from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v105 anchor: " + label)
    s = s.replace(old, new, 1)

# Explicitly hide the preview model itself; the SubViewport can otherwise keep
# displaying its texture after the parent menu has been hidden.
rep('''    if preview_container:
        preview_container.visible = false
    if online_panel:
''', '''    if preview_container:
        preview_container.visible = false
    if preview_pawn:
        preview_pawn.visible = false
    if online_panel:
''', "hide preview model during match")
rep('''    if preview_container:
        preview_container.visible = true
    local_bot_test_active = false
''', '''    if preview_container:
        preview_container.visible = true
    if preview_pawn:
        preview_pawn.visible = true
    local_bot_test_active = false
''', "restore preview model on menu return")

# Do not let world-board input intercept taps on visible gameplay controls.
rep('''func _input(event: InputEvent) -> void:
    if game_panel != null and game_panel.visible and world_root.visible:
        if event is InputEventScreenTouch and event.pressed:
            _handle_game_board_click(event.position)
            return
        if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
            _handle_game_board_click(event.position)
            return
''', '''func _is_game_ui_control_hit(screen_position: Vector2) -> bool:
    if game_panel == null:
        return false
    for control in game_panel.find_children("*", "Control", true, false):
        if not control.is_visible_in_tree():
            continue
        if control is Button or control is LineEdit or control is OptionButton:
            if control.get_global_rect().has_point(screen_position):
                return true
    return false

func _input(event: InputEvent) -> void:
    if game_panel != null and game_panel.visible and world_root.visible:
        if event is InputEventScreenTouch and event.pressed:
            if not _is_game_ui_control_hit(event.position):
                _handle_game_board_click(event.position)
                get_viewport().set_input_as_handled()
            return
        if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
            if not _is_game_ui_control_hit(event.position):
                _handle_game_board_click(event.position)
                get_viewport().set_input_as_handled()
            return
''', "protect gameplay buttons from board tap handler")

# Give the compact next-tier research card a non-overlapping vertical layout.
rep('''    var next_title := _add_label(progression_next_card, "УРОВЕНЬ 2", Vector2(10, 8), Vector2(230, 32), 18, PALE_GOLD)
    var lock := _add_label(progression_next_card, "🔒", Vector2(10, 48), Vector2(230, 70), 48, Color(0.78,0.70,0.52))
''', '''    var next_title := _add_label(progression_next_card, "УРОВЕНЬ 2", Vector2(10, 8), Vector2(230, 28), 18, PALE_GOLD)
    next_title.add_theme_font_size_override("font_size", 22)
    var lock := _add_label(progression_next_card, "🔒", Vector2(10, 38), Vector2(230, 44), 32, Color(0.78,0.70,0.52))
    lock.add_theme_font_size_override("font_size", 40)
''', "research next card title and lock")
rep('''    var next_desc := _add_label(progression_next_card, "СЛЕДУЮЩИЙ ПЕРСОНАЖ\\nОткроется после полного исследования уровня 1", Vector2(12, 125), Vector2(230, 78), 13, Color(0.83,0.80,0.74))
''', '''    var next_desc := _add_label(progression_next_card, "СЛЕДУЮЩИЙ ПЕРСОНАЖ\\nОткроется после полного исследования уровня 1", Vector2(12, 84), Vector2(230, 78), 10, Color(0.83,0.80,0.74))
    next_desc.add_theme_font_size_override("font_size", 18)
''', "research next description")
rep('''    var next_progress := _add_label(progression_next_card, "0 / 15 улучшений", Vector2(12, 205), Vector2(230, 28), 13, PALE_GOLD)
''', '''    var next_progress := _add_label(progression_next_card, "0 / 15 улучшений", Vector2(12, 164), Vector2(230, 22), 10, PALE_GOLD)
    next_progress.add_theme_font_size_override("font_size", 18)
''', "research progress label")
rep('''    research_bar.anchor_top = 0.66
    research_bar.anchor_bottom = 0.72
''', '''    research_bar.anchor_top = 0.61
    research_bar.anchor_bottom = 0.66
''', "research progress bar position")
rep('''    growth.anchor_top = 0.72
    growth.anchor_bottom = 0.79
''', '''    growth.anchor_top = 0.67
    growth.anchor_bottom = 0.83
''', "research growth label bounds")
rep('''    growth.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    var next_unlock := _ornate_button(progression_next_card, "ОТКРЫТЬ УРОВЕНЬ", 0.08, 0.79, 0.92, 0.97, 12, "party")
''', '''    growth.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    growth.add_theme_font_size_override("font_size", 18)
    var next_unlock := _ornate_button(progression_next_card, "ОТКРЫТЬ УРОВЕНЬ", 0.08, 0.84, 0.92, 0.98, 10, "party")
''', "research unlock button position")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v105: gameplay UI taps no longer collide with board handling, preview pawn is hidden in matches, and research-card text is fitted.")
