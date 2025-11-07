import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from app.utils.csv_io import safe_read_csv, append_row
from app.models.schemas import Session

class SessionService:
    """Service for managing betting sessions."""
    
    @staticmethod
    def create_session(user_name: str = "Anonymous") -> Dict[str, Any]:
        """
        Create a new betting session and store in sessions.csv.
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        session_data = {
            'session_id': session_id,
            'created_at': timestamp,
            'total_bets': 0,
            'total_stake': 0.0,
            'total_expected_profit': 0.0
        }
        
        append_row("sessions.csv", session_data)
        
        return {
            'session_id': session_id,
            'created_at': timestamp,
            'message': 'Session created successfully'
        }
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details by ID."""
        df = safe_read_csv("sessions.csv")
        
        if df.empty:
            return None
        
        result = df[df['session_id'] == session_id]
        
        if result.empty:
            return None
        
        return result.iloc[0].to_dict()
    
    @staticmethod
    def update_session_stats(session_id: str, stake: float, expected_profit: float) -> bool:
        """
        Update session statistics after placing a bet.
        """
        df = safe_read_csv("sessions.csv")
        
        if df.empty:
            return False
        
        # Find session
        session_idx = df[df['session_id'] == session_id].index
        
        if session_idx.empty:
            return False
        
        idx = session_idx[0]
        
        # Update stats
        df.at[idx, 'total_bets'] = df.at[idx, 'total_bets'] + 1
        df.at[idx, 'total_stake'] = df.at[idx, 'total_stake'] + stake
        df.at[idx, 'total_expected_profit'] = df.at[idx, 'total_expected_profit'] + expected_profit
        
        # Write back
        from app.utils.csv_io import safe_write_csv
        return safe_write_csv("sessions.csv", df)
    
    @staticmethod
    def get_all_sessions() -> list:
        """Get all sessions."""
        df = safe_read_csv("sessions.csv")
        
        if df.empty:
            return []
        
        return df.to_dict('records')