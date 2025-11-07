# app/__init__.py
"""
Arbitrage Betting Platform - Main Application Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "FastAPI backend for arbitrage betting platform"


# app/models/__init__.py
"""
Data models and schemas for the application
"""

from .schemas import (
    OddsRow,
    ArbitrageRow,
    Bet,
    Session,
    BetPlacement,
    SessionInit,
    OddsFilter,
    ArbitrageFilter
)

__all__ = [
    "OddsRow",
    "ArbitrageRow",
    "Bet",
    "Session",
    "BetPlacement",
    "SessionInit",
    "OddsFilter",
    "ArbitrageFilter"
]


# app/routes/__init__.py
"""
API route handlers
"""

from . import odds, arbitrage, session, bets, admin

__all__ = ["odds", "arbitrage", "session", "bets", "admin"]


# app/services/__init__.py
"""
Business logic services
"""

from .odds_service import OddsService
from .arb_service import ArbitrageService
from .session_service import SessionService
from .bet_service import BetService

__all__ = [
    "OddsService",
    "ArbitrageService",
    "SessionService",
    "BetService"
]


# app/utils/__init__.py
"""
Utility functions and helpers
"""

from .csv_io import (
    safe_read_csv,
    safe_write_csv,
    append_row,
    get_csv_path
)

__all__ = [
    "safe_read_csv",
    "safe_write_csv",
    "append_row",
    "get_csv_path"
]