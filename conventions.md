# Conventions

## Names
- A name says what the thing is responsible for. If one phrase cannot say it, split the thing.
- Files and folders: `snake_case`. No `utils`, `helpers` or `misc`.
- Functions are named for what they do; the return type says what comes back.

## Code
- Every function has typed parameters and a typed return value.
- A fixed set of values is an `Enum` or a `Literal`, defined once in `src/types/`.
- Errors are specific exception types with a message that says what was expected.
- Comments are rare. Prefer a clearer name.

## Tests
- A test runs the real code and asserts on behavior someone would care about.
- Each scenario in `tests/scenarios/` has at least one test, named after the scenario.

## Commits and pull requests
- One branch and one pull request per change.
- Commit message: `<area>: <verb> <what>`, under 50 characters, lowercase.
- The pull request says what changed, how it was verified, and where a person should look.
