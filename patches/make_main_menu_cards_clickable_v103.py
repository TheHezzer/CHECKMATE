from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v103 anchor: " + label)
    s = s.replace(old, new, 1)

rep('    task_desc.clip_text = true',
    '    task_desc.clip_text = true\n    var tasks_hit := Button.new()\n    tasks_hit.name = "OpenDailyTasksFromMenu"\n    tasks_hit.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)\n    tasks_hit.flat = true\n    tasks_hit.focus_mode = Control.FOCUS_NONE\n    tasks_hit.modulate = Color(1, 1, 1, 0.01)\n    tasks_hit.pressed.connect(_open_daily_tasks_from_menu)\n    tasks.add_child(tasks_hit)',
    "daily tasks card click")
rep('    pass_desc.clip_text = true',
    '    pass_desc.clip_text = true\n    var pass_hit := Button.new()\n    pass_hit.name = "OpenSeasonPassFromMenu"\n    pass_hit.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)\n    pass_hit.flat = true\n    pass_hit.focus_mode = Control.FOCUS_NONE\n    pass_hit.modulate = Color(1, 1, 1, 0.01)\n    pass_hit.pressed.connect(_open_season_pass_from_menu)\n    pass_panel.add_child(pass_hit)',
    "season pass card click")
rep('func _open_daily_tasks_screen() -> void:',
    'func _open_daily_tasks_from_menu() -> void:\n    _open_shop_screen()\n    _open_daily_tasks_screen()\n\nfunc _open_season_pass_from_menu() -> void:\n    _open_shop_screen()\n    _open_season_pass_screen()\n\nfunc _open_daily_tasks_screen() -> void:',
    "menu card navigation handlers")
rep('    var team_name := "БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ"\n    var active_name := "ТЫ • ОБЕ СТОРОНЫ" if local_self_play_active else "Игрок " + str(active_teammate)',
    '    var team_name := "БЕЛЫЕ" if current_team == "white" else "ЧЁРНЫЕ"\n    if standard_chess_mode_active:\n        team_turn_label.text = "ХОД: " + team_name\n        return\n    var active_name := "ТЫ • ОБЕ СТОРОНЫ" if local_self_play_active else "Игрок " + str(active_teammate)',
    "standard chess turn label")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v103: daily tasks and season pass cards open their screens; Standard Chess shows only the side to move.")
