# Agentic Starter

An empty repository already set up for working with a coding agent. Nothing is built yet; the structure around the code is.

## Get your own copy

```
gh repo create my-agent-app --template joeyfezster/agentic-starter --public --clone
cd my-agent-app
make install-hooks
```

Then start your agent in this folder and tell it what to build.

## What is here

| Layer | Where it lives | What it is for |
|---|---|---|
| Context | `AGENTS.md`, `src/AGENTS.md` | What the agent reads first: how to build, test and run, and the rules |
| Conventions | `conventions.md` | How things are named, structured and written here |
| Types | `src/types/` | One place for shared types, so they are not redefined |
| Skills | `.agents/skills/` | Procedures written down once, loaded when relevant |
| Owners | `CODEOWNERS` | Who must review which part |
| Commands | `Makefile` | One command each to check, test and run |
| Checks | `.githooks/`, `.github/workflows/` | The same checks before a commit and on every pull request |
| Scenarios | `tests/scenarios/` | What good means, written before the build |
| Branch rules | GitHub settings | See below; this one cannot live in a file |

## Protect main (one time, in your copy)

On GitHub: Settings, Branches, Add branch ruleset for `main`. Require a pull request before merging and require the `checks` status check to pass.
