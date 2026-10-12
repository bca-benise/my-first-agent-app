import unittest

from src.game_session import GameSession
from src.types import AppleType, BoardDimensions, Direction, Point, SnakeRole, SnakeState, SnakeStatus


class TestCollisions(unittest.TestCase):
    def setUp(self) -> None:
        self.dimensions = BoardDimensions(width=8, height=8)

    def test_snake_crashes_into_wall_leaves_green_apple(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        player_head = Point(0, 0)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[player_head, Point(0, 1), Point(0, 2)],
                direction=Direction.UP,
            )
        ]
        session.apples = []

        session.tick()

        player = session.find_snake("player")
        self.assertEqual(player.status, SnakeStatus.ELIMINATED)
        self.assertTrue(session.is_game_over)

        apple = next((a for a in session.apples if a.position == player_head), None)
        self.assertIsNotNone(apple)
        self.assertEqual(apple.kind, AppleType.GREEN)

    def test_snake_crashes_into_another_snakes_body_leaves_green_apple(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        player_head = Point(3, 4)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[player_head, Point(2, 4), Point(1, 4)],
                direction=Direction.RIGHT,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(4, 4), Point(4, 5), Point(4, 6)],
                direction=Direction.UP,
            ),
        ]
        session.apples = []

        # player moves RIGHT into Point(4, 4) which is part of npc_1's body
        session.tick()

        player = session.find_snake("player")
        self.assertEqual(player.status, SnakeStatus.ELIMINATED)

        apple = next((a for a in session.apples if a.position == player_head), None)
        self.assertIsNotNone(apple)
        self.assertEqual(apple.kind, AppleType.GREEN)

    def test_snake_crashes_into_own_body_leaves_green_apple(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        # Snake in loop: head at (2, 2) facing DOWN into its own body at (2, 3)
        head_pos = Point(2, 2)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[
                    head_pos,
                    Point(3, 2),
                    Point(3, 3),
                    Point(2, 3),
                    Point(1, 3),
                ],
                direction=Direction.DOWN,
            )
        ]
        session.apples = []

        session.tick()

        player = session.find_snake("player")
        self.assertEqual(player.status, SnakeStatus.ELIMINATED)
        self.assertTrue(session.is_game_over)

        apple = next((a for a in session.apples if a.position == head_pos), None)
        self.assertIsNotNone(apple)
        self.assertEqual(apple.kind, AppleType.GREEN)


if __name__ == "__main__":
    unittest.main()
