from pathlib import Path
p=Path(__file__).resolve().parent.parent/"scripts"/"main.gd"
s=p.read_text(encoding="utf-8")
def rep(old,new,label):
    global s
    if old not in s: raise SystemExit("Missing: "+label)
    s=s.replace(old,new,1)

# Remove every standalone rating shortcut. Rating remains in the player profile beside the portrait.
rep('''    var quick_names := ["История", "Рейтинг", "Кланы", "Настройки"]
    var quick_icons := ["◷", "🏆", "♟", "⚙"]
    for i in range(quick_names.size()):
        var x := 0.775 + float(i) * 0.052
        var q := _ornate_button(menu_panel, quick_icons[i] + "\\n" + quick_names[i], x, 0.018, x + 0.050, 0.115, 12, "nav")
        if quick_names[i] == "Рейтинг":
            q.text = quick_icons[i] + "\\nРейтинг\\n%d • %s" % [competitive_rating, _rating_division()]
            q.pressed.connect(_show_rating_details)
        elif quick_names[i] == "История":
            q.pressed.connect(_open_match_history.bind(true))
        else:
            q.pressed.connect(_show_notice.bind(quick_names[i] + " — раздел в разработке"))''','''    var quick_names := ["История", "Кланы", "Настройки"]
    var quick_icons := ["◷", "♟", "⚙"]
    for i in range(quick_names.size()):
        var x := 0.775 + float(i) * 0.070
        var q := _ornate_button(menu_panel, quick_icons[i] + "\\n" + quick_names[i], x, 0.018, x + 0.066, 0.115, 12, "nav")
        if quick_names[i] == "История":
            q.pressed.connect(_open_match_history.bind(true))
        else:
            q.pressed.connect(_show_notice.bind(quick_names[i] + " — раздел в разработке"))''',"remove top rating shortcut")
rep('''    var nav_names := ["Магазин", "Рейтинг", "Кланы", "Шахматный город", "Коллекция", "Пропуск"]
    var nav_icons := ["♜", "▥", "⚑", "♜", "♛", "▣"]
    for i in range(nav_names.size()):
        var x := 0.012 + float(i) * 0.163
        var b := _ornate_button(menu_panel, nav_icons[i] + "\\n" + nav_names[i], x, 0.875, x + 0.158, 0.995, 12, "nav")
        if nav_names[i] == "Шахматный город":
            b.pressed.connect(_open_city_screen)
        elif nav_names[i] == "Рейтинг":
            b.text = nav_icons[i] + "\\nРейтинг\\n%d" % competitive_rating
            b.pressed.connect(_show_rating_details)
        else:
            b.disabled = true
            b.text = "🔒  " + nav_names[i].to_upper() + "\\nСКОРО"
            b.add_theme_font_size_override("font_size", 13)''','''    var nav_names := ["Магазин", "Кланы", "Шахматный город", "Коллекция", "Пропуск"]
    var nav_icons := ["♜", "⚑", "♜", "♛", "▣"]
    for i in range(nav_names.size()):
        var x := 0.012 + float(i) * 0.197
        var b := _ornate_button(menu_panel, nav_icons[i] + "\\n" + nav_names[i], x, 0.875, x + 0.190, 0.995, 12, "nav")
        if nav_names[i] == "Шахматный город":
            b.pressed.connect(_open_city_screen)
        else:
            b.disabled = true
            b.text = "🔒  " + nav_names[i].to_upper() + "\\nСКОРО"
            b.add_theme_font_size_override("font_size", 13)''',"remove bottom rating and rebalance navigation")

# Rebuild the left information cards with restrained typography and wider text area.
rep('''    var tasks := _panel(menu_panel, 0.015, 0.235, 0.185, 0.375)
    _add_label(tasks, "♜", Vector2(12, 12), Vector2(48, 54), 34, PALE_GOLD)
    _add_label(tasks, "ЕЖЕДНЕВНЫЕ ЗАДАЧИ", Vector2(67, 12), Vector2(175, 28), 15, PALE_GOLD)
    _add_label(tasks, "Награды за победы и испытания", Vector2(67, 47), Vector2(175, 38), 10, Color(0.88, 0.82, 0.73))
    var pass_panel := _panel(menu_panel, 0.015, 0.405, 0.185, 0.545)
    _add_label(pass_panel, "♜", Vector2(12, 12), Vector2(48, 54), 34, PALE_GOLD)
    _add_label(pass_panel, "БОЕВОЙ ПРОПУСК", Vector2(67, 12), Vector2(175, 28), 15, PALE_GOLD)
    _add_label(pass_panel, "Уровень 12 • Награды сезона", Vector2(67, 47), Vector2(175, 38), 10, Color(0.88, 0.82, 0.73))
    var event_panel := _panel(menu_panel, 0.015, 0.575, 0.185, 0.735)
    _add_label(event_panel, "⚜", Vector2(12, 12), Vector2(48, 54), 34, PALE_GOLD)
    _add_label(event_panel, "СОБЫТИЕ", Vector2(67, 10), Vector2(180, 26), 15, PALE_GOLD)
    _add_label(event_panel, "«Осенний турнир» • до конца 7 д. 14 ч.", Vector2(67, 40), Vector2(170, 42), 10, Color(0.88, 0.82, 0.73))''','''    var tasks := _panel(menu_panel, 0.015, 0.235, 0.205, 0.375)
    var task_icon := _add_label(tasks, "♜", Vector2(12, 12), Vector2(42, 54), 18, PALE_GOLD)
    task_icon.add_theme_font_size_override("font_size", 31)
    var task_title := _add_label(tasks, "ЕЖЕДНЕВНЫЕ ЗАДАЧИ", Vector2(60, 8), Vector2(245, 34), 7, PALE_GOLD)
    task_title.add_theme_font_size_override("font_size", 19)
    var task_desc := _add_label(tasks, "Награды за победы и испытания", Vector2(60, 43), Vector2(245, 42), 4, Color(0.88, 0.82, 0.73))
    task_desc.add_theme_font_size_override("font_size", 15)
    var pass_panel := _panel(menu_panel, 0.015, 0.405, 0.205, 0.545)
    var pass_icon := _add_label(pass_panel, "♜", Vector2(12, 12), Vector2(42, 54), 18, PALE_GOLD)
    pass_icon.add_theme_font_size_override("font_size", 31)
    var pass_title := _add_label(pass_panel, "БОЕВОЙ ПРОПУСК", Vector2(60, 8), Vector2(245, 34), 7, PALE_GOLD)
    pass_title.add_theme_font_size_override("font_size", 19)
    var pass_desc := _add_label(pass_panel, "Уровень 12 • Награды сезона", Vector2(60, 43), Vector2(245, 42), 4, Color(0.88, 0.82, 0.73))
    pass_desc.add_theme_font_size_override("font_size", 15)
    var event_panel := _panel(menu_panel, 0.015, 0.575, 0.205, 0.735)
    var event_icon := _add_label(event_panel, "⚜", Vector2(12, 12), Vector2(42, 54), 18, PALE_GOLD)
    event_icon.add_theme_font_size_override("font_size", 31)
    var event_title := _add_label(event_panel, "СОБЫТИЕ", Vector2(60, 8), Vector2(245, 34), 7, PALE_GOLD)
    event_title.add_theme_font_size_override("font_size", 19)
    var event_desc := _add_label(event_panel, "«Осенний турнир»\\nДо конца: 7 д. 14 ч.", Vector2(60, 40), Vector2(245, 48), 4, Color(0.88, 0.82, 0.73))
    event_desc.add_theme_font_size_override("font_size", 15)''',"redesign left cards typography and spacing")

p.write_text(s,encoding="utf-8")
print("CHECKMATE v60 rating shortcuts removed and left menu typography repaired")
