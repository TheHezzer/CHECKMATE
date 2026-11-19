# CHECKMATE game service

HTTP service for private-room codes, quick matchmaking and persistent player accounts.

## Endpoints

- `GET /health` — health check.
- `POST /accounts/register` — create an account with `{ "username": "Knight01", "password": "your-password" }`.
- `POST /accounts/login` — sign in with username and password.
- `GET /account/me` — current account; requires `Authorization: Bearer <token>`.
- `GET /leaderboard?limit=50` — public leaderboard (up to 100 players).
- `POST /rooms` — create a six-character private room code.
- `POST /rooms/:code/join` — join a private room (two players total).
- `POST /matchmaking/queue` — enter quick-match queue by mode and rating.
- `GET /matchmaking/queue/:ticket` — poll queue status.

## Accounts and saved progress

Account data is stored in the JSON file selected by `CHECKMATE_DATA_FILE` (default: `./data/accounts.json`). The file is created automatically and written atomically. Mount a persistent disk at the data directory when deploying; ephemeral hosting filesystems can be wiped on restart or redeploy.

Set `CHECKMATE_TOKEN_SECRET` to a long random secret in the hosting provider's private environment settings. Keep it unchanged across deploys so issued 30-day bearer tokens remain valid. Never commit the secret or the account data file to GitHub.

Registration accepts usernames of 3-20 ASCII letters, numbers or underscores and passwords of 8-128 characters. Passwords are stored as salted scrypt hashes, not plaintext. Login returns a signed bearer token and public profile. The profile contains a stable server-generated player ID, rating, division, wins, losses, draws and total matches. The leaderboard exposes public profile fields only; password hashes and salts are never returned.

The account API is a first backend milestone, not a finished production identity system. There is no email/phone recovery, account deletion, social login, abuse throttling, multi-server database or client login screen yet. Protect the service with HTTPS and configure persistent storage and the token secret before inviting players.

## Rating and matchmaking

Quick matchmaking only pairs players in the same mode whose ratings are within an expanding range. The initial gap is 100 rating points; it expands by 50 points for every 15 seconds a player waits, up to 500 points. If several candidates qualify, the closest rating is selected.

New server accounts start at 1000 rating (Bronze). Divisions are Bronze (<1200), Silver (1200-1399), Gold (1400-1599), Platinum (1600-1799) and Diamond (1800+). The current API does not yet change rating or match statistics: result reporting must be tied to a trusted authoritative game server before rating changes are enabled.

## Run locally

```sh
npm test
npm start
```

## Docker

```sh
docker build -t checkmate-game-service .
docker run --rm -p 8080:8080 -v checkmate-data:/app/data -e CHECKMATE_TOKEN_SECRET="replace-with-a-long-random-secret" checkmate-game-service
```

Set `PORT` if the hosting platform supplies a different port.

## Network requirements

The matchmaking service currently returns the selected host's address and port; it does not relay game traffic. The player returned as room host must be reachable by ENet on UDP port 24567. A phone behind carrier NAT or a home router without port forwarding may not be reachable. Public matchmaking alone does not solve mobile NAT traversal; a relay or dedicated authoritative game server is still required.
