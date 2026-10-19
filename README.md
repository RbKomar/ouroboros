# ouroboros

**A delivery-metrics dashboard built by AI agents, measuring the agents that build it.**

Every pull request in this repository is written by a coding agent from a GitHub issue, checked by gates the agent
cannot change, reviewed by a second agent in a fresh context, and merged by a human. The tool this repository
produces reads the repository's own history and reports how that process is going: throughput next to
instability, split by who wrote the change.

It is an experiment in "level 3" AI-assisted delivery: agents implement from a backlog, humans own the spec,
the gates and the merge button.

## What it measures

Defined precisely in [`docs/metrics.md`](docs/metrics.md), which is the human-owned spec:

| Group | Metrics |
|---|---|
| Throughput | merged PRs per week, lead time for changes, PR size, time to merge |
| Instability | revert rate, default-branch CI failure rate, rework rate |
| Agent work | agent share, merge rate, CI rounds before merge, cost per merged PR |

Every metric is split by provenance (`agent`, `human`), taken from an `Agent:` trailer on each commit.
Nothing is measured per person, and nothing counts lines of code.

## How changes get made

```
issue (human, acceptance criteria)
  -> agent on its own branch, tests first           .claude/skills/implement-issue
  -> gates inside the session (hooks)               lint on edit, full gate before stopping,
                                                    size limit + docs coupling + trailer on commit
  -> independent reviewer agent, fresh context      .claude/agents/spec-reviewer.md
  -> draft PR with an evidence pack                 .github/pull_request_template.md
  -> the same gates again in CI                     .github/workflows/ci.yml
  -> human review and merge
```

The gates are one set of scripts used by hooks, the unattended runner and CI alike:

- `scripts/verify.sh` - ruff, mypy (strict), pytest with coverage, spec traceability, CRAP score on changed code
- `scripts/spec_trace.py` - every test that claims to verify a metric must point at an id that exists in the spec
- `scripts/crap.py` - [CRAP](https://www.artima.com/weblogs/viewpost.jsp?thread=210575) (complexity x missing coverage) per function, threshold 15
- `scripts/change-size.sh` - at most 400 changed lines per PR
- `scripts/docs-coupling.sh` - code and the docs that describe it change together (`.claude/doc-map`)
- `scripts/check-trailers.sh` - every commit declares its provenance

The agent may not edit any of these, nor `CLAUDE.md`, nor the spec (enforced by permission rules in `.claude/settings.json`).

## Running

```bash
uv sync
scripts/verify.sh
```

Unattended run for one issue (worktree, gates outside the agent, reviewer, draft PR):

```bash
scripts/l3-run.sh <issue-number> [max-budget-usd]
```

The `ouroboros` CLI itself is being built by the agents; see the open issues.

## License

MIT
