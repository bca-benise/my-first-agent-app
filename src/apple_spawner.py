from __future__ import annotations

import random
from typing import Sequence

from src.types import Apple, AppleType, BoardDimensions, Point


class AppleSpawner:
    def __init__(
        self,
        dimensions: BoardDimensions,
        green_probability: float = 0.25,
        rng: random.Random | None = None,
    ) -> None:
        self.dimensions = dimensions
        self.green_probability = green_probability
        self.rng = rng or random.Random()

    def choose_apple_type(self) -> AppleType:
        if self.rng.random() < self.green_probability:
            return AppleType.GREEN
        return AppleType.RED

    def find_unoccupied_positions(
        self,
        occupied_positions: set[Point],
    ) -> list[Point]:
        available: list[Point] = []
        for x in range(self.dimensions.width):
            for y in range(self.dimensions.height):
                candidate = Point(x, y)
                if candidate not in occupied_positions:
                    available.append(candidate)
        return available

    def spawn_apple(
        self,
        occupied_positions: set[Point],
        forced_kind: AppleType | None = None,
    ) -> Apple | None:
        available = self.find_unoccupied_positions(occupied_positions)
        if not available:
            return None
        position = self.rng.choice(available)
        kind = forced_kind if forced_kind is not None else self.choose_apple_type()
        return Apple(position=position, kind=kind)

    def spawn_head_green_apple(self, head_position: Point) -> Apple:
        return Apple(position=head_position, kind=AppleType.GREEN)
