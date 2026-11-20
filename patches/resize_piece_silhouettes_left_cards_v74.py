from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'scripts' / 'main.gd'
s = p.read_text(encoding='utf-8')

# Keep the six silhouette buttons safely inside a smaller centered shelf.
old = '''    silhouette_row.anchor_left = 0.185
    silhouette_row.anchor_right = 0.815
    silhouette_row.anchor_top = 0.585
    silhouette_row.anchor_bottom = 0.805
    menu_panel.add_child(silhouette_row)
    for i in range(PIECES.size()):'''
new = '''    silhouette_row.anchor_left = 0.225
    silhouette_row.anchor_right = 0.775
    silhouette_row.anchor_top = 0.595
    silhouette_row.anchor_bottom = 0.735
    silhouette_row.clip_contents = true
    menu_panel.add_child(silhouette_row)
    for i in range(PIECES.size()):'''
if old not in s: raise SystemExit('silhouette shelf layout anchor missing')
s = s.replace(old, new, 1)
old = '''        b.add_theme_font_size_override("font_size", 148)'''
new = '''        b.add_theme_font_size_override("font_size", 88)
        b.clip_text = true
        b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        b.size_flags_vertical = Control.SIZE_EXPAND_FILL'''
if old not in s: raise SystemExit('silhouette font anchor missing')
s = s.replace(old, new, 1)

# Make left feature cards more readable without allowing text to spill outside.
for name, old_size, new_size in [
    ('task_title', 14, 17), ('task_desc', 12, 14),
    ('pass_title', 14, 17), ('pass_desc', 12, 14),
    ('event_title', 14, 17), ('event_desc', 12, 14),
]:
    old = f'{name}.add_theme_font_size_override("font_size", {old_size})'
    new = f'{name}.add_theme_font_size_override("font_size", {new_size})'
    if old not in s: raise SystemExit(f'left card font anchor missing: {name}')
    s = s.replace(old, new, 1)

# Keep descriptions within each card's text column and wrap long phrases cleanly.
for name in ['task_desc', 'pass_desc', 'event_desc']:
    anchor = f'    {name}.add_theme_font_size_override("font_size", 14)'
    replacement = anchor + f'\n    {name}.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART\n    {name}.clip_text = true'
    if anchor not in s: raise SystemExit(f'description layout anchor missing: {name}')
    s = s.replace(anchor, replacement, 1)

p.write_text(s, encoding='utf-8')
print('CHECKMATE v74: smaller clipped silhouettes and clearer left feature cards')
