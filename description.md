# Snake Royale: Application Specification & Architecture Guide

This document provides the complete, self-contained technical specifications and rules required to rebuild **Snake Royale** in any programming language, game engine, or web environment.

---

## 1. Overview & High-Level Concept

**Snake Royale** is a multi-agent arcade variant of classic Snake where a human player competes on a shared grid against two autonomous NPC snakes.

Key twists:
- **Red Apples (75% spawn)**: Eating grants +1 segment length and has a **50% chance** to cause a random surviving rival snake to lose 1 tail segment.
- **Green Apples (25% spawn)**: Eating grants +3 segment length and has a **100% chance** to cause a random surviving rival snake to lose 1 tail segment.
- **Elimination via Shrinking (Down to Head)**: If a snake loses enough segments to be reduced down to only its head (length 1), it is eliminated. Its head position turns into a **Green Apple**.
- **Death Drops (Head Green, Body Red)**: When any snake crashes (into a boundary wall, into another snake's body, into its own body, or in a head-on collision), its head position turns into a **Green Apple**, and all of its remaining body segments (`body[1:]`) turn into **Red Apples**.
- **Background Play on Player Defeat**: If the player is eliminated, the surviving NPCs continue moving, hunting apples, and fighting in the background while a semi-transparent Game Over modal offers a restart option.
- **Victory with Continued Play**: When both NPC snakes are eliminated and the player is alive, a "👑 YOU WIN!" banner appears, but the player is allowed to continue playing freely until they choose to restart.
- **Complete Reset**: Requesting a restart resets the board, respawns all 3 snakes at starting lengths/positions, and begins a fresh match.

---

## 2. Board & Grid Specifications

- **Dimensions**: 24 columns by 24 rows (`width = 24`, `height = 24`).
- **Coordinate System**:
  - `(0, 0)` is the top-left cell.
  - `x` increases rightward from `0` to `width - 1`.
  - `y` increases downward from `0` to `height - 1`.
- **Boundaries**: Solid walls. Any movement outside the coordinate bounds (`x < 0`, `x >= width`, `y < 0`, or `y >= height`) is a fatal wall crash.

---

## 3. Entities & Initial State

### 3.1 Snakes
Each snake has the following state attributes:
- `id`: Unique identifier (`"player"`, `"npc_1"`, `"npc_2"`).
- `role`: `PLAYER` or `NPC`.
- `body`: Ordered list of coordinates `[Point(x, y), ...]`, where index `0` is the head and the final index is the tail.
- `direction`: Current direction of travel (`UP`, `DOWN`, `LEFT`, `RIGHT`).
- `status`: `ALIVE` or `ELIMINATED`.
- `score`: Total number of apples eaten by this snake.

#### Initial Configurations
- **Initial Length**: 4 segments per snake.
- **Player Snake**:
  - ID: `"player"`, Role: `PLAYER`
  - Body: `[(12, 16), (12, 17), (12, 18), (12, 19)]` (centered bottom)
  - Direction: `UP`
  - Color Theme: Emerald / Cyan (`#00c482` body, `#38ffc0` head)
- **NPC 1**:
  - ID: `"npc_1"`, Role: `NPC`
  - Body: `[(6, 6), (5, 6), (4, 6), (3, 6)]` (top-left)
  - Direction: `RIGHT`
  - Color Theme: Purple / Magenta (`#9b30c9` body, `#df80ff` head)
- **NPC 2**:
  - ID: `"npc_2"`, Role: `NPC`
  - Body: `[(18, 6), (19, 6), (20, 6), (21, 6)]` (top-right)
  - Direction: `LEFT`
  - Color Theme: Orange / Amber (`#e67e22` body, `#ffb84d` head)

### 3.2 Apples
Each apple has:
- `position`: `Point(x, y)`
- `kind`: `RED` or `GREEN`

Initial board setup spawns 3 apples randomly on unoccupied coordinates.

---

## 4. Tick Simulation Cycle & Rules

The game engine advances on a discrete timer tick (recommended interval: **`0.138s`** / ~7.25 Hz). Each tick follows this strict execution order:

### Step 1: Direction Updates
1. **Player**: If a direction input was received and is not the direct opposite (180° reverse) of the player's current direction, update the player's direction.
2. **NPCs**: For each surviving NPC, compute the next direction using AI pathfinding (see Section 5). An NPC will never reverse into its own neck segment.

### Step 2: Compute Intended Head Positions
For each alive snake, calculate the intended new head coordinate:
$$\text{intended\_head} = \text{head} + \text{direction.delta}$$

### Step 3: Collision Detection
Check collisions for all alive snakes simultaneously before moving any bodies:
1. **Wall Collisions**: If `not (0 <= intended_head.x < width and 0 <= intended_head.y < height)`, the snake has crashed into a wall.
2. **Body Collisions**: If `intended_head` overlaps any segment currently occupied by any living snake (including its own body), the snake has crashed.
3. **Head-on Collisions**: If two or more snakes target the exact same unoccupied cell in the same tick, all targeting snakes crash.

#### Processing Crashes:
- Every crashing snake is marked `ELIMINATED`.
- A **Green Apple** is placed at the snake's head position.
- For all remaining body segments (`body[1:]`), a **Red Apple** is placed at each segment coordinate (avoiding duplicate apples on already occupied apple cells).
- If the player snake crashed, set `is_game_over = True`.

### Step 4: Advance Surviving Snakes & Apple Consumption
For each surviving snake that did not crash:
1. Check if an apple exists at `intended_head`:
   - **If Apple Eaten**:
     - Remove the eaten apple from the board.
     - Increment snake's `score` by 1.
     - Insert `intended_head` at the front of `body` (`body[0]`).
     - **Growth**:
       - If `RED`: Do not pop the tail (length increases by +1).
       - If `GREEN`: Do not pop the tail, and append 2 duplicate coordinates at the tail (`snake.body.extend([snake.body[-1]] * 2)`), increasing total length by +3.
     - **Opponent Penalty**:
       - If `RED`: 50% probability (`random() < 0.50`).
       - If `GREEN`: 100% probability.
       - If triggered:
         - Identify all other living snakes with `length > 0`.
         - Randomly choose one target snake.
         - Remove 1 segment from the chosen snake's tail (`target.body.pop()`).
         - **Elimination Check**: If target snake is now reduced to only its head (`length <= 1`):
           - Mark target snake as `ELIMINATED`.
           - Place a **Green Apple** at `target.head`.
           - If target was the player, set `is_game_over = True`.
   - **If No Apple Eaten**:
     - Insert `intended_head` at the front of `body`.
     - Pop the last segment from `body` (length stays constant).

### Step 5: Periodic Apple Spawning
- If `tick_count % 12 == 0` or total apples on board `< 2`:
  - Find all unoccupied coordinates on the board (cells containing neither snake segments nor existing apples).
  - Pick a random unoccupied cell.
  - Determine type: 25% chance `GREEN` (`random() < 0.25`), otherwise `RED` (75%).
  - Spawn the apple.

### Step 6: Victory & Game Over State Assessment
- **Victory Condition**: If the player is alive and all NPC snakes are eliminated:
  - Set `is_player_winner = True`.
  - The game loop **continues ticking**, allowing the player to steer and eat apples.
- **Game Over Condition**: If the player is eliminated (by crash or segment loss down to head):
  - Set `is_game_over = True`.
  - Surviving NPCs continue moving and competing in the background.

---

## 5. NPC AI Pathfinding Algorithm

Each alive NPC computes its next direction on every tick using Breadth-First Search (BFS):

1. **Identify Occupied Obstacles**: Collect all body coordinates of all living snakes.
2. **Find Immediate Safe Moves**: Filter directions (`UP`, `DOWN`, `LEFT`, `RIGHT`) that:
   - Are not the exact opposite of the NPC's current direction.
   - Do not move into a wall.
   - Do not move into any occupied obstacle cell.
3. **Target Apple via BFS**:
   - If one or more safe moves exist and apples are on the board:
     - Run BFS starting from `head` exploring candidate safe moves.
     - Return the initial move direction of the shortest path to any apple.
4. **Fallback Moves**:
   - If no path to an apple is found, pick any available safe move.
   - If no safe move exists (trapped), maintain current direction.

---

## 6. Client-Server Architecture & API

For browser implementations, the application can be structured as a lightweight local backend serving a static frontend over HTTP.

### 6.1 Endpoints
- `GET /`: Serves static web client (`index.html`, `style.css`, `game.js`).
- `GET /api/state`: Returns the full JSON snapshot of the board:
  ```json
  {
    "dimensions": { "width": 24, "height": 24 },
    "snakes": [
      {
        "id": "player",
        "role": "PLAYER",
        "body": [{ "x": 12, "y": 16 }, { "x": 12, "y": 17 }],
        "direction": "UP",
        "status": "ALIVE",
        "score": 4,
        "length": 2
      }
    ],
    "apples": [
      {
        "position": { "x": 5, "y": 8 },
        "kind": "RED"
      }
    ],
    "is_game_over": false,
    "is_player_winner": true,
    "tick_count": 142
  }
  ```
- `GET /api/stream`: Server-Sent Events (SSE) stream (`text/event-stream`) pushing state updates on every tick.
- `POST /api/direction`: Accepts JSON payload `{"direction": "UP" | "DOWN" | "LEFT" | "RIGHT"}`.
- `POST /api/restart`: Resets game session to a fresh game state.

### 6.2 Frontend Features
- **Canvas Rendering**: 600x600 px canvas rendering grid cells, glowing red and green apples with highlights, distinct snake colors, and eyes on heads facing their direction of travel.
- **Scoreboard**: Cards for Player, NPC 1, and NPC 2 displaying Length, Apples Eaten, and Alive/Eliminated status badges.
- **Victory Banner**: Non-blocking banner (`👑 YOU WIN!`) shown when `is_player_winner == true` with "RESTART GAME" button and <kbd>Space</kbd>/<kbd>Enter</kbd> shortcuts, while allowing player movement keys to continue functioning.
- **Game Over Overlay**: Translucent modal shown when `is_game_over == true` displaying defeat reason, revealing live background NPC battles, and providing restart controls.
- **Controls**:
  - Steer: Arrow keys or <kbd>W</kbd>, <kbd>A</kbd>, <kbd>S</kbd>, <kbd>D</kbd>
  - Restart: <kbd>Space</kbd>, <kbd>Enter</kbd>, or <kbd>R</kbd> (when in Game Over or Victory state), or clicking restart buttons.

---

## 7. Rebuilding Checklist

When porting to another language or engine (e.g. TypeScript/React, Unity, Godot, C++):
1. [ ] Define grid dimensions (24x24) and point math (`(x + dx, y + dy)`).
2. [ ] Implement snake body as a deque or array of points.
3. [ ] Set tick timer to ~138ms (~7.25 ticks/sec).
4. [ ] Implement BFS pathfinding for NPC snakes with obstacle avoidance.
5. [ ] Implement solid wall and snake body collision checks.
6. [ ] Implement death drops: head $\rightarrow$ Green Apple, remaining body segments $\rightarrow$ Red Apples.
7. [ ] Implement apple penalties: Red = 50% chance -1 segment; Green = 100% chance -1 segment.
8. [ ] Implement apple growth: Red = +1 length; Green = +3 length.
9. [ ] Implement elimination when segment loss reduces snake to length $\le 1$.
10. [ ] Implement background NPC play when player dies.
11. [ ] Implement non-blocking victory banner when player is the last survivor.
12. [ ] Implement board reset on restart.
