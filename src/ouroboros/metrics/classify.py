"""Pull request provenance (M-PRV-01)."""

from typing import Literal

from ouroboros.model import Commit, PullRequest

Provenance = Literal["agent", "human", "unknown"]


def _is_agent_authored(commit: Commit) -> bool:
    return commit.agent is not None and commit.agent != "none"


def provenance(pr: PullRequest) -> Provenance:
    """Classify a pull request as ``agent``, ``human`` or ``unknown``.

    Any agent-authored commit makes the pull request ``agent``; otherwise any commit without an
    ``Agent:`` trailer makes it ``unknown``; otherwise it is ``human``.
    """
    if any(_is_agent_authored(commit) for commit in pr.commits):
        return "agent"
    if any(commit.agent is None for commit in pr.commits):
        return "unknown"
    return "human"
