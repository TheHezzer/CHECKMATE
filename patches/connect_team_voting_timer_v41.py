from pathlib import Path

root = Path(__file__).resolve().parent.parent
script_path = root / "scripts" / "main.gd"
s = script_path.read_text(encoding="utf-8")
old = '''        status_label.text = vote_text
    var chat_lines := PackedStringArray()'''
new = '''        var expires_at_ms := int(pending_vote.get("expiresAt", 0))
        var remaining_ms := maxi(0, expires_at_ms - int(Time.get_unix_time_from_system() * 1000.0))
        var seconds_left := int(ceil(float(remaining_ms) / 1000.0))
        vote_text += "\\nДО КОНЦА ГОЛОСОВАНИЯ: %d СЕК." % seconds_left
        status_label.text = vote_text
    var chat_lines := PackedStringArray()'''
if s.count(old) != 1:
    raise SystemExit(f"vote countdown insertion point: expected one match, found {s.count(old)}")
s = s.replace(old, new, 1)
script_path.write_text(s, encoding="utf-8")
print("CHECKMATE v41 vote countdown patch applied")
