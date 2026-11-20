from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

old = """    _build_onboarding_screen()
    if not onboarding_completed:
        _open_onboarding()
"""
new = """    _build_onboarding_screen()
    # Skip the blocking first-run tutorial: launch directly into the main menu.
    onboarding_completed = true
    onboarding_panel.visible = false
    menu_panel.visible = true
"""
if old not in s:
    raise SystemExit("Missing startup onboarding anchor; refusing to patch an unexpected project version.")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("CHECKMATE v98: first-run Continue/tutorial screen skipped; main menu opens immediately.")
