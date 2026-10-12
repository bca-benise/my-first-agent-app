# Collisions

Given a snake moving towards the board boundary
When the snake moves into a wall
Then the snake crashes and is eliminated
And a green apple appears at its last valid board position

Given a snake moving towards another snake's body
When the snake moves into the segment of another snake
Then the colliding snake crashes and is eliminated
And a green apple appears at the position where its head was

Given a snake moving towards its own body
When the snake moves into its own segment
Then the snake crashes and is eliminated
And a green apple appears at the position where its head was
