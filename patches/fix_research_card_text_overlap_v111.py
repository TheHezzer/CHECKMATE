from pathlib import Path
p = Path(__file__).resolve().parents[1] / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")
repls = [
    ('next_desc.add_theme_font_size_override("font_size", 18)', 'next_desc.add_theme_font_size_override("font_size", 13)'),
    ('next_progress.add_theme_font_size_override("font_size", 18)', 'next_progress.add_theme_font_size_override("font_size", 13)'),
    ('growth.add_theme_font_size_override("font_size", 18)', 'growth.add_theme_font_size_override("font_size", 13)'),
    ('lock.add_theme_font_size_override("font_size", 40)', 'lock.add_theme_font_size_override("font_size", 30)'),
]
for old, new in repls:
    if old not in s:
        raise SystemExit(f"Expected research layout code not found: {old}")
    s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("v111 research card typography compacted")

# Rebuild after correcting the v111 output archive path.
