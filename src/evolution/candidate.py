from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SUPPORTED_STRATEGY_FAMILIES = ("momentum_rotation", "volatility_target")


@dataclass(frozen=True)
class StrategyCandidate:
    candidate_id: str
    round_id: int
    strategy_family: str
    params: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None
    mutation_note: str | None = None

    def __post_init__(self) -> None:
        if self.strategy_family not in SUPPORTED_STRATEGY_FAMILIES:
            raise ValueError(f"Unsupported strategy family: {self.strategy_family}")
