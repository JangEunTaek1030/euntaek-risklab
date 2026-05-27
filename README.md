# Euntaek RiskLab

Evaluator-driven AI lab for quantitative portfolio risk control and strategy stress testing.

## Purpose
Euntaek RiskLab demonstrates how a complex risk management problem can be translated into a verifiable optimization workflow:

1. Candidate strategy generation
2. Deterministic backtest
3. Risk metric calculation
4. Evaluator scoring
5. Leaderboard ranking
6. Best strategy summary

> Educational and research purpose only. Not investment advice.

## Stage 1 pipeline
Run:

```bash
python scripts/run_baseline.py
```

Outputs:
- `reports/leaderboard.csv`
- `reports/best_strategy_summary.md`
- `reports/equity_curves.csv`
- `reports/drawdown_curves.csv`

## Strategy baselines
- Equal Weight
- Momentum Rotation (monthly top-k by trailing return)
- Volatility Target (target annual vol with leverage cap)
