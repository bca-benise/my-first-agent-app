---
name: write-scenarios
description: Use before building anything new, or when a request is not covered by a file in tests/scenarios. Turns what the person wants into scenarios that say what good means, before any code is written.
---

# Write scenarios first

1. Ask the person what they want and who uses it. Ask about the edges: empty input, wrong input, the largest case.
2. Write one file per behavior in `tests/scenarios/`, in the format in `tests/scenarios/README.md`.
3. Read the scenarios back to the person and get a yes before building.
4. From then on, scenarios are the person's. Do not change one to make a test pass.
