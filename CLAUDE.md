# Ouroboros

Delivery and agent metrics for this repository, built by agents. Read `docs/architecture.md` before changing structure
and `docs/metrics.md` (the spec) before touching anything under `src/ouroboros/metrics`.

## Commands
- Full gate (what CI runs): `scripts/verify.sh`
- Single test: `uv run pytest tests/path::test_name`
- Add a dependency: `uv add <pkg>` (runtime) or `uv add --dev <pkg>`; prefer the standard library.

## Rules that are not obvious from the code
- `docs/metrics.md` is the spec and is human-owned. Never edit it. If a definition is ambiguous or wrong,
  stop and say so in the PR under "Spec questions"; do not guess.
- Every test that verifies a metric carries `@pytest.mark.spec("M-XXX-NN")` with the id from the spec.
- Never weaken, skip or delete an existing assertion to make a test pass. If a test is wrong, explain why in the PR.
- No network in tests. Use recorded JSON in `tests/fixtures/`.
- Metrics functions are pure: no I/O, no `datetime.now()`; take "now" as a parameter.
- Do not create new markdown files. Documentation changes go into the files mapped in `.claude/doc-map`.
- Every commit message ends with the trailer `Agent: <model-id>` (or `Agent: none` for human-only work).
- One issue, one branch (`agent/issue-<n>`), one pull request, under 400 changed lines of non-test code. Bigger: propose a split.

## When compacting
Keep the issue number, the list of modified files and the last `scripts/verify.sh` result.
