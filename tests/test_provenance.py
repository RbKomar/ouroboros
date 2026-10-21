from datetime import UTC, datetime

import pytest

from ouroboros.metrics import provenance
from ouroboros.model import Commit, PullRequest

T0 = datetime(2026, 10, 5, 8, 0, tzinfo=UTC)

AGENT = "Add thing\n\nAgent: claude-sonnet-5-5"
OTHER_AGENT = "Fix thing\n\nAgent: claude-opus-5-5"
NONE = "Tidy thing\n\nAgent: none"
MISSING = "Hand-written change\n\nNo trailer here"


def make_pull_request(*messages: str) -> PullRequest:
    commits = tuple(
        Commit(sha=f"{index:040d}", authored_at=T0, message=message)
        for index, message in enumerate(messages)
    )
    return PullRequest(
        number=7,
        title="Provenance",
        body=None,
        labels=(),
        created_at=T0,
        ready_at=None,
        merged_at=None,
        closed_at=None,
        additions=1,
        deletions=0,
        base_ref="main",
        commits=commits,
        check_runs=(),
    )


@pytest.mark.spec("M-PRV-01")
def test_all_commits_agent_authored_is_agent() -> None:
    # 2 of 2 commits have an Agent value other than none -> at least one agent commit -> agent
    assert provenance(make_pull_request(AGENT, OTHER_AGENT)) == "agent"


@pytest.mark.spec("M-PRV-01")
def test_all_commits_agent_none_is_human() -> None:
    # 0 agent commits, 0 unknown commits (every trailer present) -> human
    assert provenance(make_pull_request(NONE, NONE)) == "human"


@pytest.mark.spec("M-PRV-01")
def test_agent_and_none_is_agent() -> None:
    # 1 agent commit among 2 -> agent
    assert provenance(make_pull_request(NONE, AGENT)) == "agent"


@pytest.mark.spec("M-PRV-01")
def test_none_and_missing_trailer_is_unknown() -> None:
    # 0 agent commits, 1 unknown commit -> unknown
    assert provenance(make_pull_request(NONE, MISSING)) == "unknown"


@pytest.mark.spec("M-PRV-01")
def test_agent_and_missing_trailer_is_agent() -> None:
    # 1 agent commit outranks the unknown commit -> agent
    assert provenance(make_pull_request(MISSING, AGENT)) == "agent"


@pytest.mark.spec("M-PRV-01")
def test_single_commit_without_trailer_is_unknown() -> None:
    # 0 agent commits, 1 unknown commit -> unknown
    assert provenance(make_pull_request(MISSING)) == "unknown"


@pytest.mark.spec("M-PRV-01")
def test_pull_request_without_commits_is_human() -> None:
    # Literal spec: 0 agent and 0 unknown commits -> human (flagged under Spec questions)
    assert provenance(make_pull_request()) == "human"
