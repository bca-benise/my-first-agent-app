from __future__ import annotations

from collections import deque
from typing import Sequence

from src.types import Apple, BoardDimensions, Direction, Point, SnakeState


class NpcNavigator:
    def __init__(self, dimensions: BoardDimensions) -> None:
        self.dimensions = dimensions

    def compute_next_direction(
        self,
        snake: SnakeState,
        apples: Sequence[Apple],
        snakes: Sequence[SnakeState],
    ) -> Direction:
        occupied: set[Point] = set()
        for other in snakes:
            if not other.is_alive():
                continue
            for segment in other.body:
                occupied.add(segment)

        head = snake.head
        safe_moves = self.find_safe_moves(snake, occupied)
        if not safe_moves:
            return snake.direction

        if not apples:
            return safe_moves[0]

        best_path_direction = self.find_direction_to_nearest_apple(
            head=head,
            safe_moves=safe_moves,
            apples=apples,
            occupied=occupied,
        )
        if best_path_direction is not None:
            return best_path_direction

        return safe_moves[0]

    def find_safe_moves(
        self,
        snake: SnakeState,
        occupied: set[Point],
    ) -> list[Direction]:
        safe: list[Direction] = []
        head = snake.head
        for candidate_direction in (
            Direction.UP,
            Direction.DOWN,
            Direction.LEFT,
            Direction.RIGHT,
        ):
            if candidate_direction.is_opposite(snake.direction):
                continue
            target = head.translate(candidate_direction)
            if self.dimensions.contains(target) and target not in occupied:
                safe.append(candidate_direction)
        return safe

    def find_direction_to_nearest_apple(
        self,
        head: Point,
        safe_moves: list[Direction],
        apples: Sequence[Apple],
        occupied: set[Point],
    ) -> Direction | None:
        target_positions = {apple.position for apple in apples}
        queue: deque[tuple[Point, Direction]] = deque()
        visited: set[Point] = {head}

        for direction in safe_moves:
            next_step = head.translate(direction)
            if next_step in target_positions:
                return direction
            visited.add(next_step)
            queue.append((next_step, direction))

        while queue:
            current_point, initial_direction = queue.popleft()
            for direction in (
                Direction.UP,
                Direction.DOWN,
                Direction.LEFT,
                Direction.RIGHT,
            ):
                neighbor = current_point.translate(direction)
                if not self.dimensions.contains(neighbor):
                    continue
                if neighbor in occupied or neighbor in visited:
                    continue
                if neighbor in target_positions:
                    return initial_direction
                visited.add(neighbor)
                queue.append((neighbor, initial_direction))

        return None
