CHECKMATE classic v115
======================

Full project archive: CHECKMATE_classic_v115.zip
This build is based on the user's uploaded v114 archive.

Changes:
- Random seed initialized when the game starts.
- A single helper chooses a local player's side randomly (white or black).
- Standard Chess mode rolls the side for each new match.
- Local bot matchmaking rolls the side again for each new match.
- Online matches continue to use the side assigned by the matchmaking server, so all players stay synchronized.

Validation:
- ZIP integrity check passed.
- Godot runtime / visual testing was not run in this environment.
- The archive does not contain the online server source, so server-side team assignment was not changed.
