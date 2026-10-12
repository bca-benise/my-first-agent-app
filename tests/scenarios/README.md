# Scenarios

A scenario says what good means for one behavior, in plain language, before the code exists. The person owns these files. The agent reads them and proves them with tests; it does not edit them to make a test pass.

## Format

One file per behavior, named for the behavior, for example `add_a_grade.md`:

```
# Add a grade

Given a student with no grades
When I add a grade of 92 for "Quiz 1"
Then the student's average is 92

Given a grade above 100
When I add it
Then it is refused with a message that says the allowed range
```
