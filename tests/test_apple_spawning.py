import random
import unittest

from src.apple_spawner import AppleSpawner
from src.types import AppleType, BoardDimensions, Point


class TestAppleSpawning(unittest.TestCase):
    def setUp(self) -> None:
        self.dimensions = BoardDimensions(width=5, height=5)

    def test_spawn_appears_on_unoccupied_cell(self) -> None:
        spawner = AppleSpawner(dimensions=self.dimensions)
        occupied = {
            Point(x, y)
            for x in range(self.dimensions.width)
            for y in range(self.dimensions.height)
            if not (x == 2 and y == 2)
        }
        # Only (2, 2) is free
        apple = spawner.spawn_apple(occupied)
        self.assertIsNotNone(apple)
        self.assertEqual(apple.position, Point(2, 2))

    def test_spawner_returns_none_when_board_is_completely_full(self) -> None:
        spawner = AppleSpawner(dimensions=self.dimensions)
        occupied = {
            Point(x, y)
            for x in range(self.dimensions.width)
            for y in range(self.dimensions.height)
        }
        apple = spawner.spawn_apple(occupied)
        self.assertIsNone(apple)

    def test_twenty_five_percent_chance_of_green_apple(self) -> None:
        rng = random.Random(12345)
        spawner = AppleSpawner(dimensions=self.dimensions, green_probability=0.25, rng=rng)
        samples = 1000
        green_count = sum(
            1 for _ in range(samples) if spawner.choose_apple_type() == AppleType.GREEN
        )
        # Expected around 250 (25%), allow reasonable statistical margin [210, 290]
        self.assertGreaterEqual(green_count, 210)
        self.assertLessEqual(green_count, 290)


if __name__ == "__main__":
    unittest.main()
