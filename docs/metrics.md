# Metric definitions

This file is the specification. It is owned by humans: agents read it but never edit it.
If an implementation needs a definition changed, the agent says so in its PR and a human edits this file.

Every metric has an id (`M-XXX-NN`). Tests that verify a metric are marked `@pytest.mark.spec("M-XXX-NN")`;
`scripts/spec_trace.py` fails the build when a test references an id that is not defined here.

## Ground rules

- **Unit of analysis is the change (a merged pull request), never a person.** No metric is broken down by author.
- **Speed is never shown without quality.** Every throughput view sits next to an instability view for the same period.
- **Provenance splits every metric.** Each metric is reported for `agent`, `human` and `all` (see M-PRV-01).
- Periods are ISO weeks (Monday 00:00 UTC to Sunday 23:59 UTC) unless stated otherwise.
- Only pull requests targeting the default branch count.
- Medians and p90 use the nearest-rank method. A metric with no data in a period is reported as "no data", not 0.

## Provenance

### M-PRV-01 Pull request provenance
A commit is **agent-authored** when its `Agent:` trailer value is anything other than `none`
(compared case-insensitively, after trimming whitespace). A trailer with an empty value counts as no trailer.
Trailers are read from the last paragraph of the commit message; the last `Agent:` line wins.
A pull request is `agent` when at least one of its commits is agent-authored, otherwise `human`.
A commit with no `Agent:` trailer is `unknown`; a pull request with any `unknown` commit and no agent-authored commit is `unknown`.
`unknown` pull requests are counted in `all` and reported separately as a data-quality warning.

## Throughput

### M-THR-01 Merged pull requests per week
Count of pull requests merged into the default branch in the period. Proxy for deployment frequency:
every merge to the default branch publishes the report.

### M-THR-02 Lead time for changes
For each merged pull request: time from the earliest authored timestamp among its commits to the merge timestamp.
Reported as median and p90 per period (period = week of merge), in hours.

### M-THR-03 Pull request size
For each merged pull request: additions + deletions as reported by GitHub. Median and p90 per period.

### M-THR-04 Time to merge
For each merged pull request: time from the PR leaving draft (or creation, if never a draft) to merge.
Median and p90 per period, in hours.

## Instability

### M-INS-01 Revert rate
Share of merged pull requests in the period that were later reverted. A pull request is reverted when
another merged pull request has a title starting with `Revert "` followed by its exact title,
or a body containing `Reverts <owner>/<repo>#<number>`.

### M-INS-02 Default branch CI failure rate
Share of completed CI workflow runs on pushes to the default branch in the period whose conclusion is `failure`.
Runs with conclusion `cancelled` or `skipped` are excluded from both numerator and denominator.

### M-INS-03 Rework rate
Share of merged pull requests in the period that are rework: they carry the label `rework`.
The label is applied by a human when a pull request fixes a defect introduced by an earlier merged pull request.

## Agent work

### M-AGT-01 Agent share
Share of merged pull requests in the period whose provenance is `agent`.

### M-AGT-02 Merge rate
Of the pull requests closed in the period (merged or not), the share that were merged. Per provenance.

### M-AGT-03 CI rounds before merge
For each merged pull request: number of distinct head commits of the PR that had at least one failed CI check run.
Median and p90 per period. Measures how often the agent (or human) needed CI to tell them something was wrong.

### M-AGT-04 Cost per merged pull request
For each merged agent pull request whose body contains a line `Cost-USD: <decimal>`: that value.
Median and total per period. Pull requests without the line are reported as "cost unknown" count.

## Out of scope

Lines of code written, share of code written by AI, commit counts, and anything per person.
These are easy to game and say nothing about delivery (see the research notes linked in the README).
