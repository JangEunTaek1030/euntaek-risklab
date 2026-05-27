from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    name: str

    @abstractmethod
    def generate_weights(self, returns: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
