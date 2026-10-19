"""Typed snapshot of a repository and its stable JSON form.

Every timestamp is a timezone-aware UTC ``datetime``. Optional fields are ``None`` when absent.
The JSON form has sorted keys and ISO-8601 timestamps, so the same data is always the same bytes.
"""

import json
import re
import types
import typing
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

_AGENT_TRAILER = re.compile(r"^agent:[ \t]*(.*?)[ \t]*$", re.IGNORECASE)


def _require_utc(owner: str, name: str, value: datetime) -> None:
    offset = value.utcoffset()
    if offset is None:
        raise ValueError(f"{owner}.{name} must be timezone-aware, got naive {value!r}")
    if offset != timedelta(0):
        raise ValueError(f"{owner}.{name} must be UTC, got offset {offset}")


def _validate_timestamps(instance: object) -> None:
    owner = type(instance).__name__
    for field in fields(instance):  # type: ignore[arg-type]
        value = getattr(instance, field.name)
        if isinstance(value, datetime):
            _require_utc(owner, field.name, value)


def _encode(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_encode(item) for item in value]
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _encode(getattr(value, field.name)) for field in fields(value)}
    return value


def _decode(hint: Any, value: Any) -> Any:
    if value is None:
        return None
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin in (types.UnionType, typing.Union):
        return _decode(next(arg for arg in args if arg is not type(None)), value)
    if origin is tuple:
        return tuple(_decode(args[0], item) for item in value)
    if hint is datetime:
        parsed = datetime.fromisoformat(value)
        _require_utc("json", "timestamp", parsed)
        return parsed.astimezone(UTC)
    if isinstance(hint, type) and is_dataclass(hint):
        hints = typing.get_type_hints(hint)
        names = [field.name for field in fields(hint)]
        factory: Any = hint
        return factory(**{name: _decode(hints[name], value[name]) for name in names})
    return value


@dataclass(frozen=True)
class Commit:
    sha: str
    authored_at: datetime
    message: str

    def __post_init__(self) -> None:
        _validate_timestamps(self)

    @property
    def agent(self) -> str | None:
        """Value of the ``Agent:`` trailer in the last paragraph of the message, else ``None``.

        Follows git conventions: trailers live in the last paragraph, which must not be the
        subject paragraph; keys are case-insensitive; the last occurrence wins.
        """
        paragraphs = re.split(r"\n[ \t]*\n", self.message.replace("\r\n", "\n").strip())
        if len(paragraphs) < 2:
            return None
        value = None
        for line in paragraphs[-1].split("\n"):
            match = _AGENT_TRAILER.match(line)
            if match:
                value = match.group(1)
        return value


@dataclass(frozen=True)
class CheckRun:
    head_sha: str
    conclusion: str | None
    completed_at: datetime | None

    def __post_init__(self) -> None:
        _validate_timestamps(self)


@dataclass(frozen=True)
class PullRequest:
    number: int
    title: str
    body: str | None
    labels: tuple[str, ...]
    created_at: datetime
    ready_at: datetime | None
    merged_at: datetime | None
    closed_at: datetime | None
    additions: int
    deletions: int
    base_ref: str
    commits: tuple[Commit, ...]
    check_runs: tuple[CheckRun, ...]

    def __post_init__(self) -> None:
        _validate_timestamps(self)


@dataclass(frozen=True)
class WorkflowRun:
    head_sha: str
    event: str
    branch: str
    conclusion: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        _validate_timestamps(self)


@dataclass(frozen=True)
class Snapshot:
    repo: str
    default_branch: str
    collected_at: datetime
    pull_requests: tuple[PullRequest, ...]
    workflow_runs: tuple[WorkflowRun, ...]

    def __post_init__(self) -> None:
        _validate_timestamps(self)

    def to_json(self) -> str:
        return json.dumps(_encode(self), sort_keys=True, indent=2, ensure_ascii=False) + "\n"

    @classmethod
    def from_json(cls, text: str) -> "Snapshot":
        return _decode(cls, json.loads(text))  # type: ignore[no-any-return]
