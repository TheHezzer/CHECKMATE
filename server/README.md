# CHECKMATE matchmaking service

A small HTTP matchmaking and private-room directory for the CHECKMATE Godot prototype.

## Endpoints

- `GET /health` — health check.
- `POST /rooms` — create a six-character private room code.
- `POST /rooms/:code/join` — join a private room (two players total).
- `POST /matchmaking/queue` — enter the quick-match queue by mode.
- `GET /matchmaking/queue/:ticket` — poll queue status.

The service stores rooms and queue tickets in memory. Restarting the service clears them. Expiry is 15 minutes for rooms and 2 minutes for unmatched queue tickets.

## Run locally

```sh
npm test
npm start
```

## Docker

```sh
docker build -t checkmate-matchmaking .
docker run --rm -p 8080:8080 checkmate-matchmaking
```

Set `PORT` if the hosting platform supplies a different port.

## Network requirements

The matchmaking service does not relay game traffic. The player returned as the room host must be reachable by ENet on UDP port 24567. For public matches, deploy the game host on a server with a public address and open UDP port, or add a relay/dedicated game-server layer. A phone behind carrier NAT or a home router without port forwarding may not be reachable.

This service is a prototype: no accounts, persistent database, authentication, anti-abuse protection, rating-range matching, or encrypted player identity is implemented yet. Do not use it as a production service until those are added.
