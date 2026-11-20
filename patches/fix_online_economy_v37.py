from pathlib import Path
p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

old = '''        if action.begins_with("city_") or action.begins_with("account_"):
            if city_status_label: city_status_label.text = error_text
        else:
            if status_label and action.begins_with("game_"): status_label.text = error_text
            elif queue_status_label: queue_status_label.text = error_text'''
new = '''        if action in ["queue_start", "queue_poll"] and (response_code == 404 or (payload is Dictionary and str(payload.get("error", "")) == "NOT_ENOUGH_ZLOTY")):
            _refund_pending_match_purchase()
        if action.begins_with("city_") or action.begins_with("account_"):
            if city_status_label: city_status_label.text = error_text
        else:
            if status_label and action.begins_with("game_"): status_label.text = error_text
            elif queue_status_label: queue_status_label.text = error_text'''
if old not in s:
    raise SystemExit("Missing queue error refund anchor")
s = s.replace(old, new, 1)

old = '''        "queue_change_piece":
            online_ticket = ""
            if online_poll_timer: online_poll_timer.stop()
            online_panel.visible = false
            preparation_panel.visible = true
            _refresh_preparation_ui()'''
new = '''        "queue_change_piece":
            _refund_pending_match_purchase()
            online_ticket = ""
            if online_poll_timer: online_poll_timer.stop()
            online_panel.visible = false
            preparation_panel.visible = true
            _refresh_preparation_ui()'''
if old not in s:
    raise SystemExit("Missing queue change refund anchor")
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("CHECKMATE v37 Classic online purchase refund sync applied")
