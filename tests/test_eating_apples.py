import random
import unittest
from unittest.mock import patch

from src.game_session import GameSession
from src.types import Apple, AppleType, BoardDimensions, Direction, Point, SnakeRole, SnakeState


class TestEatingApples(unittest.TestCase):
    def setUp(self) -> None:
        self.dimensions = BoardDimensions(width=10, height=10)

    def test_snake_eating_red_apple_grows_and_may_penalize_opponent(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[Point(5, 5), Point(5, 6), Point(5, 7)],
                direction=Direction.UP,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(2, 2), Point(2, 3), Point(2, 4), Point(2, 5)],
                direction=Direction.LEFT,
            ),
        ]
        # Red apple directly above player's head
        session.apples = [Apple(position=Point(5, 4), kind=AppleType.RED)]

        # Mock rng to ensure 50% chance triggers (random() < 0.50)
        with patch.object(session.rng, "random", return_value=0.20):
            session.tick()

        player = session.find_snake("player")
        npc = session.find_snake("npc_1")

        # Player grew by 1 segment (was 3, now 4)
        self.assertEqual(player.length, 4)
        self.assertEqual(player.head, Point(5, 4))
        # NPC lost 1 segment due to red apple penalty (was 4, now 3)
        self.assertEqual(npc.length, 3)

    def test_snake_eating_red_apple_does_not_penalize_when_probability_misses(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[Point(5, 5), Point(5, 6), Point(5, 7)],
                direction=Direction.UP,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(2, 2), Point(2, 3), Point(2, 4), Point(2, 5)],
                direction=Direction.LEFT,
            ),
        ]
        session.apples = [Apple(position=Point(5, 4), kind=AppleType.RED)]

        # Mock rng to fail the 50% chance (random() >= 0.50)
        with patch.object(session.rng, "random", return_value=0.80):
            session.tick()

        player = session.find_snake("player")
        npc = session.find_snake("npc_1")

        self.assertEqual(player.length, 4)
        self.assertEqual(npc.length, 4)

    def test_snake_eating_green_apple_grows_and_always_penalizes_opponent(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[Point(5, 5), Point(5, 6), Point(5, 7)],
                direction=Direction.UP,
            ),
            SnakeState(
                id="npc_1",
                role=SnakeRole.NPC,
                body=[Point(2, 2), Point(2, 3), Point(2, 4), Point(2, 5)],
                direction=Direction.LEFT,
            ),
        ]
        session.apples = [Apple(position=Point(5, 4), kind=AppleType.GREEN)]

        session.tick()

        player = session.find_snake("player")
        npc = session.find_snake("npc_1")

        # Player grew, NPC definitely shrank
        self.assertEqual(player.length, 4)
        self.assertEqual(npc.length, 3)

    def test_snake_eating_apple_with_no_other_living_snakes(self) -> None:
        session = GameSession(dimensions=self.dimensions)
        session.snakes = [
            SnakeState(
                id="player",
                role=SnakeRole.PLAYER,
                body=[Point(5, 5), Point(5, 6), Point(5, 7)],
                direction=Direction.UP,
            ),
        ]
        session.apples = [Apple(position=Point(5, 4), kind=AppleType.GREEN)]

        session.tick()

        player = session.find_snake("player")
        self.assertEqual(player.length, 4)


if __name__ == "__main__":
    unittest.main()
