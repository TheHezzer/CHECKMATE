from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# Compact all three wallet values in the persistent top strip.
wallet_start = s.index("func _build_wallet_hud()")
wallet_end = s.index("\nfunc _refresh_wallet_hud()", wallet_start)
wallet = s[wallet_start:wallet_end]
old = 'label.add_theme_font_size_override("font_size", 17)'
if old not in wallet:
    raise SystemExit("Wallet label font anchor not found")
wallet = wallet.replace(old, 'label.add_theme_font_size_override("font_size", 13)', 1)
s = s[:wallet_start] + wallet + s[wallet_end:]

# The three left-side information cards should use the former wallet text scale.
# Keep icon glyphs larger; adjust only headings and explanatory text.
for name in ["task_title", "task_desc", "pass_title", "pass_desc", "event_title", "event_desc"]:
    marker = name + '.add_theme_font_size_override("font_size", '
    start = s.find(marker)
    if start < 0:
        raise SystemExit("Left card font anchor not found: " + name)
    end = s.find(")", start)
    s = s[:start] + marker + "17)" + s[end+1:]

p.write_text(s, encoding="utf-8")
print("CHECKMATE v70: wallet text reduced to 13; all three left info cards use 17-point text.")
