"""Shared agent primitives: audit records and least-privilege execution."""

from __future__ import annotations

import copy
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """What an agent's ``run()`` returns: its payload plus a human-readable rationale."""

    output: dict[str, Any]
    reasoning: str = ""


@dataclass
class AgentRun:
    """Auditable record of one agent execution."""

    agent: str
    role: str
    model: str
    suggested_model: str
    permissions: list[str]
    allowed_inputs: list[str]
    status: str
    duration_ms: float
    reasoning: str
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseAgent:
    """Base class for deterministic specialist agents.

    ``allowed_inputs`` is the least-privilege contract: ``execute()`` builds the
    agent's context by copying only these keys from the orchestrator context, so
    an agent physically cannot read data it was not granted.
    """

    name: str = "Agent"
    role: str = ""
    model: str = "deterministic-python"
    suggested_model: str = ""
    permissions: tuple[str, ...] = ()
    allowed_inputs: tuple[str, ...] = ()

    def run(self, context: dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    def _record(
        self,
        *,
        status: str,
        output: dict[str, Any],
        reasoning: str,
        duration_ms: float,
        error: str | None = None,
    ) -> AgentRun:
        return AgentRun(
            agent=self.name,
            role=self.role,
            model=self.model,
            suggested_model=self.suggested_model,
            permissions=list(self.permissions),
            allowed_inputs=list(self.allowed_inputs),
            status=status,
            duration_ms=duration_ms,
            reasoning=reasoning,
            output=output,
            error=error,
        )

    def execute(self, full_context: dict[str, Any]) -> AgentRun:
        # Deep copy so an agent cannot mutate nested structures it was granted
        # read-only access to (the scoping contract is value-level, not just key-level).
        scoped = {
            key: copy.deepcopy(full_context[key])
            for key in self.allowed_inputs
            if key in full_context
        }
        start = time.perf_counter()
        status = "success"
        error: str | None = None
        try:
            result = self.run(scoped)
            output, reasoning = result.output, result.reasoning
        except Exception as exc:  # noqa: BLE001 - surfaced in audit record
            logger.exception("%s failed", self.name)
            output = {}
            reasoning = f"Agent failed: {exc}"
            status = "error"
            error = str(exc)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return self._record(
            status=status,
            output=output,
            reasoning=reasoning,
            duration_ms=duration_ms,
            error=error,
        )

    def definition(self) -> dict[str, Any]:
        """Static agent description, used by the registry endpoint."""
        return {
            "agent": self.name,
            "role": self.role,
            "model": self.model,
            "suggested_model": self.suggested_model,
            "permissions": list(self.permissions),
            "allowed_inputs": list(self.allowed_inputs),
        }
