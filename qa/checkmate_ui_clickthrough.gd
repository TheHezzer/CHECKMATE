extends SceneTree

var checks := 0
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _check(ok: bool, label: String) -> void:
    checks += 1
    if ok:
        print("UI PASS: " + label)
    else:
        failures.append(label)
        push_error("UI FAIL: " + label)

func _click(root_node: Node, fragment: String) -> bool:
    if root_node == null:
        return false
    for node in root_node.find_children("*", "Button", true, false):
        var button := node as Button
        if button != null and button.visible and not button.disabled and button.text.contains(fragment):
            button.emit_signal("pressed")
            await process_frame
            await process_frame
            return true
    return false

func _run() -> void:
    var packed := load("res://scenes/Main.tscn") as PackedScene
    if packed == null:
        _check(false, "main scene loads for real UI clickthrough")
        quit(1)
        return
    var game = packed.instantiate()
    root.add_child(game)
    await process_frame
    await process_frame

    _check(await _click(game.menu_panel, "П А Р Т И Я"), "main Party button opens mode selection")
    _check(game.mode_selection_panel.visible, "mode selection panel becomes visible")
    _check(game.mode_choice_buttons.size() == 3, "three selectable chess modes are present")
    for i in range(game.mode_choice_buttons.size()):
        var mode_button: Button = game.mode_choice_buttons[i]
        var mode_name: String = ["Классика", "Командное голосование", "Стандартные шахматы"][i]
        mode_button.emit_signal("pressed")
        await process_frame
        _check(game.selected_mode == mode_name, "mode card selects " + mode_name)

    game._select_mode_card("Классика")
    _check(await _click(game.mode_selection_panel, "НАЧАТЬ"), "classic mode Start button responds")
    _check(game.preparation_panel.visible, "classic mode opens preparation")
    _check(await _click(game.preparation_panel, "НАЗАД"), "preparation Back button responds")
    _check(game.menu_panel.visible, "preparation returns to menu")

    _check(await _click(game.menu_panel, "П А Р Т И Я"), "Party can be reopened")
    game._select_mode_card("Командное голосование")
    _check(await _click(game.mode_selection_panel, "НАЧАТЬ"), "team voting Start button responds")
    _check(game.preparation_panel.visible, "team voting opens preparation")
    _check(await _click(game.preparation_panel, "НАЗАД"), "team voting preparation Back responds")

    _check(await _click(game.menu_panel, "П А Р Т И Я"), "Party opens for standard mode")
    game._select_mode_card("Стандартные шахматы")
    _check(await _click(game.mode_selection_panel, "НАЧАТЬ"), "standard chess Start button responds")
    _check(game.game_panel.visible and game.standard_chess_mode_active, "standard chess enters a live match")
    if game.local_user_team == "black":
        await create_timer(2.0).timeout
        _check(not game.last_move.is_empty(), "standard chess bot opens when player is black")
    else:
        _check(game.current_team == "white", "standard chess waits for the human white opening")
        game._process_classic_move(4, 6, 4, 4)
        await create_timer(2.0).timeout
        _check(not game.last_move.is_empty() and game.current_team == "white", "standard chess bot replies after the human opening")
    _check(await _click(game.game_panel, "В МЕНЮ"), "live match Back to menu button responds")
    _check(game.menu_panel.visible, "live match returns to main menu")

    _check(await _click(game.menu_panel, "Магазин"), "bottom Shop navigation button responds")
    _check(game.shop_panel.visible, "shop opens from main menu")
    _check(await _click(game.shop_panel, "ВЫБРАТЬ ДОСКУ"), "shop board skins action responds")
    _check(game.board_skins_panel.visible, "board skins catalogue opens")
    _check(await _click(game.board_skins_panel, "В МАГАЗИН"), "board skins Back button responds")
    _check(game.shop_panel.visible, "board skins returns to shop")

    _check(await _click(game.shop_panel, "ЗАДАНИЯ И СУНДУК"), "daily tasks shop action responds")
    _check(game.daily_tasks_panel.visible, "daily tasks screen opens")
    _check(await _click(game.daily_tasks_panel, "БОНУС ЗА ВХОД"), "login streak button responds")
    _check(game.login_streak_panel.visible, "login streak screen opens")
    _check(await _click(game.login_streak_panel, "К ЗАДАНИЯМ"), "login streak Back button responds")
    _check(game.daily_tasks_panel.visible, "login streak returns to daily tasks")
    _check(await _click(game.daily_tasks_panel, "В МАГАЗИН"), "daily tasks Back button responds")
    _check(game.shop_panel.visible, "daily tasks returns to shop")

    _check(await _click(game.shop_panel, "ОТКРЫТЬ ПРОПУСК"), "season pass shop action responds")
    _check(game.season_pass_panel.visible, "season pass screen opens")
    _check(await _click(game.season_pass_panel, "В МАГАЗИН"), "season pass Back button responds")
    _check(game.shop_panel.visible, "season pass returns to shop")

    _check(await _click(game.shop_panel, "ВЫБРАТЬ ПАКЕТ"), "Gambit packages shop action responds")
    _check(game.gambit_packs_panel.visible, "Gambit packages screen opens")
    _check(await _click(game.gambit_packs_panel, "В МАГАЗИН"), "Gambit packages Back button responds")
    _check(game.shop_panel.visible, "Gambit packages returns to shop")
    _check(await _click(game.shop_panel, "НАЗАД"), "Shop Back button responds")
    _check(game.menu_panel.visible, "shop returns to main menu")

    _check(await _click(game.menu_panel, "Шахматный город"), "Chess City bottom navigation button responds")
    _check(game.castle_hub_battle_panel.visible, "Chess City castle hub opens from main menu")
    _check(await _click(game.castle_hub_battle_panel, "ЗАМОК I"), "castle opens army deployment")
    _check(game.castle_hub_deploy_panel.visible, "army deployment panel opens")
    _check(game.castle_hub_piece_buttons.has("Пешка"), "deployment has pawn selector")
    game.castle_hub_piece_buttons["Пешка"].emit_signal("pressed")
    await process_frame
    if game.castle_hub_board_cells.size() > 0:
        game.castle_hub_board_cells[48].emit_signal("pressed")
    await process_frame
    _check(not game.castle_hub_army.is_empty(), "deployment cell click places a figure")
    _check(await _click(game.castle_hub_deploy_panel, "К ЗАМКУ"), "deployment Back button responds")
    _check(game.castle_hub_battle_panel.visible, "deployment returns to castle hub")
    _check(await _click(game.castle_hub_battle_panel, "НАПАСТЬ"), "castle Attack button responds")
    _check(game.city_offline_active and game.city_offline_battle_panel.visible, "Attack opens offline battle")
    _check(await _click(game.city_offline_battle_panel, "ВЫЙТИ"), "offline battle Back button responds")
    _check(game.castle_hub_battle_panel.visible, "offline battle returns to castle hub")
    _check(await _click(game.castle_hub_battle_panel, "НАЗАД"), "castle hub Back button responds")
    _check(game.menu_panel.visible, "castle hub returns to main menu")

    _check(await _click(game.menu_panel, "ВОЙТИ"), "account Login button responds")
    _check(game.account_panel.visible, "account panel opens")
    _check(await _click(game.account_panel, "ГОСТЬ"), "guest/offline account option responds")
    _check(game.menu_panel.visible, "guest login returns to main menu")

    print("CHECKMATE UI CLICKTHROUGH SUMMARY: %d checks, %d failures" % [checks, failures.size()])
    if failures.is_empty():
        print("CHECKMATE UI CLICKTHROUGH RESULT: PASS")
        quit(0)
    else:
        print("CHECKMATE UI CLICKTHROUGH RESULT: FAIL")
        quit(1)
