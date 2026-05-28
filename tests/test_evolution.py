import random

import pandas as pd

from src.evolution.candidate import SUPPORTED_STRATEGY_FAMILIES, StrategyCandidate
from src.evolution.generator import generate_initial_population
from src.evolution.mutation import mutate_candidate
from src.evolution.selection import select_top_candidates

SEARCH_SPACE = {
    "momentum_rotation": {
        "lookback_days": [21, 63, 126, 252],
        "top_k": [1, 2, 3, 4, 5],
    },
    "volatility_target": {
        "target_annual_vol": [0.08, 0.10, 0.12, 0.15, 0.18],
        "max_leverage": [1.0, 1.2, 1.5, 2.0],
    },
}


def test_generator_returns_requested_population_size() -> None:
    population = generate_initial_population(SEARCH_SPACE, population_size=20, random_seed=42)

    assert len(population) == 20
    assert len({candidate.candidate_id for candidate in population}) == 20


def test_generated_candidates_have_valid_families_and_params() -> None:
    population = generate_initial_population(SEARCH_SPACE, population_size=20, random_seed=42)

    for candidate in population:
        assert candidate.strategy_family in SUPPORTED_STRATEGY_FAMILIES
        for param_name, param_value in candidate.params.items():
            assert param_value in SEARCH_SPACE[candidate.strategy_family][param_name]


def test_mutation_changes_candidate_while_keeping_valid_params() -> None:
    candidate = StrategyCandidate(
        candidate_id="cand_r00_000",
        round_id=0,
        strategy_family="momentum_rotation",
        params={"lookback_days": 63, "top_k": 3},
    )

    mutated = mutate_candidate(
        candidate=candidate,
        search_space=SEARCH_SPACE,
        mutation_rate=1.0,
        new_candidate_id="cand_r01_000",
        round_id=1,
        random_state=random.Random(7),
    )

    assert mutated.params != candidate.params
    assert mutated.parent_id == candidate.candidate_id
    assert mutated.mutation_note
    for param_name, param_value in mutated.params.items():
        assert param_value in SEARCH_SPACE[mutated.strategy_family][param_name]


def test_selection_returns_top_candidates_by_final_score() -> None:
    results = pd.DataFrame(
        [
            {"candidate_id": "low", "final_score": 0.1},
            {"candidate_id": "high", "final_score": 0.9},
            {"candidate_id": "mid", "final_score": 0.5},
        ]
    )

    selected = select_top_candidates(results, top_k=2)

    assert selected["candidate_id"].tolist() == ["high", "mid"]
