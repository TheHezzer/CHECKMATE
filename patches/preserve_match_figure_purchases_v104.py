from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old: str, new: str, label: str) -> None:
    global s
    if old not in s:
        raise SystemExit("Missing v104 anchor: " + label)
    s = s.replace(old, new, 1)

# Pending figure purchases are an inventory until a match actually starts.
rep('''        piece_progression = cfg.get_value("progress", "piece_progression", piece_progression)
''', '''        piece_progression = cfg.get_value("progress", "piece_progression", piece_progression)
        prep_match_purchases = cfg.get_value("progress", "prep_match_purchases", prep_match_purchases)
''', "load prepared figure purchases")
rep('''    cfg.set_value("progress", "piece_progression", piece_progression)
''', '''    cfg.set_value("progress", "piece_progression", piece_progression)
    cfg.set_value("progress", "prep_match_purchases", prep_match_purchases)
''', "save prepared figure purchases")

# Leaving the preparation screen is navigation, not a cancellation or refund.
rep('''func _close_preparation() -> void:
    _refund_pending_match_purchase()
    preparation_panel.visible = false
    menu_panel.visible = true
''', '''func _close_preparation() -> void:
    preparation_panel.visible = false
    menu_panel.visible = true
    _save_economy()
''', "keep purchases when leaving preparation")

# Do not refund other selected inventory items or clear them when queuing.
rep('''    # Only the selected figure is consumed by this match. Return any other
    # options bought while browsing the preparation screen.
    for bought_piece in prep_match_purchases.keys():
        if str(bought_piece) != selected_name:
            balances["zloty"] = int(balances["zloty"]) + int(prep_match_purchases[bought_piece])
    var selected_cost := int(prep_match_purchases[selected_name])
    prep_match_purchases.clear()
    pending_match_purchase = true
''', '''    # Keep the whole purchased inventory until a match really starts.
    # Only the selected figure is consumed by that match.
    var selected_cost := int(prep_match_purchases[selected_name])
    pending_match_purchase = true
''', "preserve unselected purchased figures")

# Cancelling matchmaking must not erase a figure already paid for.
start = s.find("func _refund_pending_match_purchase() -> void:")
end = s.find("\nfunc _load_economy() -> void:", start)
if start < 0 or end < 0:
    raise SystemExit("Missing v104 refund function range")
s = s[:start] + '''func _refund_pending_match_purchase() -> void:
    # A purchased figure remains in the player's inventory until an actual
    # match starts. Cancelling or leaving the queue only clears the reservation.
    pending_match_purchase = false
    pending_match_purchase_cost = 0
    pending_match_purchase_piece = ""
    _save_economy()

''' + s[end:]

# Consume the reserved figure only when the game scene is genuinely started.
rep('''func _start_game(mode_name: String) -> void:
    game_over = false
''', '''func _start_game(mode_name: String) -> void:
    if pending_match_purchase:
        prep_match_purchases.erase(pending_match_purchase_piece)
        pending_match_purchase = false
        pending_match_purchase_cost = 0
        pending_match_purchase_piece = ""
        _save_economy()
    game_over = false
''', "consume selected figure on actual match start")


# The menu's SubViewport preview must never sit over the live chessboard.
rep('''    menu_panel.visible = false
    if online_panel:
        online_panel.visible = false
    game_panel.visible = true
''', '''    menu_panel.visible = false
    if preview_container:
        preview_container.visible = false
    if online_panel:
        online_panel.visible = false
    game_panel.visible = true
''', "hide menu figure preview during a match")
rep('''    menu_panel.visible = true
    local_bot_test_active = false
''', '''    menu_panel.visible = true
    if preview_container:
        preview_container.visible = true
    local_bot_test_active = false
''', "restore menu figure preview after a match")

p.write_text(s, encoding="utf-8")
print("CHECKMATE v104: purchased match figures now persist across menus/restarts and are consumed only when a match starts.")
