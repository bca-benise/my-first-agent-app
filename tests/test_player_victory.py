import unittest

from src.game_session import GameSession
from src.types import Apple, AppleType, BoardDimensions, Direction, Point, SnakeRole, SnakeState, SnakeStatus


class TestPlayerVictory(unittest.TestCase):
    def setUp(self) -> None:
        self.dimensions = BoardDimensions(width=10, height=10)

    def test_player_wins_when_all_npcs_are_eliminated(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[Point(5, 5), Point(5, 6), Point(5, 7)],
                direction=Direction.UP,
                status=SnakeStatus.ALIVE,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(1, 1)],
                direction=Direction.RIGHT,
                status=SnakeStatus.ELIMINATED,
            ),
            SnakeState(
                id="npc_2",
                role=SnakeRole.NPC,
                body=[Point(2, 2)],
                direction=Direction.LEFT,
                status=SnakeStatus.ELIMINATED,
            ),
        ]
        session.apples = []

        session.tick()

        self.assertTrue(session.is_player_winner)
        self.assertFalse(session.is_game_over)
        player = session.find_snake("player")
        self.assertTrue(player.is_alive())

    def test_player_continues_playing_after_winning(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[Point(5, 5), Point(5, 6), Point(5, 7)],
                direction=Direction.UP,
                status=SnakeStatus.ALIVE,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(1, 1)],
                direction=Direction.RIGHT,
                status=SnakeStatus.ELIMINATED,
            ),
            SnakeState(
                id="npc_2",
                role=SnakeRole.NPC,
                body=[Point(2, 2)],
                direction=Direction.LEFT,
                status=SnakeStatus.ELIMINATED,
            ),
        ]
        session.apples = [Apple(position=Point(5, 4), kind=AppleType.RED)]

        # Tick 1: Player moves onto apple
        session.tick()
        player = session.find_snake("player")

        self.assertTrue(session.is_player_winner)
        self.assertFalse(session.is_game_over)
        self.assertEqual(player.head, Point(5, 4))
        self.assertEqual(player.length, 4)

        # Tick 2: Player turns LEFT and continues moving
        session.set_player_direction(Direction.LEFT)
        session.tick()

        self.assertTrue(session.is_player_winner)
        self.assertFalse(session.is_game_over)
        self.assertEqual(player.head, Point(4, 4))

    def test_reset_clears_player_victory(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.is_player_winner = True

        session.reset()

        self.assertFalse(session.is_player_winner)


if __name__ == "__main__":
    unittest.main()
