import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.utils.csv_io import safe_read_csv, append_row
from app.services.arb_service import ArbitrageService
from app.services.session_service import SessionService

class BetService:
    """Service for managing bet placements."""
    
    @staticmethod
    def place_bet(session_id: str, arbitrage_id: str, total_stake: float) -> Dict[str, Any]:
        """
        Place bets for an arbitrage opportunity.
        """
        # Verify session exists
        session = SessionService.get_session(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Invalid session ID'
            }
        
        # Get arbitrage opportunity and calculate stakes
        stake_calc = ArbitrageService.calculate_stakes(arbitrage_id, total_stake)
        
        if not stake_calc:
            return {
                'success': False,
                'error': 'Invalid arbitrage ID'
            }
        
        # Get arbitrage details
        arb = ArbitrageService.get_arbitrage_by_id(arbitrage_id)
        
        timestamp = datetime.now().isoformat()
        placed_bets = []
        
        # Place individual bets for each outcome
        for outcome, stake in stake_calc['stakes'].items():
            bet_id = str(uuid.uuid4())
            bookmaker = stake_calc['bookmakers'][outcome]
            
            # Determine odds
            if outcome == arb['outcome1']:
                odds = arb['odds1']
            elif outcome == arb['outcome2']:
                odds = arb['odds2']
            else:
                odds = arb['odds3']
            
            expected_return = stake * odds
            expected_profit = expected_return - total_stake
            
            bet_data = {
                'bet_id': bet_id,
                'session_id': session_id,
                'arbitrage_id': arbitrage_id,
                'bookmaker': bookmaker,
                'outcome': outcome,
                'stake': round(stake, 2),
                'odds': odds,
                'expected_return': round(expected_return, 2),
                'expected_profit': round(expected_profit, 2),
                'timestamp': timestamp
            }
            
            append_row("bets.csv", bet_data)
            placed_bets.append(bet_data)
        
        # Update session stats
        SessionService.update_session_stats(
            session_id, 
            total_stake, 
            stake_calc['expected_profit']
        )
        
        return {
            'success': True,
            'bets': placed_bets,
            'summary': stake_calc,
            'arbitrage': {
                'sport': arb['sport'],
                'match': arb['match'],
                'market': arb['market']
            }
        }
    
    @staticmethod
    def get_bets_by_session(session_id: str) -> List[Dict[str, Any]]:
        """Get all bets for a specific session."""
        df = safe_read_csv("bets.csv")
        
        if df.empty:
            return []
        
        result = df[df['session_id'] == session_id]
        return result.to_dict('records')
    
    @staticmethod
    def get_all_bets() -> List[Dict[str, Any]]:
        """Get all bets."""
        df = safe_read_csv("bets.csv")
        
        if df.empty:
            return []
        
        return df.to_dict('records')
    
    @staticmethod
    def get_bet_by_id(bet_id: str) -> Optional[Dict[str, Any]]:
        """Get specific bet by ID."""
        df = safe_read_csv("bets.csv")
        
        if df.empty:
            return None
        
        result = df[df['bet_id'] == bet_id]
        
        if result.empty:
            return None
        
        return result.iloc[0].to_dict()