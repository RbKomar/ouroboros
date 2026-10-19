---
name: implement-issue
description: Implement one GitHub issue end to end on its own branch, verify it, get an independent review, and open a draft pull request with an evidence pack. Use only when explicitly invoked.
disable-model-invocation: true
arguments: [issue]
---
Issue #$issue:
!`gh issue view $issue --json number,title,body,labels --jq '"# " + .title + "\n\n" + .body'`

Follow these steps in order. Do not skip any.

1. **Check readiness.** If the acceptance criteria are not testable, or the issue depends on an open issue that is
   not merged, stop and explain what is missing. Do not guess.
2. **Branch.** `git fetch origin && git switch -c agent/issue-$issue origin/main`, then use the Write tool to
   create `out/state/issue` containing `$issue` (`out/` is gitignored).
3. **Plan briefly** (in the conversation, not in a file): modules touched, tests to write, spec ids covered.
   If production code (tests excluded) will exceed ~400 changed lines, stop and propose a split instead.
4. **Tests first** for each acceptance criterion, marked with the spec id where one applies. Run them and see them fail
   for the right reason.
5. **Implement** until `scripts/verify.sh` passes. Fix causes, never weaken tests or gates.
6. **Commit** in small logical commits. Each message ends with `Agent: <your model id>`.
7. **Independent review.** Run the `spec-reviewer` subagent with the issue text. Fix every blocking item and
   re-run it until the verdict is `pass` (at most 3 rounds; after that, stop and report).
8. **Push and open a draft PR** with `git push -u origin agent/issue-$issue` and
   `gh pr create --draft --title "<issue title>" --body-file <file>` using `.github/pull_request_template.md`.
   Fill every section honestly; "What was not done" is never empty without a reason. Put `Closes #$issue` in the body.
9. Stop. A human reviews and merges.
