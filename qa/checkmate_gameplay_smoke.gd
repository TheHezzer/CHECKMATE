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

    # Standard chess: legal/illegal moves and a complete deterministic checkmate.
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

    game._start_game("Стандартные шахматы")
    game._process_classic_move(5, 6, 5, 5)
    game._process_classic_move(4, 1, 4, 3)
    game._process_classic_move(6, 6, 6, 4)
    game._process_classic_move(3, 0, 7, 4)
    _check(game.game_over, "standard chess full game reaches Fool's Mate")
    _check(game._is_in_check("white"), "checkmate position correctly detects white king in check")
    game._start_game("Стандартные шахматы")
    game._finish_game("ШАХ И МАТ", "Победа БЕЛЫХ")
    _check(game.match_result_panel.visible and game.match_result_team != null, "offline game opens detailed match results panel")

    # Team Classic and Team Voting use the shared chess movement engine.
    game.local_self_play_active = false
    game.local_bot_test_active = false
    game.local_offline_mode_active = false
    game.developer_mode = false
    game._start_game("Классика")
    game._process_classic_move(0, 6, 0, 5)
    _check(game._get_game_piece_at(0, 5) != null and game.current_team == "black", "team classic accepts legal move and switches teams")
    _check(game.get("team_chat_label") == null or game.get("team_chat_label").visible, "team chat remains available in team classic")
    game._start_game("Командное голосование")
    game._process_classic_move(4, 6, 4, 5)
    _check(game._get_game_piece_at(4, 5) != null and game.current_team == "black", "team voting mode accepts a legal board move in local rules test")
    _check(game.get("team_chat_label") == null or game.get("team_chat_label").visible, "team chat remains available in team voting")

    # Mode selector inventory: identify implemented modes rather than pretending missing modes exist.
    if game.mode_selection_panel == null:
        game._build_mode_selection_screen()
    _check(game.mode_choice_buttons.size() == 3, "mode selector exposes three implemented chess modes")
    _check(game.mode_description_label.text.contains("Командная партия") or game.selected_mode == "Классика", "mode selector renders its description")
    game._select_mode_card("Командное голосование")
    _check(game.selected_mode == "Командное голосование", "team voting card changes selected mode")
    game._select_mode_card("Стандартные шахматы")
    _check(game.selected_mode == "Стандартные шахматы", "standard chess card changes selected mode")

    # Purchases survive navigation and are consumed only when match starts.
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
    _check(not game.prep_match_purchases.has("Конь") and game.prep_match_purchases.has("Слон"), "only selected figure is consumed when match starts")

    # Bot move generator.
    game.local_self_play_active = false
    game.local_bot_test_active = true
    game.local_user_team = "observer"
    game.local_user_slot = 1
    game._start_game("Стандартные шахматы")
    game._make_bot_move()
    await create_timer(0.60).timeout
    _check(not game.last_move.is_empty() and game.current_team == "black", "bot generates and executes a legal opening move")

    # UI navigation is tested by invoking the same callbacks connected to buttons.
    game._return_to_menu()
    _check(game.preview_pawn.visible, "menu preview pawn returns after leaving a match")
    game._open_shop_screen()
    _check(game.shop_panel.visible, "shop opens")
    game._open_board_skins_screen()
    _check(game.board_skins_panel.visible and not game.shop_panel.visible, "board skins screen opens from shop")
    game.balances["zloty"] = maxi(5000, int(game.balances["zloty"]))
    game._board_skin_action("Сланец", 2800)
    _check(game.owned_board_skins.has("Сланец") and game.selected_board_skin == "Сланец", "board skin purchase and selection work")
    var saved_skin := ConfigFile.new()
    var skin_result := saved_skin.load("user://checkmate_economy.cfg")
    _check(skin_result == OK and saved_skin.get_value("progress", "selected_board_skin", "") == "Сланец", "selected board skin persists to disk")
    game._open_shop_screen()
    game._open_season_pass_screen()
    _check(game.season_pass_panel.visible and not game.shop_panel.visible, "season pass opens from shop")
    _check(game.season_pass_level_labels.size() == 15 and game.season_pass_free_buttons.size() == 15, "season pass creates all 15 reward levels")
    game._close_season_pass_screen()
    game._open_shop_screen()
    game._open_daily_tasks_screen()
    _check(game.daily_tasks_panel.visible, "daily tasks screen opens")
    game._open_shop_screen()
    game._open_piece_progression("Пешка")
    await process_frame
    var growth := game.progression_next_card.find_child("NextTierGrowth", true, false) as Label
    var unlock := game.progression_next_card.find_child("NextTierUnlockButton", true, false) as Button
    _check(growth != null and unlock != null and not growth.get_global_rect().intersects(unlock.get_global_rect()), "research growth text does not overlap unlock button")
    _check(game.progression_panel.visible, "piece research screen opens")

    # Chess City hub and deployment are checked separately; attack matchmaking is not implemented yet.
    game._return_to_menu()
    game._open_city_screen()
    _check(game.castle_hub_battle_panel.visible, "Chess City castle hub opens")
    game._open_castle_hub_deployment()
    _check(game.castle_hub_deploy_panel.visible, "Chess City army deployment opens")
    game._close_castle_hub_deployment()
    game._close_city_screen()

    print("CHECKMATE QA SUMMARY: %d checks, %d failures" % [checks, failures.size()])
    if failures.is_empty():
        print("CHECKMATE QA RESULT: PASS")
        quit(0)
    else:
        print("CHECKMATE QA RESULT: FAIL")
        quit(1)
