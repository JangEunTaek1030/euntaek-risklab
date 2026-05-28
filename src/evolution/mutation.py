from __future__ import annotations

import random
from typing import Any

from src.evolution.candidate import StrategyCandidate
from src.evolution.generator import SearchSpace


def _choose_different_value(valid_values: list[Any], current_value: Any, random_state: random.Random) -> Any:
    alternatives = [value for value in valid_values if value != current_value]
    if not alternatives:
        return current_value
    return random_state.choice(alternatives)


def mutate_candidate(
    candidate: StrategyCandidate,
    search_space: SearchSpace,
    mutation_rate: float,
    new_candidate_id: str,
    round_id: int,
    random_state: random.Random,
) -> StrategyCandidate:
    """Mutate one candidate while keeping it inside the deterministic search space."""
    if candidate.strategy_family not in search_space:
        raise ValueError(f"Missing search space for {candidate.strategy_family}")
    if not 0 <= mutation_rate <= 1:
        raise ValueError("mutation_rate must be between 0 and 1")

    family_space = search_space[candidate.strategy_family]
    mutated_params = dict(candidate.params)
    changed_params: list[str] = []

    for param_name, valid_values in family_space.items():
        if random_state.random() < mutation_rate:
            new_value = _choose_different_value(valid_values, mutated_params[param_name], random_state)
            if new_value != mutated_params[param_name]:
                mutated_params[param_name] = new_value
                changed_params.append(param_name)

    if not changed_params:
        param_name = random_state.choice(list(family_space.keys()))
        new_value = _choose_different_value(family_space[param_name], mutated_params[param_name], random_state)
        if new_value != mutated_params[param_name]:
            mutated_params[param_name] = new_value
            changed_params.append(param_name)

    if changed_params:
        note_parts = [f"{name}: {candidate.params[name]} -> {mutated_params[name]}" for name in changed_params]
        mutation_note = "; ".join(note_parts)
    else:
        mutation_note = "No available alternative parameter values; candidate copied unchanged."

    return StrategyCandidate(
        candidate_id=new_candidate_id,
        round_id=round_id,
        strategy_family=candidate.strategy_family,
        params=mutated_params,
        parent_id=candidate.candidate_id,
        mutation_note=mutation_note,
    )
