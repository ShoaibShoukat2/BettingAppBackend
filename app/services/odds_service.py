import pandas as pd
from typing import Optional, List, Dict, Any
from app.utils.csv_io import safe_read_csv
from app.models.schemas import OddsRow, OddsFilter

class OddsService:
    """Service for reading and filtering odds data."""
    
    @staticmethod
    def get_live_odds(sport: Optional[str] = None, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get live odds from CSV with optional filters.
        """
        df = safe_read_csv("odds.csv")
        
        if df.empty:
            return []
        
        # Apply filters
        if sport:
            df = df[df['sport'].str.lower() == sport.lower()]
        
        if market:
            df = df[df['market'].str.lower() == market.lower()]
        
        # Convert to list of dictionaries
        return df.to_dict('records')
    
    @staticmethod
    def get_odds_snapshot() -> Dict[str, Any]:
        """
        Get a snapshot of current odds for WebSocket broadcasting.
        """
        df = safe_read_csv("odds.csv")
        
        if df.empty:
            return {
                "total_odds": 0,
                "sports": [],
                "bookmakers": [],
                "matches": [],
                "odds": []
            }
        
        return {
            "total_odds": len(df),
            "sports": df['sport'].unique().tolist(),
            "bookmakers": df['bookmaker'].unique().tolist(),
            "matches": df['match'].unique().tolist(),
            "odds": df.to_dict('records')
        }
    
    @staticmethod
    def get_odds_by_match(match: str) -> List[Dict[str, Any]]:
        """Get all odds for a specific match."""
        df = safe_read_csv("odds.csv")
        
        if df.empty:
            return []
        
        df = df[df['match'].str.lower() == match.lower()]
        return df.to_dict('records')
    
    @staticmethod
    def get_available_sports() -> List[str]:
        """Get list of available sports."""
        df = safe_read_csv("odds.csv")
        
        if df.empty:
            return []
        
        return df['sport'].unique().tolist()
    
    @staticmethod
    def get_available_markets(sport: Optional[str] = None) -> List[str]:
        """Get list of available markets, optionally filtered by sport."""
        df = safe_read_csv("odds.csv")
        
        if df.empty:
            return []
        
        if sport:
            df = df[df['sport'].str.lower() == sport.lower()]
        
        return df['market'].unique().tolist()