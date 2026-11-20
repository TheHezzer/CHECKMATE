from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

anchor = '''    var details := _panel(frame, 0.025, 0.545, 0.975, 0.965)'''
replacement = '''    var details := _panel(frame, 0.025, 0.535, 0.975, 0.835)'''
if anchor not in s:
    raise SystemExit("Mode details panel anchor not found")
s = s.replace(anchor, replacement, 1)

anchor = '''    details.add_child(mode_description_label)
    _refresh_mode_selection()
'''
replacement = '''    details.add_child(mode_description_label)

    var start_button := _ornate_button(frame, "НАЧАТЬ  →", 0.30, 0.855, 0.70, 0.965, 19, "party")
    start_button.name = "StartSelectedModeButton"
    start_button.pressed.connect(_continue_to_preparation)

    _refresh_mode_selection()
'''
if anchor not in s:
    raise SystemExit("Mode description end anchor not found")
s = s.replace(anchor, replacement, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v67: added a dedicated START button to the mode selection screen.")
