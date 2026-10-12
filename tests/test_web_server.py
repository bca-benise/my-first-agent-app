import json
import threading
import unittest
from http.client import HTTPConnection

from src.game_session import GameSession
from src.types import Direction
from src.web_server import create_snake_server


class TestWebServer(unittest.TestCase):
    def setUp(self) -> None:
        self.session = GameSession()
        self.server, self.state = create_snake_server(session=self.session, host="127.0.0.1", port=0)
        self.port = self.server.server_address[1]
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

    def tearDown(self) -> None:
        self.state.stop()
        self.server.shutdown()
        self.server.server_close()

    def test_get_api_state(self) -> None:
        conn = HTTPConnection("127.0.0.1", self.port)
        conn.request("GET", "/api/state")
        res = conn.getresponse()
        self.assertEqual(res.status, 200)
        data = json.loads(res.read().decode("utf-8"))
        self.assertIn("dimensions", data)
        self.assertIn("snakes", data)
        self.assertIn("apples", data)
        self.assertEqual(len(data["snakes"]), 3)
        conn.close()

    def test_post_api_direction(self) -> None:
        conn = HTTPConnection("127.0.0.1", self.port)
        body = json.dumps({"direction": "LEFT"})
        conn.request("POST", "/api/direction", body=body, headers={"Content-Type": "application/json"})
        res = conn.getresponse()
        self.assertEqual(res.status, 204)
        conn.close()

        self.assertEqual(self.session.pending_player_direction, Direction.LEFT)

    def test_post_api_restart(self) -> None:
        self.session.is_game_over = True
        conn = HTTPConnection("127.0.0.1", self.port)
        conn.request("POST", "/api/restart")
        res = conn.getresponse()
        self.assertEqual(res.status, 204)
        conn.close()

        self.assertFalse(self.session.is_game_over)

    def test_serve_index_html(self) -> None:
        conn = HTTPConnection("127.0.0.1", self.port)
        conn.request("GET", "/")
        res = conn.getresponse()
        self.assertEqual(res.status, 200)
        content = res.read().decode("utf-8")
        self.assertIn("SNAKE ROYALE", content)
        conn.close()


if __name__ == "__main__":
    unittest.main()
