from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "scripts" / "main.gd"
source = path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if old not in source:
        raise SystemExit("Rating patch anchor missing: " + label)
    source = source.replace(old, new, 1)

replace_once(
'''var online_player_id := ""
''',
'''var online_player_id := ""
var competitive_rating := 1000
var persistent_player_id := ""
''', "rating variables")

replace_once(
'''        q.pressed.connect(_show_notice.bind(quick_names[i] + " — раздел в разработке"))''',
'''        if quick_names[i] == "Рейтинг":
            q.text = quick_icons[i] + "\\nРейтинг\\n%d • %s" % [competitive_rating, _rating_division()]
            q.pressed.connect(_show_rating_details)
        else:
            q.pressed.connect(_show_notice.bind(quick_names[i] + " — раздел в разработке"))''', "quick rating button")

replace_once(
'''        if nav_names[i] == "Шахматный город":
            b.pressed.connect(func(): _show_notice("ШАХМАТНЫЙ ГОРОД — отдельный режим. Открытые фигуры доступны постоянно, без расхода злотых за вход."))
        else:
            b.pressed.connect(_show_notice.bind(nav_names[i] + " — раздел в разработке"))''',
'''        if nav_names[i] == "Шахматный город":
            b.pressed.connect(func(): _show_notice("ШАХМАТНЫЙ ГОРОД — отдельный режим. Открытые фигуры доступны постоянно, без расхода злотых за вход."))
        elif nav_names[i] == "Рейтинг":
            b.text = nav_icons[i] + "\\nРейтинг\\n%d" % competitive_rating
            b.pressed.connect(_show_rating_details)
        else:
            b.pressed.connect(_show_notice.bind(nav_names[i] + " — раздел в разработке"))''', "bottom rating button")

replace_once(
'''        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)
''',
'''        owned_skins = cfg.get_value("progress", "owned_skins", owned_skins)
        competitive_rating = clampi(int(cfg.get_value("ranked", "rating", 1000)), 0, 100000)
        persistent_player_id = str(cfg.get_value("identity", "player_id", ""))
    if persistent_player_id.is_empty():
        persistent_player_id = Crypto.new().generate_random_bytes(16).hex_encode()
        _save_economy()
''', "load rating and identity")

replace_once(
'''    cfg.set_value("progress", "owned_skins", owned_skins)
    cfg.save("user://checkmate_economy.cfg")''',
'''    cfg.set_value("progress", "owned_skins", owned_skins)
    cfg.set_value("ranked", "rating", competitive_rating)
    cfg.set_value("identity", "player_id", persistent_player_id)
    cfg.save("user://checkmate_economy.cfg")''', "save rating and identity")

replace_once(
'''func _make_online_player_id() -> String:
    return str(Time.get_unix_time_from_system()) + "-" + str(randi()) + "-" + str(OS.get_process_id())''',
'''func _make_online_player_id() -> String:
    if persistent_player_id.is_empty():
        persistent_player_id = Crypto.new().generate_random_bytes(16).hex_encode()
        _save_economy()
    return persistent_player_id

func _rating_division() -> String:
    if competitive_rating >= 1800:
        return "АЛМАЗ"
    if competitive_rating >= 1600:
        return "ПЛАТИНА"
    if competitive_rating >= 1400:
        return "ЗОЛОТО"
    if competitive_rating >= 1200:
        return "СЕРЕБРО"
    return "БРОНЗА"

func _show_rating_details() -> void:
    _show_notice("ТВОЙ РЕЙТИНГ: %d\\nДИВИЗИОН: %s\\nНачальный рейтинг — 1000. Очки будут изменяться после подтверждённых результатов рейтинговых матчей." % [competitive_rating, _rating_division()])''',
"stable player identity and rating panel")

source = source.replace('"rating": DEFAULT_MATCHMAKING_RATING', '"rating": competitive_rating')
if '"rating": DEFAULT_MATCHMAKING_RATING' in source:
    raise SystemExit("Temporary matchmaking rating was not fully replaced")

path.write_text(source, encoding="utf-8")
print("Persistent competitive rating and stable player identity integrated.")
