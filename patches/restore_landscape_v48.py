from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
project = root / "project.godot"
if not project.exists():
    raise SystemExit("project.godot not found")

lines = project.read_text(encoding="utf-8").splitlines()
lines = [line for line in lines if not line.startswith("window/handheld/orientation=")]
try:
    index = lines.index("[display]")
    lines.insert(index + 1, "window/handheld/orientation=0")
except ValueError:
    lines.extend(["", "[display]", "window/handheld/orientation=0"])
project.write_text("\n".join(lines) + "\n", encoding="utf-8")

presets = root / "export_presets.cfg"
if presets.exists():
    ptext = presets.read_text(encoding="utf-8")
    ptext = re.sub(r"(?m)^screen/orientation=.*$", "screen/orientation=0", ptext)
    presets.write_text(ptext, encoding="utf-8")

print("Landscape orientation applied (Godot orientation=0).")
