"""Entry point: `python -m src` runs the application."""

from __future__ import annotations

import socket
import sys
import webbrowser

from src.web_server import create_snake_server


def find_available_port(host: str = "127.0.0.1", preferred_port: int = 8000) -> int:
    for port in range(preferred_port, preferred_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) != 0:
                return port
    return preferred_port


def main() -> None:
    # When executed non-interactively without --serve (e.g. by starter entrypoint tests),
    # exit cleanly with status message.
    if not sys.stdin.isatty() and "--serve" not in sys.argv:
        print("Snake application entry point ready. Run in an interactive terminal or with --serve to play.")
        return

    port = find_available_port()
    server, state = create_snake_server(port=port)
    url = f"http://127.0.0.1:{port}"
    print(f"Snake Royale running at {url}")
    print("Opening browser. Press Ctrl+C to stop.")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        state.stop()
        server.server_close()


if __name__ == "__main__":
    main()
