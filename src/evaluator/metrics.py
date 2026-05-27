from __future__ import annotations

import numpy as np
import pandas as pd


def annual_return(returns: pd.Series) -> float:
    return float((1 + returns).prod() ** (252 / len(returns)) - 1)


def annual_volatility(returns: pd.Series) -> float:
    return float(returns.std(ddof=0) * np.sqrt(252))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    ann_ret = annual_return(returns)
    ann_vol = annual_volatility(returns)
    if ann_vol == 0:
        return 0.0
    return float((ann_ret - risk_free_rate) / ann_vol)


def sortino_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    downside = returns[returns < 0]
    downside_vol = downside.std(ddof=0) * np.sqrt(252) if len(downside) > 0 else 0.0
    if downside_vol == 0:
        return 0.0
    return float((annual_return(returns) - risk_free_rate) / downside_vol)


def max_drawdown(returns: pd.Series) -> float:
    curve = (1 + returns).cumprod()
    dd = curve / curve.cummax() - 1
    return float(dd.min())


def calmar_ratio(returns: pd.Series) -> float:
    mdd = abs(max_drawdown(returns))
    if mdd == 0:
        return 0.0
    return float(annual_return(returns) / mdd)


def historical_var_95(returns: pd.Series) -> float:
    return float(returns.quantile(0.05))


def historical_cvar_95(returns: pd.Series) -> float:
    var_95 = historical_var_95(returns)
    tail_losses = returns[returns <= var_95]
    return float(tail_losses.mean()) if len(tail_losses) > 0 else float(var_95)
