# Player restart

Given a game where the player has crashed or lost all body segments
When the player loses
Then the game enters game over with a restart control available
And the surviving NPC snakes continue moving and playing in the background

Given a game where the player has lost and NPCs are playing in the background
When the player triggers a restart
Then the board and all snakes are completely reset to a fresh game
