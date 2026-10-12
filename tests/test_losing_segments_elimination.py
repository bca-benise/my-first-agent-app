import unittest

from src.game_session import GameSession
from src.types import Apple, AppleType, BoardDimensions, Direction, Point, SnakeRole, SnakeState, SnakeStatus


class TestLosingSegmentsElimination(unittest.TestCase):
    def setUp(self) -> None:
        self.dimensions = BoardDimensions(width=12, height=12)

    def test_npc_snake_with_two_segments_loses_one_and_is_eliminated(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[Point(6, 6), Point(6, 7), Point(6, 8)],
                direction=Direction.UP,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(2, 2), Point(2, 3)],
                direction=Direction.LEFT,
            ),
        ]
        npc_head_pos = Point(2, 2)
        # Player eats green apple
        session.apples = [Apple(position=Point(6, 5), kind=AppleType.GREEN)]

        session.tick()

        npc = session.find_snake("npc_1")
        self.assertEqual(npc.status, SnakeStatus.ELIMINATED)
        self.assertFalse(npc.is_alive())

        # Check green apple placed where NPC head was
        head_apple = next(
            (apple for apple in session.apples if apple.position == npc_head_pos),
            None,
        )
        self.assertIsNotNone(head_apple)
        self.assertEqual(head_apple.kind, AppleType.GREEN)

    def test_player_snake_reduced_to_head_causes_game_over_and_drops_green_apple(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        player_head_pos = Point(6, 6)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[player_head_pos, Point(6, 7)],
                direction=Direction.UP,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(2, 2), Point(2, 3), Point(2, 4)],
                direction=Direction.UP,
            ),
        ]
        # NPC eats green apple at (2, 1)
        session.apples = [Apple(position=Point(2, 1), kind=AppleType.GREEN)]

        session.tick()

        player = session.find_snake("player")
        self.assertEqual(player.status, SnakeStatus.ELIMINATED)
        self.assertTrue(session.is_game_over)

        # Check green apple placed where player head was after moving
        player_head_after_move = Point(6, 5)
        player_apple = next(
            (apple for apple in session.apples if apple.position == player_head_after_move),
            None,
        )
        self.assertIsNotNone(player_apple)
        self.assertEqual(player_apple.kind, AppleType.GREEN)


if __name__ == "__main__":
    unittest.main()
