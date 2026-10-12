---
name: open-pull-request
description: Use when a change on a branch is finished and needs to go to a person for review. Runs the checks, pushes the branch and opens a pull request with a description a reviewer can act on.
---

# Open a pull request

1. Confirm you are not on `main`: `git branch --show-current`. If you are, create a branch and move the work there.
2. Run `make check` (or the commands in `AGENTS.md` if `make` is missing). If anything fails, fix it or stop and report it. Do not open the pull request on a red check.
3. Commit with a message in the form `<area>: <verb> <what>`.
4. Push: `git push -u origin HEAD`.
5. Open the pull request in this repository: `gh pr create --fill --repo "$(gh repo view --json nameWithOwner -q .nameWithOwner)"`.
6. Fill every section of the template. Under "Where a person should look", name the decisions you made that the person did not ask for, and anything you could not verify.
7. Give the person the pull request link. Do not merge.
