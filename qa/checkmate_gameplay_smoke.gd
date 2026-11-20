extends SceneTree

var failures: Array[String] = []
var checks := 0

func _initialize() -> void:
    call_deferred("_run")

func _check(condition: bool, message: String) -> void:
    checks += 1
    if not condition:
        failures.append(message)
        push_error("QA FAIL: " + message)
    else:
        print("QA PASS: " + message)

func _run() -> void:
    var packed := load("res://scenes/Main.tscn") as PackedScene
    if packed == null:
        _check(false, "main scene loads")
        quit(1)
        return
    var game = packed.instantiate()
    root.add_child(game)
    await process_frame
    await process_frame
    _check(game.game_piece_nodes.size() == 32, "initial chessboard has 32 pieces")

    # Legal movement and illegal movement.
    game.local_self_play_active = true
    game._start_game("Стандартные шахматы")
    _check(not game.preview_pawn.visible, "menu preview pawn is hidden during a live match")
    var menu_button: Button = null
    for node in game.game_panel.find_children("*", "Button", true, false):
        if node is Button and str(node.text).contains("МЕНЮ"):
            menu_button = node
            break
    _check(menu_button != null and game._is_game_ui_control_hit(menu_button.get_global_rect().get_center()), "menu button is protected from board click handling")
    game._process_classic_move(4, 6, 4, 4)
    _check(game._get_game_piece_at(4, 4) != null and game.current_team == "black", "white pawn e2-e4 moves and passes turn")
    var previous_move: Dictionary = game.last_move.duplicate(true)
    game._process_classic_move(4, 1, 4, 4)
    _check(game._get_game_piece_at(4, 1) != null and game.last_move == previous_move, "illegal three-square pawn move is rejected")
    game._process_classic_move(4, 1, 4, 3)
    _check(game._get_game_piece_at(4, 3) != null and game.current_team == "white", "black pawn e7-e5 moves and passes turn")
    game._process_classic_move(6, 7, 5, 5)
    _check(game._get_game_piece_at(5, 5) != null and game.current_team == "black", "white knight g1-f3 moves legally")

    # Full deterministic self-play game ending in checkmate (Fool's Mate).
    game._start_game("Стандартные шахматы")
    game._process_classic_move(5, 6, 5, 5)
    game._process_classic_move(4, 1, 4, 3)
    game._process_classic_move(6, 6, 6, 4)
    game._process_classic_move(3, 0, 7, 4)
    _check(game.game_over, "self-play completes a full game by checkmate")
    _check(game._is_in_check("white"), "checkmate position correctly detects white king in check")

    # Team classic turn transition.
    game.local_self_play_active = false
    game.local_bot_test_active = false
    game.local_offline_mode_active = false
    game.developer_mode = false
    game._start_game("Классика")
    game._process_classic_move(0, 6, 0, 5)
    _check(game._get_game_piece_at(0, 5) != null and game.current_team == "black", "team classic mode accepts a legal move and switches teams")

    # Purchased pieces must survive navigation and app-style config reload.
    game.prep_match_purchases = {"Конь": 30, "Слон": 35}
    game._save_economy()
    game._close_preparation()
    _check(game.prep_match_purchases.has("Конь") and game.prep_match_purchases.has("Слон"), "leaving preparation keeps purchased figures")
    var cfg := ConfigFile.new()
    var load_result := cfg.load("user://checkmate_economy.cfg")
    var saved: Dictionary = cfg.get_value("progress", "prep_match_purchases", {}) if load_result == OK else {}
    _check(saved.has("Конь") and saved.has("Слон"), "purchased figures are persisted to disk")
    game.pending_match_purchase = true
    game.pending_match_purchase_piece = "Конь"
    game.pending_match_purchase_cost = 30
    game._start_game("Классика")
    _check(not game.prep_match_purchases.has("Конь") and game.prep_match_purchases.has("Слон"), "only the selected figure is consumed when a match starts")

    # Exercise the actual bot move generator and move executor.
    game.local_self_play_active = false
    game.local_bot_test_active = true
    game.local_user_team = "observer"
    game.local_user_slot = 99
    game._start_game("Стандартные шахматы")
    game.local_user_slot = 1
    game._make_bot_move()
    await create_timer(0.60).timeout
    _check(not game.last_move.is_empty() and game.current_team == "black", "bot generates and executes a legal opening move")

    game._return_to_menu()
    _check(game.preview_pawn.visible, "menu preview pawn returns after leaving a match")
    game._open_piece_progression("Пешка")
    await process_frame
    var growth := game.progression_next_card.find_child("NextTierGrowth", true, false) as Label
    var unlock := game.progression_next_card.find_child("NextTierUnlockButton", true, false) as Button
    _check(growth != null and unlock != null and not growth.get_global_rect().intersects(unlock.get_global_rect()), "research growth text does not overlap the unlock button")

    print("CHECKMATE QA SUMMARY: %d checks, %d failures" % [checks, failures.size()])
    if failures.is_empty():
        print("CHECKMATE QA RESULT: PASS")
        quit(0)
    else:
        print("CHECKMATE QA RESULT: FAIL")
        quit(1)
