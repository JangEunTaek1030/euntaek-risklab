# Euntaek RiskLab

Evaluator-driven AI lab for quantitative portfolio risk control and strategy stress testing.

> Educational and research purpose only. This project is not investment advice.

## Why this project matters
Risk management workflows in finance are often opaque or overfit to prediction narratives. Euntaek RiskLab demonstrates a PM-friendly alternative: convert portfolio risk control into a deterministic, auditable evaluation loop with explicit metrics and a transparent scoring function.

## Product logic
Euntaek RiskLab frames the problem as a verifiable optimization workflow:

1. Candidate strategy generation
2. Deterministic backtest
3. Risk metric calculation
4. Evaluator scoring (explicit formula)
5. Leaderboard ranking
6. Best strategy summary

## Evaluator-driven design
The evaluator is rule-based and deterministic. Strategy quality is judged by explicit risk metrics (e.g., Sharpe, Calmar, max drawdown, CVaR, turnover) and weighted scoring—not by subjective model outputs.

## What the LLM does and does not do
- **Does**: help structure experiments, generate code scaffolding, and automate workflow orchestration.
- **Does not**: predict prices, provide trading signals, or decide strategy quality directly.

Important principles:
- This is **not** a stock prediction bot.
- This is **not** investment advice.
- LLMs do **not** decide strategy quality.
- Strategy quality is evaluated by deterministic backtests and explicit risk metrics.

## Quick start
```bash
pip install -r requirements.txt
python scripts/run_baseline.py
```

## Stage 1 outputs
- `reports/leaderboard.csv`
- `reports/best_strategy_summary.md`
- `reports/equity_curves.csv`
- `reports/drawdown_curves.csv`


## Stage 2: Agentic Strategy Evolution
Stage 2 adds a deterministic strategy-evolution loop on top of the Stage 1 evaluator. Instead of using an LLM or price predictions, the system samples candidate configurations, evaluates each one through the same backtest/risk/scoring pipeline, selects the strongest candidates, mutates their parameters, and repeats the process.

The loop is **agentic** in the product sense: it follows a structured generate -> evaluate -> select -> mutate workflow using evaluator feedback. It remains fully reproducible because the random seed, search space, scoring weights, and backtest logic are all explicit.

This system does **not** predict prices, produce trading signals, or provide investment advice. It stress tests simple portfolio-risk-control strategy configurations and ranks them with deterministic metrics.

Run Stage 2 with:
```bash
python scripts/run_evolution.py
```

Stage 2 outputs:
- `reports/evolution_leaderboard.csv` — all evaluated candidates sorted by final evaluator score
- `reports/evolution_experiment_log.csv` — round-by-round candidate details, metrics, scores, constraints, and mutation lineage
- `reports/best_evolved_strategy_summary.md` — plain-English summary of the best evolved candidate and why the evaluator selected it


## Stage 3: AI-Generated Institutional Risk Memo
Stage 3 turns the saved Stage 2 deterministic reports into an institutional-style risk memo. The LLM is used only as a report-writing assistant after the evaluator has already completed its backtests, metric calculations, constraints, and explicit score ranking.

The deterministic evaluator still decides strategy quality. The AI memo generator must use only the saved Stage 2 report artifacts as input; it does not predict prices, create trading signals, override evaluator scores, or provide investment advice.

Configure DeepSeek credentials by copying `.env.example` to `.env` and setting `DEEPSEEK_API_KEY`. Do not commit real API keys.

Run Stage 3 with:
```bash
python scripts/generate_ai_memo.py
```

Stage 3 output:
- `reports/ai_institutional_risk_memo.md` — AI-written institutional risk memo based only on deterministic Stage 2 reports

## Baseline strategies
- Equal Weight
- Momentum Rotation (monthly top-k by trailing return)
- Volatility Target (target annual vol with leverage cap)

## Roadmap
1. **Stage 1**: Deterministic risk evaluation (current)
2. **Stage 2**: Agentic strategy evolution
3. **Stage 3**: AI-generated institutional risk memo
4. **Stage 4**: Streamlit dashboard
