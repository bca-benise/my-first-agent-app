from __future__ import annotations

import json
import mimetypes
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from src.game_session import GameSession
from src.types import Direction, GameSnapshot, InvalidDirectionError

STATIC_DIRECTORY: Path = Path(__file__).resolve().parent / "static"


def serialize_snapshot(snapshot: GameSnapshot) -> dict[str, Any]:
    return {
        "dimensions": {
            "width": snapshot.dimensions.width,
            "height": snapshot.dimensions.height,
        },
        "snakes": [
            {
                "id": snake.id,
                "role": snake.role.value,
                "body": [{"x": p.x, "y": p.y} for p in snake.body],
                "direction": snake.direction.name,
                "status": snake.status.value,
                "score": snake.score,
                "length": snake.length,
            }
            for snake in snapshot.snakes
        ],
        "apples": [
            {
                "position": {"x": apple.position.x, "y": apple.position.y},
                "kind": apple.kind.value,
            }
            for apple in snapshot.apples
        ],
        "is_game_over": snapshot.is_game_over,
        "is_player_winner": snapshot.is_player_winner,
        "tick_count": snapshot.tick_count,
    }


class GameServerState:
    def __init__(self, session: GameSession, tick_interval_seconds: float = 0.138) -> None:
        self.session = session
        self.tick_interval_seconds = tick_interval_seconds
        self.lock = threading.Lock()
        self.running = True
        self.ticker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.ticker_thread.start()

    def _run_loop(self) -> None:
        while self.running:
            time.sleep(self.tick_interval_seconds)
            with self.lock:
                self.session.tick()

    def stop(self) -> None:
        self.running = False

    def get_snapshot(self) -> GameSnapshot:
        with self.lock:
            return self.session.snapshot()

    def set_player_direction(self, direction_name: str) -> None:
        try:
            direction = Direction[direction_name.upper()]
        except KeyError as err:
            raise InvalidDirectionError(direction_name) from err

        with self.lock:
            self.session.set_player_direction(direction)

    def restart_game(self) -> None:
        with self.lock:
            self.session.reset()


def create_request_handler(state: GameServerState) -> type[BaseHTTPRequestHandler]:
    class SnakeRequestHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            # Suppress default stdout log spam
            pass

        def do_GET(self) -> None:
            path = self.path.split("?")[0]

            if path == "/api/state":
                snapshot = state.get_snapshot()
                data = json.dumps(serialize_snapshot(snapshot)).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            if path == "/api/stream":
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                try:
                    while state.running:
                        snapshot = state.get_snapshot()
                        payload = f"data: {json.dumps(serialize_snapshot(snapshot))}\n\n"
                        self.wfile.write(payload.encode("utf-8"))
                        self.wfile.flush()
                        time.sleep(state.tick_interval_seconds)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return

            # Serve static files
            if path == "/" or path == "":
                filename = "index.html"
            else:
                filename = path.lstrip("/")

            target_file = (STATIC_DIRECTORY / filename).resolve()
            if not target_file.is_relative_to(STATIC_DIRECTORY) or not target_file.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return

            mime_type, _ = mimetypes.guess_type(target_file)
            content_type = mime_type or "application/octet-stream"
            content = target_file.read_bytes()

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_POST(self) -> None:
            path = self.path.split("?")[0]

            if path == "/api/direction":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                try:
                    payload = json.loads(body)
                    direction_str = payload.get("direction", "")
                    state.set_player_direction(direction_str)
                    self.send_response(HTTPStatus.NO_CONTENT)
                    self.end_headers()
                except (json.JSONDecodeError, InvalidDirectionError):
                    self.send_error(HTTPStatus.BAD_REQUEST, "Invalid direction payload")
                return

            if path == "/api/restart":
                state.restart_game()
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
                return

            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    return SnakeRequestHandler


def create_snake_server(
    session: GameSession | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> tuple[ThreadingHTTPServer, GameServerState]:
    game_session = session or GameSession()
    server_state = GameServerState(game_session)
    handler_class = create_request_handler(server_state)
    httpd = ThreadingHTTPServer((host, port), handler_class)
    return httpd, server_state
