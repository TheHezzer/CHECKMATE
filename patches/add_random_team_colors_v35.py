from pathlib import Path

p = Path(__file__).resolve().parent.parent / "scripts" / "main.gd"
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Missing anchor: " + label)
    s = s.replace(old, new, 1)

s = s.replace("    _build_first_move_vote_panel()\n", "", 1)
start = s.find("func _build_first_move_vote_panel() -> void:")
if start >= 0:
    end = s.find("func _start_game(mode_name: String) -> void:", start)
    if end < 0:
        raise SystemExit("Could not find _start_game after obsolete vote UI")
    s = s[:start] + s[end:]

rep("var team_turn_label: Label\n", "var local_player_team := \"white\"\nvar opening_player_id := \"\"\nvar team_turn_label: Label\n", "local team state")
rep("""    var team := str(payload.get("team", ""))
    if queue_status_label:""", """    var team := str(payload.get("team", ""))
    local_player_team = team if team in ["white", "black"] else "white"
    opening_player_id = str(payload.get("startingPlayerId", ""))
    if queue_status_label:""", "server team assignment")
rep("""    current_team = "white"
    active_teammate = 1
    first_move_vote_done = false
    first_move_voted = false
    first_move_votes = {"white": 0, "black": 0}
    team_next_player = {"white": 1, "black": 1}""", """    current_team = "white"
    active_teammate = randi_range(1, CLASSIC_TEAM_SIZE)
    first_move_vote_done = true
    first_move_voted = false
    first_move_votes = {"white": 0, "black": 0}
    team_next_player = {"white": (active_teammate % CLASSIC_TEAM_SIZE) + 1, "black": randi_range(1, CLASSIC_TEAM_SIZE)}""", "white always opens")
rep("""    _update_turn_highlights()
    if first_move_vote_panel:
        first_move_vote_panel.visible = true
    _remember_position()""", """    _update_turn_highlights()
    status_label.text = "Первыми ходят БЕЛЫЕ. Команда белых решает, какой ход сделать."
    _remember_position()""", "remove vote overlay at game start")
rep("""        if not first_move_vote_done:
            return
""", "", "remove move lock from obsolete vote")
p.write_text(s, encoding="utf-8")
print("CHECKMATE v35 client rules applied")
