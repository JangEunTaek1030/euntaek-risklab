from __future__ import annotations

import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reporting.ai_memo import generate_ai_risk_memo

LEADERBOARD_PATH = ROOT / "reports" / "evolution_leaderboard.csv"
EXPERIMENT_LOG_PATH = ROOT / "reports" / "evolution_experiment_log.csv"
BEST_SUMMARY_PATH = ROOT / "reports" / "best_evolved_strategy_summary.md"
OUTPUT_PATH = ROOT / "reports" / "ai_institutional_risk_memo.md"


def _print_configuration_help() -> None:
    print("Stage 3 AI memo generation requires DeepSeek API configuration.")
    print("Create a .env file in the project root with:")
    print("DEEPSEEK_API_KEY=your_api_key_here")
    print("DEEPSEEK_BASE_URL=https://api.deepseek.com")
    print("DEEPSEEK_MODEL=deepseek-chat")
    print("Do not commit real API keys.")


def main() -> int:
    env_path = ROOT / ".env"
    if not env_path.exists():
        print("Missing .env file.")
        _print_configuration_help()
        return 1

    from dotenv import load_dotenv

    load_dotenv(env_path)
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Missing DEEPSEEK_API_KEY in .env.")
        _print_configuration_help()
        return 1

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    try:
        memo = generate_ai_risk_memo(
            leaderboard_path=LEADERBOARD_PATH,
            experiment_log_path=EXPERIMENT_LOG_PATH,
            best_summary_path=BEST_SUMMARY_PATH,
            api_key=api_key,
            base_url=base_url,
            model=model,
            output_path=OUTPUT_PATH,
        )
    except FileNotFoundError as exc:
        print(f"Missing deterministic Stage 2 report: {exc.filename}")
        print("Run Stage 2 first with: python scripts/run_evolution.py")
        return 1
    except Exception as exc:
        print("AI memo generation failed.")
        print(f"Reason: {exc}")
        print("Verify your DeepSeek API key, base URL, model name, and network access.")
        return 1

    print("Stage 3 AI institutional risk memo generated.")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Characters written: {len(memo)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
