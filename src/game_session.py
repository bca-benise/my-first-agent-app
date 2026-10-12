from __future__ import annotations

import random
from typing import Sequence

from src.apple_spawner import AppleSpawner
from src.npc_navigator import NpcNavigator
from src.types import (
    Apple,
    AppleType,
    BoardDimensions,
    Direction,
    GameSnapshot,
    InvalidDirectionError,
    Point,
    SnakeNotFoundError,
    SnakeRole,
    SnakeStatus,
    SnakeState,
)


class GameSession:
    def __init__(
        self,
        dimensions: BoardDimensions = BoardDimensions(width=24, height=24),
        rng: random.Random | None = None,
        apple_spawn_interval: int = 12,
        initial_length: int = 4,
    ) -> None:
        self.dimensions = dimensions
        self.rng = rng or random.Random()
        self.apple_spawn_interval = apple_spawn_interval
        self.initial_length = initial_length
        self.apple_spawner = AppleSpawner(dimensions=dimensions, rng=self.rng)
        self.npc_navigator = NpcNavigator(dimensions=dimensions)
        self.snakes: list[SnakeState] = []
        self.apples: list[Apple] = []
        self.is_game_over: bool = False
        self.tick_count: int = 0
        self.pending_player_direction: Direction | None = None
        self.reset()

    def reset(self) -> None:
        self.tick_count = 0
        self.is_game_over = False
        self.pending_player_direction = None
        self.snakes = self.build_initial_snakes()
        self.apples = []
        for _ in range(3):
            self.spawn_periodic_apple()

    def build_initial_snakes(self) -> list[SnakeState]:
        center_x = self.dimensions.width // 2
        center_y = self.dimensions.height // 2

        player_head_y = min(self.dimensions.height - 4, center_y + 4)
        player_body = [
            Point(center_x, player_head_y + i)
            for i in range(self.initial_length)
        ]
        player = SnakeState(
            id="player",
            role=SnakeRole.PLAYER,
            body=player_body,
            direction=Direction.UP,
        )

        npc1_x = max(2, self.dimensions.width // 4)
        npc1_y = max(3, self.dimensions.height // 4)
        npc1_body = [
            Point(npc1_x - i, npc1_y)
            for i in range(self.initial_length)
        ]
        npc1 = SnakeState(
            id="npc_1",
            role=SnakeRole.NPC,
            body=npc1_body,
            direction=Direction.RIGHT,
        )

        npc2_x = min(self.dimensions.width - 3, (self.dimensions.width * 3) // 4)
        npc2_y = max(3, self.dimensions.height // 4)
        npc2_body = [
            Point(npc2_x + i, npc2_y)
            for i in range(self.initial_length)
        ]
        npc2 = SnakeState(
            id="npc_2",
            role=SnakeRole.NPC,
            body=npc2_body,
            direction=Direction.LEFT,
        )

        return [player, npc1, npc2]

    def set_player_direction(self, direction: Direction) -> None:
        player = self.find_snake("player")
        if not player.is_alive():
            return
        if not direction.is_opposite(player.direction):
            self.pending_player_direction = direction

    def find_snake(self, snake_id: str) -> SnakeState:
        for snake in self.snakes:
            if snake.id == snake_id:
                return snake
        raise SnakeNotFoundError(snake_id)

    def get_occupied_positions(self) -> set[Point]:
        occupied: set[Point] = {apple.position for apple in self.apples}
        for snake in self.snakes:
            if snake.is_alive():
                occupied.update(snake.body)
        return occupied

    def spawn_periodic_apple(self) -> Apple | None:
        occupied = self.get_occupied_positions()
        new_apple = self.apple_spawner.spawn_apple(occupied)
        if new_apple is not None:
            self.apples.append(new_apple)
        return new_apple

    def add_green_apple_at(self, position: Point) -> None:
        # If an apple is already there, replace it with a green apple
        self.apples = [apple for apple in self.apples if apple.position != position]
        self.apples.append(self.apple_spawner.spawn_head_green_apple(position))

    def add_red_apple_at(self, position: Point) -> None:
        # Avoid duplicating an apple if one already exists at this position
        if not any(apple.position == position for apple in self.apples):
            self.apples.append(self.apple_spawner.spawn_body_red_apple(position))

    def trigger_apple_penalty(self, eating_snake: SnakeState, apple: Apple) -> None:
        should_trigger = False
        if apple.kind == AppleType.GREEN:
            should_trigger = True
        elif apple.kind == AppleType.RED:
            should_trigger = self.rng.random() < 0.50

        if not should_trigger:
            return

        eligible_targets = [
            snake
            for snake in self.snakes
            if snake.is_alive() and snake.id != eating_snake.id and snake.length > 0
        ]
        if not eligible_targets:
            return

        target_snake = self.rng.choice(eligible_targets)
        self.reduce_snake_segment(target_snake)

    def reduce_snake_segment(self, snake: SnakeState) -> None:
        if not snake.is_alive():
            return

        # Lose 1 segment from the tail
        if len(snake.body) > 0:
            snake.body.pop()

        # If reduced down to only head (length 1), snake is eliminated
        if len(snake.body) <= 1:
            head_pos = snake.head
            snake.status = SnakeStatus.ELIMINATED
            self.add_green_apple_at(head_pos)
            if snake.role == SnakeRole.PLAYER:
                self.is_game_over = True

    def eliminate_snake_by_crash(self, snake: SnakeState, head_position: Point) -> None:
        snake.status = SnakeStatus.ELIMINATED
        self.add_green_apple_at(head_position)
        for segment in snake.body[1:]:
            self.add_red_apple_at(segment)
        if snake.role == SnakeRole.PLAYER:
            self.is_game_over = True

    def tick(self) -> None:
        self.tick_count += 1

        # 1. Update directions
        for snake in self.snakes:
            if not snake.is_alive():
                continue
            if snake.role == SnakeRole.PLAYER:
                if self.pending_player_direction is not None:
                    if not self.pending_player_direction.is_opposite(snake.direction):
                        snake.direction = self.pending_player_direction
                    self.pending_player_direction = None
            else:
                snake.direction = self.npc_navigator.compute_next_direction(
                    snake=snake,
                    apples=self.apples,
                    snakes=self.snakes,
                )

        # 2. Compute intended next head positions
        intended_heads: dict[str, Point] = {}
        for snake in self.snakes:
            if snake.is_alive():
                intended_heads[snake.id] = snake.head.translate(snake.direction)

        # 3. Detect collisions
        crashed_ids: set[str] = set()

        # Wall collisions
        for snake in self.snakes:
            if not snake.is_alive():
                continue
            target = intended_heads[snake.id]
            if not self.dimensions.contains(target):
                crashed_ids.add(snake.id)

        # Body collisions against existing alive bodies
        # Note: In classic snake, moving into any snake's body segment causes a crash.
        occupied_bodies: set[Point] = set()
        for snake in self.snakes:
            if snake.is_alive():
                occupied_bodies.update(snake.body)

        for snake in self.snakes:
            if not snake.is_alive() or snake.id in crashed_ids:
                continue
            target = intended_heads[snake.id]
            # Colliding with own body or another snake's body
            if target in occupied_bodies:
                crashed_ids.add(snake.id)

        # Head-on collisions (two snakes targeting the exact same unoccupied cell)
        target_counts: dict[Point, list[str]] = {}
        for snake_id, target in intended_heads.items():
            if snake_id not in crashed_ids:
                target_counts.setdefault(target, []).append(snake_id)

        for target, snake_ids in target_counts.items():
            if len(snake_ids) > 1:
                for snake_id in snake_ids:
                    crashed_ids.add(snake_id)

        # Process crashes
        for snake in self.snakes:
            if snake.id in crashed_ids and snake.is_alive():
                # Head position turns into a green apple
                self.eliminate_snake_by_crash(snake, snake.head)

        # 4. Advance surviving snakes and check for apples
        for snake in self.snakes:
            if not snake.is_alive() or snake.id in crashed_ids:
                continue

            new_head = intended_heads[snake.id]
            eaten_apple: Apple | None = None
            for apple in self.apples:
                if apple.position == new_head:
                    eaten_apple = apple
                    break

            if eaten_apple is not None:
                self.apples = [a for a in self.apples if a.position != eaten_apple.position]
                snake.body.insert(0, new_head)
                if eaten_apple.kind == AppleType.GREEN:
                    snake.body.extend([snake.body[-1]] * 2)
                snake.score += 1
                self.trigger_apple_penalty(snake, eaten_apple)
            else:
                snake.body.insert(0, new_head)
                snake.body.pop()

        # 5. Periodic apple spawning
        if self.tick_count % self.apple_spawn_interval == 0 or len(self.apples) < 2:
            self.spawn_periodic_apple()

    def snapshot(self) -> GameSnapshot:
        return GameSnapshot(
            dimensions=self.dimensions,
            snakes=[
                SnakeState(
                    id=s.id,
                    role=s.role,
                    body=list(s.body),
                    direction=s.direction,
                    status=s.status,
                    score=s.score,
                )
                for s in self.snakes
            ],
            apples=list(self.apples),
            is_game_over=self.is_game_over,
            tick_count=self.tick_count,
        )
