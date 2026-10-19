import json
from datetime import UTC, datetime, timedelta, timezone

import pytest

from ouroboros.model import CheckRun, Commit, PullRequest, Snapshot, WorkflowRun

T0 = datetime(2026, 10, 5, 8, 0, tzinfo=UTC)
T1 = datetime(2026, 10, 5, 9, 30, 15, tzinfo=UTC)
T2 = datetime(2026, 10, 6, 12, 0, tzinfo=UTC)


def make_commit(message: str = "Add thing\n\nAgent: claude-sonnet-5-5") -> Commit:
    return Commit(sha="a" * 40, authored_at=T0, message=message)


def make_pull_request(**overrides: object) -> PullRequest:
    fields: dict[str, object] = {
        "number": 7,
        "title": "Snapshot model",
        "body": "Closes #1",
        "labels": ("agent", "model"),
        "created_at": T0,
        "ready_at": T1,
        "merged_at": T2,
        "closed_at": T2,
        "additions": 120,
        "deletions": 4,
        "base_ref": "main",
        "commits": (make_commit(),),
        "check_runs": (CheckRun(head_sha="a" * 40, conclusion="success", completed_at=T1),),
    }
    fields.update(overrides)
    return PullRequest(**fields)  # type: ignore[arg-type]


def make_snapshot() -> Snapshot:
    open_pr = make_pull_request(
        number=8,
        body=None,
        labels=(),
        ready_at=None,
        merged_at=None,
        closed_at=None,
        commits=(),
        check_runs=(CheckRun(head_sha="b" * 40, conclusion=None, completed_at=None),),
    )
    return Snapshot(
        repo="rbkomar/ouroboros",
        default_branch="main",
        collected_at=T2,
        pull_requests=(make_pull_request(), open_pr),
        workflow_runs=(
            WorkflowRun(
                head_sha="a" * 40,
                event="push",
                branch="main",
                conclusion="failure",
                created_at=T1,
            ),
            WorkflowRun(
                head_sha="b" * 40, event="push", branch="main", conclusion=None, created_at=T2
            ),
        ),
    )


def test_snapshot_round_trips_exactly() -> None:
    snapshot = make_snapshot()

    assert Snapshot.from_json(snapshot.to_json()) == snapshot


def test_round_trip_preserves_absent_optionals_as_none() -> None:
    restored = Snapshot.from_json(make_snapshot().to_json())

    open_pr = restored.pull_requests[1]
    assert open_pr.body is None
    assert open_pr.ready_at is None
    assert open_pr.merged_at is None
    assert open_pr.closed_at is None
    assert open_pr.check_runs[0].conclusion is None
    assert open_pr.check_runs[0].completed_at is None
    assert restored.workflow_runs[1].conclusion is None


def test_empty_snapshot_round_trips() -> None:
    snapshot = Snapshot(
        repo="a/b", default_branch="main", collected_at=T0, pull_requests=(), workflow_runs=()
    )

    assert Snapshot.from_json(snapshot.to_json()) == snapshot


def test_same_data_produces_byte_identical_json() -> None:
    first = make_snapshot().to_json()
    second = Snapshot.from_json(first).to_json()

    assert first == second
    assert first == make_snapshot().to_json()


def test_json_has_sorted_keys_at_every_level() -> None:
    def assert_sorted(node: object) -> None:
        if isinstance(node, dict):
            assert list(node) == sorted(node)
            for value in node.values():
                assert_sorted(value)
        elif isinstance(node, list):
            for item in node:
                assert_sorted(item)

    assert_sorted(json.loads(make_snapshot().to_json()))


def test_json_timestamps_are_iso_8601_utc() -> None:
    data = json.loads(make_snapshot().to_json())

    assert data["collected_at"] == "2026-10-06T12:00:00+00:00"
    assert data["pull_requests"][0]["created_at"] == "2026-10-05T08:00:00+00:00"
    assert data["pull_requests"][0]["ready_at"] == "2026-10-05T09:30:15+00:00"
    assert data["pull_requests"][1]["ready_at"] is None


def test_from_json_returns_timezone_aware_utc_datetimes() -> None:
    restored = Snapshot.from_json(make_snapshot().to_json())

    assert restored.collected_at.utcoffset() == timedelta(0)
    assert restored.pull_requests[0].commits[0].authored_at.utcoffset() == timedelta(0)


def test_from_json_accepts_z_suffix() -> None:
    data = json.loads(make_snapshot().to_json())
    data["collected_at"] = "2026-10-06T12:00:00Z"

    assert Snapshot.from_json(json.dumps(data)).collected_at == T2


def test_models_are_frozen() -> None:
    commit = make_commit()

    with pytest.raises(AttributeError):
        commit.message = "other"  # type: ignore[misc]


@pytest.mark.parametrize(
    "build",
    [
        lambda naive: Commit(sha="a", authored_at=naive, message="m"),
        lambda naive: CheckRun(head_sha="a", conclusion="success", completed_at=naive),
        lambda naive: make_pull_request(created_at=naive),
        lambda naive: make_pull_request(merged_at=naive),
        lambda naive: WorkflowRun(
            head_sha="a", event="push", branch="main", conclusion=None, created_at=naive
        ),
        lambda naive: Snapshot(
            repo="a/b",
            default_branch="main",
            collected_at=naive,
            pull_requests=(),
            workflow_runs=(),
        ),
    ],
)
def test_naive_datetime_is_rejected(build: object) -> None:
    naive = datetime(2026, 10, 5, 8, 0)

    with pytest.raises(ValueError, match="timezone-aware"):
        build(naive)  # type: ignore[operator]


def test_non_utc_datetime_is_rejected() -> None:
    warsaw = datetime(2026, 10, 5, 10, 0, tzinfo=timezone(timedelta(hours=2)))

    with pytest.raises(ValueError, match="UTC"):
        Commit(sha="a", authored_at=warsaw, message="m")


def test_from_json_rejects_naive_timestamp() -> None:
    data = json.loads(make_snapshot().to_json())
    data["collected_at"] = "2026-10-06T12:00:00"

    with pytest.raises(ValueError, match="timezone-aware"):
        Snapshot.from_json(json.dumps(data))


def test_agent_trailer_is_read_from_last_paragraph() -> None:
    commit = make_commit("Add thing\n\nBody text.\n\nAgent: claude-sonnet-5-5\n")

    assert commit.agent == "claude-sonnet-5-5"


def test_agent_trailer_among_other_trailers() -> None:
    commit = make_commit(
        "Add thing\n\nSigned-off-by: A <a@example.com>\nAgent: claude-opus-5-5\n"
        "Co-Authored-By: B <b@example.com>"
    )

    assert commit.agent == "claude-opus-5-5"


def test_agent_none_trailer_is_returned_as_value() -> None:
    assert make_commit("Hand written\n\nAgent: none").agent == "none"


def test_message_without_trailer_has_no_agent() -> None:
    assert make_commit("Just a subject").agent is None
    assert make_commit("Subject\n\nBody without trailers.").agent is None
    assert make_commit("").agent is None


def test_agent_line_outside_last_paragraph_is_ignored() -> None:
    commit = make_commit("Subject\n\nAgent: claude-sonnet-5-5\n\nClosing remarks, no trailer.")

    assert commit.agent is None


def test_agent_line_in_subject_is_not_a_trailer() -> None:
    assert make_commit("Agent: claude-sonnet-5-5").agent is None


def test_last_agent_trailer_wins() -> None:
    commit = make_commit("Subject\n\nAgent: first\nAgent: second")

    assert commit.agent == "second"


def test_trailer_key_is_case_insensitive_and_value_is_trimmed() -> None:
    assert make_commit("Subject\n\nagent:   claude-haiku-5-5  ").agent == "claude-haiku-5-5"


def test_trailer_with_crlf_line_endings() -> None:
    assert make_commit("Subject\r\n\r\nAgent: claude-sonnet-5-5\r\n").agent == "claude-sonnet-5-5"
