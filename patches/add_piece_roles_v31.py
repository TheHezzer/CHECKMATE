from pathlib import Path

path = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
source = path.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global source
    if old not in source:
        raise SystemExit("Missing anchor: " + label)
    source = source.replace(old, new, 1)

def remove_func(name):
    global source
    marker = "func " + name + "("
    start = source.find(marker)
    if start < 0:
        return
    end = source.find("\nfunc ", start + len(marker))
    if end < 0:
        source = source[:start]
    else:
        source = source[:start] + source[end + 1:]

replace_once('"mode": "classic",\n        "rating": competitive_rating',
             '"mode": "classic",\n        "piece": selected_match_piece,\n        "rating": competitive_rating',
             "send selected chess piece to matchmaking")
replace_once('var line := "%s   •   %d" % [str(player.get("name", "Игрок")), int(player.get("rating", 1000))]',
             'var line := "%s   •   %s   •   %d" % [str(player.get("name", "Игрок")), str(player.get("piece", "Пешка")), int(player.get("rating", 1000))]',
             "show chosen piece beside player nickname and rating")
replace_once('queue_status_label = _add_label(frame, "Подключаемся к рейтинговой очереди…", Vector2(24, 520), Vector2(650, 42), 15, PALE_GOLD)',
             'queue_status_label = _add_label(frame, "Подключаемся к рейтинговой очереди…", Vector2(24, 520), Vector2(650, 42), 15, PALE_GOLD)\n    online_status_label = queue_status_label',
             "route connection status into queue screen")

# Remove obsolete manual room and peer-hosting functions; only the automatic queue remains.
for function_name in ["_create_private_room", "_join_private_room", "_host_online_room", "_join_online_room"]:
    remove_func(function_name)

# Remove obsolete text-entry fields from the old manual room UI.
for declaration in [
    "var online_server_url_input: LineEdit\n",
    "var online_room_code_input: LineEdit\n",
    "var online_ip_input: LineEdit\n"
]:
    source = source.replace(declaration, "")

path.write_text(source, encoding="utf-8")
print("CHECKMATE v31: queue sends selected chess role, roster shows nickname/piece/rating, legacy manual room code removed.")
