from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'scripts' / 'main.gd'
s = p.read_text(encoding='utf-8')
old = '''    remember_me_checkbox.anchor_left = 0.15
    remember_me_checkbox.anchor_right = 0.85
    remember_me_checkbox.anchor_top = 0.525
    remember_me_checkbox.anchor_bottom = 0.575
    remember_me_checkbox.offset_left = 0
    remember_me_checkbox.offset_right = 0
    remember_me_checkbox.offset_top = 0
    remember_me_checkbox.offset_bottom = 0
    remember_me_checkbox.button_pressed = remember_me
    remember_me_checkbox.add_theme_font_override("font", UI_FONT)
    remember_me_checkbox.add_theme_font_size_override("font_size", 16)
    remember_me_checkbox.add_theme_color_override("font_color", PALE_GOLD)
    remember_me_checkbox.toggled.connect(_on_remember_me_toggled)
    frame.add_child(remember_me_checkbox)

    var login := _ornate_button(frame, "ВОЙТИ ОНЛАЙН", 0.045, 0.59, 0.345, 0.705, 14, "party")
    login.pressed.connect(_account_login)
    var offline := _ornate_button(frame, "ОФЛАЙН • БОТЫ", 0.355, 0.59, 0.645, 0.705, 14, "nav")
    offline.pressed.connect(_account_offline_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.655, 0.59, 0.955, 0.705, 14, "nav")
    register.pressed.connect(_account_register)'''
new = '''    remember_me_checkbox.anchor_left = 0.09
    remember_me_checkbox.anchor_right = 0.91
    remember_me_checkbox.anchor_top = 0.515
    remember_me_checkbox.anchor_bottom = 0.595
    remember_me_checkbox.offset_left = 0
    remember_me_checkbox.offset_right = 0
    remember_me_checkbox.offset_top = 0
    remember_me_checkbox.offset_bottom = 0
    remember_me_checkbox.custom_minimum_size = Vector2(0, 68)
    remember_me_checkbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    remember_me_checkbox.button_pressed = remember_me
    remember_me_checkbox.add_theme_font_override("font", UI_FONT)
    remember_me_checkbox.add_theme_font_size_override("font_size", 22)
    remember_me_checkbox.add_theme_color_override("font_color", Color(1.0, 0.91, 0.68))
    remember_me_checkbox.add_theme_color_override("font_hover_color", Color(1.0, 0.98, 0.86))
    remember_me_checkbox.add_theme_color_override("font_pressed_color", Color(1.0, 0.98, 0.86))
    remember_me_checkbox.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
    remember_me_checkbox.focus_mode = Control.FOCUS_ALL
    remember_me_checkbox.toggled.connect(_on_remember_me_toggled)
    frame.add_child(remember_me_checkbox)

    var login := _ornate_button(frame, "ВОЙТИ ОНЛАЙН", 0.045, 0.615, 0.345, 0.725, 15, "party")
    login.pressed.connect(_account_login)
    var offline := _ornate_button(frame, "ОФЛАЙН • БОТЫ", 0.355, 0.615, 0.645, 0.725, 15, "nav")
    offline.pressed.connect(_account_offline_login)
    var register := _ornate_button(frame, "РЕГИСТРАЦИЯ", 0.655, 0.615, 0.955, 0.725, 15, "nav")
    register.pressed.connect(_account_register)'''
if old not in s: raise SystemExit('checkbox block missing')
s = s.replace(old, new, 1)
s = s.replace('    account_status_label.anchor_top = 0.72\n    account_status_label.anchor_bottom = 0.81', '    account_status_label.anchor_top = 0.74\n    account_status_label.anchor_bottom = 0.825', 1)
s = s.replace('    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.20, 0.835, 0.80, 0.935, 14, "nav")', '    var guest := _ornate_button(frame, "ПРОДОЛЖИТЬ КАК ГОСТЬ", 0.20, 0.845, 0.80, 0.945, 15, "nav")', 1)
p.write_text(s, encoding='utf-8')
print('CHECKMATE v73 readable remember-me checkbox applied')
