from pathlib import Path
import re

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

pattern = r"func _build_startup_sequence\(\) -> void:\n.*?(?=\nfunc _advance_startup_progress\(\) -> void:)"
replacement = """func _build_startup_sequence() -> void:
    # The campaign intro is only a placeholder. Do not block the player with it.
    onboarding_completed = true
    if onboarding_panel:
        onboarding_panel.visible = false
    if menu_panel:
        menu_panel.visible = true
    _save_economy()
    startup_panel = Control.new()
    startup_panel.name = "CampaignIntroAndLoading"
    startup_panel.visible = false
    ui.add_child(startup_panel)
"""
s, count = re.subn(pattern, replacement, s, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Could not locate startup intro function; refusing to patch.")
p.write_text(s, encoding="utf-8")
print("CHECKMATE v98: removed blocking campaign intro and Continue button; main menu opens directly.")
