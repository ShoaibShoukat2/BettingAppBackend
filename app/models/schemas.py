from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

# Enums for better type safety
class OpportunityType(str, Enum):
    ARBITRAGE = "arbitrage"
    MIDDLE = "middle"
    EV = "ev"
    LOW = "low"

class OpportunityStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REMOVED = "removed"

# Core Data Models
class Event(BaseModel):
    """Represents a sporting event"""
    event_id: str
    sport: str
    home_team: str
    away_team: str
    event_time: Optional[str] = None
    status: str = "upcoming"  # upcoming, live, completed

class Market(BaseModel):
    """Represents a betting market for an event"""
    market_id: str
    event_id: str
    market_type: str  # Match Winner, Spread, Total, etc.
    market_params: Optional[str] = None  # e.g., "Over/Under 2.5", "Spread -3.5"

class Outcome(BaseModel):
    """Represents a single outcome in a market"""
    outcome_id: str
    market_id: str
    outcome_name: str  # Home, Away, Over, Under, etc.
    
class OddsRow(BaseModel):
    """Enhanced odds row with proper entity linking"""
    odds_id: str
    event_id: str
    sport: str
    match: str
    market: str
    market_params: Optional[str] = None
    bookmaker: str
    outcome: str
    odds: float
    timestamp: str
    is_active: bool = True

# Opportunity Models
class ArbitrageOpportunity(BaseModel):
    id: str
    type: str = "arbitrage"
    event_id: str
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
    roi: float  # Return on Investment %
    status: str = "active"
    timestamp: str
    expires_at: Optional[str] = None

class MiddleOpportunity(BaseModel):
    """Middle betting opportunity - overlapping line ranges"""
    id: str
    type: str = "middle"
    event_id: str
    sport: str
    match: str
    market: str  # Usually spread or total
    line1: float  # First line (e.g., +3.5)
    bookmaker1: str
    odds1: float
    line2: float  # Second line (e.g., -2.5)
    bookmaker2: str
    odds2: float
    middle_range: str  # e.g., "3 to 3.5"
    win_both_scenarios: str  # Description of middle outcomes
    max_profit_percentage: float
    worst_case_loss_percentage: float
    roi: float
    status: str = "active"
    timestamp: str
    expires_at: Optional[str] = None

class EVOpportunity(BaseModel):
    """Expected Value (Positive EV) opportunity"""
    id: str
    type: str = "ev"
    event_id: str
    sport: str
    match: str
    market: str
    outcome: str
    bookmaker: str
    offered_odds: float
    fair_odds: float  # Calculated from consensus/market average
    fair_probability: float
    implied_probability: float
    expected_value: float  # EV in percentage
    edge_percentage: float  # Advantage over fair line
    roi: float
    recommended_stake: Optional[float] = None  # Kelly criterion stake
    status: str = "active"
    timestamp: str
    expires_at: Optional[str] = None

class LowHoldOpportunity(BaseModel):
    """Low-hold market opportunity (low vig/juice)"""
    id: str
    type: str = "low"
    event_id: str
    sport: str
    match: str
    market: str
    bookmaker: str
    outcomes: dict  # {outcome: odds}
    total_implied_probability: float  # Should be close to 100%
    hold_percentage: float  # Bookmaker's margin (vig)
    true_probability_estimates: dict  # Adjusted probabilities
    roi: float  # Potential advantage
    status: str = "active"
    timestamp: str
    expires_at: Optional[str] = None

# Unified Opportunity Response
class Opportunity(BaseModel):
    """Generic opportunity wrapper"""
    id: str
    type: OpportunityType
    sport: str
    match: str
    roi: float
    profit_percentage: Optional[float] = None
    status: OpportunityStatus
    timestamp: str
    details: dict  # Full opportunity data

# Bet Models
class Bet(BaseModel):
    bet_id: str
    session_id: str
    opportunity_id: str
    opportunity_type: str
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

# Request Models
class BetPlacement(BaseModel):
    session_id: str
    opportunity_id: str
    opportunity_type: OpportunityType
    total_stake: float = Field(..., gt=0)

class SessionInit(BaseModel):
    user_name: Optional[str] = "Anonymous"

# Filter Models
class OpportunityFilter(BaseModel):
    category: Optional[OpportunityType] = None
    sport: Optional[str] = None
    min_roi: Optional[float] = 0.0
    min_profit: Optional[float] = 0.0
    top_n: Optional[int] = 100
    status: Optional[OpportunityStatus] = OpportunityStatus.ACTIVE

class OddsFilter(BaseModel):
    sport: Optional[str] = None
    market: Optional[str] = None
    bookmaker: Optional[str] = None
    event_id: Optional[str] = None