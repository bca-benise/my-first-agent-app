# Losing segments and elimination

Given a snake with 2 segments (head and 1 body segment)
When the snake loses 1 segment from an opponent's apple penalty
Then the snake is reduced to only its head (length 1)
And the snake is eliminated

Given an NPC snake that is eliminated by losing all body segments
When the elimination occurs
Then the NPC snake is removed from play
And a green apple appears at the position where its head was

Given a player snake that is reduced to only its head
When the elimination occurs
Then the player loses the game
And a green apple appears at the position where the player's head was
