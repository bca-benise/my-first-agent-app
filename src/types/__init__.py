"""Shared types for the whole application. Define each type once, here."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def delta(self) -> Point:
        return Point(self.value[0], self.value[1])

    def is_opposite(self, other: Direction) -> bool:
        return self.value[0] == -other.value[0] and self.value[1] == -other.value[1]


class Point(NamedTuple):
    x: int
    y: int

    def translate(self, direction: Direction) -> Point:
        return Point(self.x + direction.delta.x, self.y + direction.delta.y)


class AppleType(Enum):
    RED = "RED"
    GREEN = "GREEN"


class Apple(NamedTuple):
    position: Point
    kind: AppleType


class SnakeRole(Enum):
    PLAYER = "PLAYER"
    NPC = "NPC"


class SnakeStatus(Enum):
    ALIVE = "ALIVE"
    ELIMINATED = "ELIMINATED"


@dataclass
class SnakeState:
    id: str
    role: SnakeRole
    body: list[Point]
    direction: Direction
    status: SnakeStatus = SnakeStatus.ALIVE
    score: int = 0

    @property
    def head(self) -> Point:
        return self.body[0]

    @property
    def length(self) -> int:
        return len(self.body)

    def is_alive(self) -> bool:
        return self.status == SnakeStatus.ALIVE


class BoardDimensions(NamedTuple):
    width: int
    height: int

    def contains(self, point: Point) -> bool:
        return 0 <= point.x < self.width and 0 <= point.y < self.height


@dataclass
class GameSnapshot:
    dimensions: BoardDimensions
    snakes: list[SnakeState]
    apples: list[Apple]
    is_game_over: bool
    tick_count: int


class InvalidDirectionError(Exception):
    def __init__(self, direction_name: str) -> None:
        super().__init__(f"Expected a valid direction name, got: {direction_name}")


class SnakeNotFoundError(Exception):
    def __init__(self, snake_id: str) -> None:
        super().__init__(f"Expected existing snake id, got: {snake_id}")
