# app/repositories/local.py
from __future__ import annotations

import abc

from app.models.forecast import Forecast

class ForecastRepository(abc.ABC):    
    @abc.abstractmethod
    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        city: str | None = None,
        # **filters
    ) -> list[Forecast]:
        """."""
    
    @abc.abstractmethod
    def get(self, forecast_id: int) -> Forecast | None:
        """."""
    
    @abc.abstractmethod
    def add(self, forecast: Forecast) -> Forecast:
        """."""
    
    @abc.abstractmethod
    def replace_all(self, locals: list[Forecast]) -> list[Forecast]:
        """."""
    
    @abc.abstractmethod
    def replace_by_id(self, forecast_id: int, forecast: Forecast) -> Forecast:
        """."""
    
    @abc.abstractmethod
    def delete(self) -> None:
        """."""
    
    @abc.abstractmethod
    def delete(self, forecast_id: int) -> bool:
        """."""
    
    @abc.abstractmethod
    # def update(self, forecast_id: int, data: dict) -> Forecast:
    def update(self, forecast: Forecast) -> Forecast:
        """."""
    
