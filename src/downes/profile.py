"""Agent profile — who this agent is, loaded from a clear ``agent.yaml``.

The shared spine reads one YAML file to set the agent's identity, focus,
disposition, and priorities, then injects a persona block into every system
prompt. Swap ``agent.yaml`` to turn the same harness into a different agent
(Downes = education; Lia Fáil = time management and office coordination).

See ``agent.example.yaml`` for the documented template. Resolution order:

1. ``$AGENT_PROFILE`` if set,
2. ``agent.yaml`` in the current working directory,
3. ``agent.yaml`` at the repo root (two levels above this package).

If none is found, sensible defaults are used so the agent still runs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class AgentProfile:
    name: str = "Agent"
    pronouns: str = "they/them"
    role: str = "an assistant"
    focus: str = "general assistance"
    mission: str = ""
    priorities: List[str] = field(default_factory=list)
    tone: str = "clear and concise"
    traits: List[str] = field(default_factory=list)
    scope_note: str = ""

    def traits_str(self) -> str:
        return ", ".join(self.traits)

    def persona_block(self) -> str:
        """The shared identity preamble injected into every system prompt."""
        lines = [
            f"You are {self.name} ({self.pronouns}), {self.role}.",
            f"You focus on {self.focus}.",
        ]
        if self.mission:
            lines += ["", self.mission.strip()]
        if self.priorities:
            lines += ["", "Your priorities:"]
            lines += [f"- {p}" for p in self.priorities]
        disposition = self.tone.strip()
        if self.traits:
            joined = self.traits_str()
            disposition = f"{disposition}. You are {joined}" if disposition else f"You are {joined}"
        if disposition:
            lines += ["", f"Disposition: {disposition}."]
        return "\n".join(lines)

    def default_system_prompt(self) -> str:
        """The base system prompt: persona + agent-agnostic operating rules."""
        return "\n".join(
            [
                self.persona_block(),
                "",
                "Read each request carefully, identify what must be done and for whom, "
                "and produce a clear, ready-to-use result. If a needed detail is missing, "
                "say so plainly rather than guessing. Be methodical and concise.",
                "You never invent facts, names, dates, numbers, or commitments.",
            ]
        )

    def fill(self, text: str) -> str:
        """Substitute profile tokens, leaving other braces (e.g. ``{tools}``) intact."""
        return (
            text.replace("{name}", self.name)
            .replace("{role}", self.role)
            .replace("{focus}", self.focus)
            .replace("{pronouns}", self.pronouns)
            .replace("{scope_note}", self.scope_note)
        )


def _profile_path() -> Optional[Path]:
    env = os.getenv("AGENT_PROFILE")
    if env:
        return Path(env)
    candidates = [
        Path.cwd() / "agent.yaml",
        Path(__file__).resolve().parent.parent.parent / "agent.yaml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def load_profile() -> AgentProfile:
    """Load the agent profile from YAML, falling back to defaults if absent/invalid."""
    path = _profile_path()
    if not path or not path.is_file():
        return AgentProfile()
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except Exception:
        return AgentProfile()
    if not isinstance(data, dict):
        return AgentProfile()

    disposition = data.get("disposition") or {}
    if not isinstance(disposition, dict):
        disposition = {}

    defaults = AgentProfile()
    return AgentProfile(
        name=data.get("name", defaults.name),
        pronouns=data.get("pronouns", defaults.pronouns),
        role=data.get("role", defaults.role),
        focus=data.get("focus", defaults.focus),
        mission=(data.get("mission") or "").strip(),
        priorities=list(data.get("priorities") or []),
        tone=(disposition.get("tone") or defaults.tone),
        traits=list(disposition.get("traits") or []),
        scope_note=(data.get("scope_note") or "").strip(),
    )
