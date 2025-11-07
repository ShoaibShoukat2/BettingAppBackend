from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class OddsRow(BaseModel):
    id: str
    sport: str
    match: str
    market: str
    bookmaker: str
    outcome: str
    odds: float
    timestamp: str

class ArbitrageRow(BaseModel):
    id: str
    sport: str
    match: str
    market: str
    outcome1: str
    bookmaker1: str
    odds1: float
    outcome2: str
    bookmaker2: str
    odds2: float
    outcome3: Optional[str] = None
    bookmaker3: Optional[str] = None
    odds3: Optional[float] = None
    arb_percentage: float
    profit_percentage: float
    timestamp: str

class Bet(BaseModel):
    bet_id: str
    session_id: str
    arbitrage_id: str
    bookmaker: str
    outcome: str
    stake: float
    odds: float
    expected_return: float
    expected_profit: float
    timestamp: str

class Session(BaseModel):
    session_id: str
    created_at: str
    total_bets: int = 0
    total_stake: float = 0.0
    total_expected_profit: float = 0.0

class BetPlacement(BaseModel):
    session_id: str
    arbitrage_id: str
    total_stake: float = Field(..., gt=0)

class SessionInit(BaseModel):
    user_name: Optional[str] = "Anonymous"

class OddsFilter(BaseModel):
    sport: Optional[str] = None
    market: Optional[str] = None

class ArbitrageFilter(BaseModel):
    min_arb: Optional[float] = 0.0
    top_n: Optional[int] = 100
    sport: Optional[str] = None