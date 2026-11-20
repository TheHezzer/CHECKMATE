from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

# Add a compact visual research progress bar to the next-tier card.
anchor = '    next_progress.name = "NextResearchProgress"\n'
if anchor not in s:
    raise SystemExit("Next-tier progress label anchor missing")
if 'NextTierResearchBar' not in s:
    s = s.replace(anchor, anchor + '''    var research_bar := ProgressBar.new()
    research_bar.name = "NextTierResearchBar"
    research_bar.min_value = 0
    research_bar.max_value = 15
    research_bar.value = 0
    research_bar.show_percentage = false
    research_bar.anchor_left = 0.07
    research_bar.anchor_right = 0.93
    research_bar.anchor_top = 0.66
    research_bar.anchor_bottom = 0.72
    research_bar.offset_left = 0
    research_bar.offset_right = 0
    research_bar.offset_top = 0
    research_bar.offset_bottom = 0
    progression_next_card.add_child(research_bar)
    var growth := _add_label(progression_next_card, "РОСТ ХАРАКТЕРИСТИК\n+10 HP  •  +5 ЩИТ  •  +5 АТАКА", Vector2(10, 0), Vector2(230, 44), 12, Color(0.78,0.88,0.72))
    growth.name = "NextTierGrowth"
    growth.anchor_left = 0.05
    growth.anchor_right = 0.95
    growth.anchor_top = 0.72
    growth.anchor_bottom = 0.79
    growth.offset_left = 0
    growth.offset_right = 0
    growth.offset_top = 0
    growth.offset_bottom = 0
    growth.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    growth.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    growth.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
''', 1)

# Display the actual 0..15 research progress and compare the next tier
# against the fully upgraded previous tier.
anchor2 = '    var next_unlock := progression_next_card.find_child("NextTierUnlockButton", true, false) as Button\n'
if anchor2 not in s:
    raise SystemExit("Next-tier unlock button lookup anchor missing")
s = s.replace(anchor2, anchor2 + '''    var research_bar := progression_next_card.find_child("NextTierResearchBar", true, false) as ProgressBar
    var growth_label := progression_next_card.find_child("NextTierGrowth", true, false) as Label
''', 1)
anchor3 = '    if next_progress:\n        next_progress.text = "15 / 15 улучшений" if unlocked else "%d / 15 улучшений" % total\n'
if anchor3 not in s:
    raise SystemExit("Next-tier progress text anchor missing")
s = s.replace(anchor3, anchor3 + '''    if research_bar:
        research_bar.value = total
    if growth_label:
        growth_label.text = "РОСТ К МАКСИМУМУ ПРЕДЫДУЩЕГО\n+10 HP  •  +5 ЩИТ  •  +5 АТАКА"
''', 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v81: visual 15-step research progress and clear next-tier stat growth comparison.")
