from __future__ import annotations

import random
from typing import Any

from src.evolution.candidate import SUPPORTED_STRATEGY_FAMILIES, StrategyCandidate

SearchSpace = dict[str, dict[str, list[Any]]]


def _sample_params(strategy_family: str, search_space: SearchSpace, random_state: random.Random) -> dict[str, Any]:
    family_space = search_space[strategy_family]
    return {param_name: random_state.choice(valid_values) for param_name, valid_values in family_space.items()}


def generate_initial_population(
    search_space: SearchSpace,
    population_size: int,
    random_seed: int,
) -> list[StrategyCandidate]:
    """Create deterministic round-0 strategy candidates from the configured search space."""
    if population_size <= 0:
        raise ValueError("population_size must be positive")

    random_state = random.Random(random_seed)
    supported_families = [family for family in SUPPORTED_STRATEGY_FAMILIES if family in search_space]
    if not supported_families:
        raise ValueError("search_space must include at least one supported strategy family")

    candidates: list[StrategyCandidate] = []
    for idx in range(population_size):
        strategy_family = random_state.choice(supported_families)
        candidates.append(
            StrategyCandidate(
                candidate_id=f"cand_r00_{idx:03d}",
                round_id=0,
                strategy_family=strategy_family,
                params=_sample_params(strategy_family, search_space, random_state),
            )
        )
    return candidates
