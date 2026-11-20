from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v99 anchor: " + label)
    s = s.replace(old, new, 1)

# Profile text must stay on one line and never run under the login button.
rep('profile_state_label = _add_label(profile, "", Vector2(94, 39), Vector2(205, 24), 14, Color(0.86, 0.83, 0.76))',
    'profile_state_label = _add_label(profile, "", Vector2(94, 39), Vector2(300, 22), 11, Color(0.86, 0.83, 0.76))',
    "profile state label width")
rep('profile_vip_label = _add_label(profile, "VIP  •  НЕ ПРИОБРЕТЁН", Vector2(94, 67), Vector2(205, 22), 13, Color(0.62, 0.59, 0.54))',
    'profile_vip_label = _add_label(profile, "VIP  •  НЕ ПРИОБРЕТЁН", Vector2(94, 67), Vector2(300, 20), 10, Color(0.62, 0.59, 0.54))',
    "profile vip label width")

# Left cards: keep larger-than-original typography, but prevent title/description overlap.
for name, old_size, new_size in [
    ("task_title", 25, 19), ("task_desc", 20, 15),
    ("pass_title", 25, 19), ("pass_desc", 20, 15),
    ("event_title", 25, 19), ("event_desc", 20, 15),
]:
    rep(f'{name}.add_theme_font_size_override("font_size", {old_size})',
        f'{name}.add_theme_font_size_override("font_size", {new_size})',
        name + " fit card")
    if name.endswith("_title"):
        rep(f'{name}.size = Vector2(285, 34)', f'{name}.size = Vector2(300, 30)', name + " title bounds") if f'{name}.size = Vector2(285, 34)' in s else None

# Navigation buttons were inheriting an oversized global font, clipping labels such as History and Chess City.
rep('    button.add_theme_font_size_override("font_size", font_size + 19)',
    '    button.add_theme_font_size_override("font_size", font_size + (9 if style_kind == "nav" else 19))',
    "navigation font scaling")
rep('    normal.content_margin_left = 28\n    normal.content_margin_right = 28\n    normal.content_margin_top = 17\n    normal.content_margin_bottom = 17',
    '    normal.content_margin_left = 10 if style_kind == "nav" else 28\n    normal.content_margin_right = 10 if style_kind == "nav" else 28\n    normal.content_margin_top = 8 if style_kind == "nav" else 17\n    normal.content_margin_bottom = 8 if style_kind == "nav" else 17',
    "navigation button content margins")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v99: fixed profile text wrapping, left-card overlap and clipped navigation labels.")
