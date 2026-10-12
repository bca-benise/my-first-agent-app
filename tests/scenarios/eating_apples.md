# Eating apples

Given a snake eating a red apple
When the snake moves onto the red apple
Then the snake grows by 1 segment
And there is a 50% chance that another randomly chosen living snake loses 1 segment

Given a snake eating a green apple
When the snake moves onto the green apple
Then the snake grows by 3 segments
And another randomly chosen living snake loses 1 segment with 100% certainty

Given a snake eating an apple when no other living snakes exist
When the apple is eaten
Then the snake grows and no segment loss is triggered
