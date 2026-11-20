from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")
old = '''    if not developer_mode or game_over or current_team == local_user_team or not game_panel.visible:
        return
'''
new = '''    if not developer_mode or game_over or (current_team == local_user_team and active_teammate == local_user_slot) or not game_panel.visible:
        return
'''
if old not in s:
    raise SystemExit("Missing bot turn guard")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("Fixed bot guard: bots now act for teammate slots on both teams.")
