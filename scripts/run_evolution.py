from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evolution.loop import run_evolution_loop


def main() -> None:
    result = run_evolution_loop(root=ROOT)
    best = result["best"]
    report_paths = result["report_paths"]

    print("Stage 2 evolution run complete.")
    print(f"Candidates evaluated: {len(result['experiment_log'])}")
    print(f"Best candidate ID: {best['candidate_id']}")
    print(f"Best strategy family: {best['strategy_family']}")
    print(f"Best params: {best['params']}")
    print(f"Final score: {best['final_score']:.4f}")
    print("Report paths:")
    for path in report_paths.values():
        print(f"- {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
