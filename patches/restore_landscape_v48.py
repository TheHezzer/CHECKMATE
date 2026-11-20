from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
project = root / "project.godot"
if not project.exists():
    raise SystemExit("project.godot not found")

text = project.read_text(encoding="utf-8")
# Remove any previous orientation declaration to avoid duplicate settings.
text = re.sub(r"(?m)^window/handheld/orientation\s*=.*\n?", "", text)
if "[display]" in text:
    text = re.sub(r"(?m)^\\[display\\]\s*$", "[display]\nwindow/handheld/orientation=0", text, count=1)
else:
    text += "\n[display]\nwindow/handheld/orientation=0\n"
project.write_text(text, encoding="utf-8")

# Keep Android export preset in landscape too, when a preset file exists.
presets = root / "export_presets.cfg"
if presets.exists():
    ptext = presets.read_text(encoding="utf-8")
    ptext = re.sub(r"(?m)^screen/orientation\s*=.*$", "screen/orientation=0", ptext)
    presets.write_text(ptext, encoding="utf-8")

print("Landscape orientation applied (Godot orientation=0).")
