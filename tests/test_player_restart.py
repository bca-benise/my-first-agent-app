import unittest

from src.game_session import GameSession
from src.types import Apple, AppleType, BoardDimensions, Direction, Point, SnakeRole, SnakeState, SnakeStatus


class TestPlayerRestart(unittest.TestCase):
    def setUp(self) -> None:
        self.dimensions = BoardDimensions(width=14, height=14)

    def test_npcs_continue_moving_in_background_after_player_dies(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        player_head = Point(0, 0)
        npc_head = Point(5, 5)

        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[player_head, Point(0, 1), Point(0, 2)],
                direction=Direction.UP,  # Will crash into wall (y = -1)
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[npc_head, Point(5, 6), Point(5, 7)],
                direction=Direction.UP,
            ),
        ]
        session.apples = [Apple(position=Point(5, 2), kind=AppleType.RED)]

        # Tick 1: player crashes, npc moves forward
        session.tick()

        player = session.find_snake("player")
        npc = session.find_snake("npc_1")

        self.assertEqual(player.status, SnakeStatus.ELIMINATED)
        self.assertTrue(session.is_game_over)
        self.assertEqual(npc.status, SnakeStatus.ALIVE)
        self.assertEqual(npc.head, Point(5, 4))

        # Tick 2: player is dead, but game ticks and NPC keeps moving towards the apple
        session.tick()
        self.assertEqual(npc.status, SnakeStatus.ALIVE)
        self.assertEqual(npc.head, Point(5, 3))

    def test_restart_resets_board_and_all_snakes_to_fresh_game(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        # Force game over
        session.is_game_over = True
        session.tick_count = 42
        for snake in session.snakes:
            snake.status = SnakeStatus.ELIMINATED

        # Player restarts
        session.reset()

        self.assertFalse(session.is_game_over)
        self.assertEqual(session.tick_count, 0)
        self.assertEqual(len(session.snakes), 3)

        player = session.find_snake("player")
        self.assertEqual(player.status, SnakeStatus.ALIVE)
        self.assertEqual(player.length, session.initial_length)

        npc1 = session.find_snake("npc_1")
        self.assertEqual(npc1.status, SnakeStatus.ALIVE)
        self.assertEqual(npc1.length, session.initial_length)

        npc2 = session.find_snake("npc_2")
        self.assertEqual(npc2.status, SnakeStatus.ALIVE)
        self.assertEqual(npc2.length, session.initial_length)


if __name__ == "__main__":
    unittest.main()
