"""
Opportunity Service - Manages all opportunity types and lifecycle
Handles detection, storage, expiry, and cleanup
"""

import pandas as pd
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.utils.csv_io import safe_read_csv, safe_write_csv
from app.services.detection_service import DetectionService

class OpportunityService:
    """Unified service for managing all opportunity types"""
    
    @staticmethod
    def compute_all_opportunities() -> Dict[str, int]:
        """
        Compute all opportunity types (arbitrage, middles, EV, lows)
        Returns count of each type found
        """
        # Read odds data
        odds_df = safe_read_csv("odds.csv")
        
        if odds_df.empty:
            return {
                "arbitrage": 0,
                "middles": 0,
                "ev": 0,
                "lows": 0,
                "total": 0
            }
        
        # Filter only active odds
        odds_df = odds_df[odds_df['is_active'] == True]
        
        # Run all detection algorithms
        arbitrage_opps = DetectionService.detect_arbitrage(odds_df)
        middle_opps = DetectionService.detect_middles(odds_df)
        ev_opps = DetectionService.detect_ev(odds_df)
        low_opps = DetectionService.detect_lows(odds_df)
        
        # Prepare unified opportunities data
        all_opportunities = []
        
        # Add arbitrage opportunities
        for opp in arbitrage_opps:
            all_opportunities.append({
                'id': opp['id'],
                'type': 'arbitrage',
                'event_id': opp['event_id'],
                'sport': opp['sport'],
                'match': opp['match'],
                'roi': opp['roi'],
                'profit_percentage': opp['profit_percentage'],
                'status': 'active',
                'timestamp': opp['timestamp'],
                'expires_at': opp['expires_at'],
                'details': json.dumps(opp)
            })
        
        # Add middle opportunities
        for opp in middle_opps:
            all_opportunities.append({
                'id': opp['id'],
                'type': 'middle',
                'event_id': opp['event_id'],
                'sport': opp['sport'],
                'match': opp['match'],
                'roi': opp['roi'],
                'profit_percentage': opp.get('max_profit_percentage'),
                'status': 'active',
                'timestamp': opp['timestamp'],
                'expires_at': opp['expires_at'],
                'details': json.dumps(opp)
            })
        
        # Add EV opportunities
        for opp in ev_opps:
            all_opportunities.append({
                'id': opp['id'],
                'type': 'ev',
                'event_id': opp['event_id'],
                'sport': opp['sport'],
                'match': opp['match'],
                'roi': opp['roi'],
                'profit_percentage': opp['edge_percentage'],
                'status': 'active',
                'timestamp': opp['timestamp'],
                'expires_at': opp['expires_at'],
                'details': json.dumps(opp)
            })
        
        # Add low-hold opportunities
        for opp in low_opps:
            all_opportunities.append({
                'id': opp['id'],
                'type': 'low',
                'event_id': opp['event_id'],
                'sport': opp['sport'],
                'match': opp['match'],
                'roi': opp['roi'],
                'profit_percentage': None,
                'status': 'active',
                'timestamp': opp['timestamp'],
                'expires_at': opp['expires_at'],
                'details': json.dumps(opp)
            })
        
        # Clean up old opportunities before saving new ones
        OpportunityService._cleanup_expired_opportunities()
        
        # Save all opportunities
        if all_opportunities:
            opps_df = pd.DataFrame(all_opportunities)
            safe_write_csv("opportunities.csv", opps_df)
        
        return {
            "arbitrage": len(arbitrage_opps),
            "middles": len(middle_opps),
            "ev": len(ev_opps),
            "lows": len(low_opps),
            "total": len(all_opportunities)
        }
    
    @staticmethod
    def get_opportunities(
        category: Optional[str] = None,
        sport: Optional[str] = None,
        min_roi: float = 0.0,
        min_profit: float = 0.0,
        top_n: int = 100,
        status: str = "active"
    ) -> List[Dict[str, Any]]:
        """
        Get opportunities with filters
        """
        df = safe_read_csv("opportunities.csv")
        
        if df.empty:
            return []
        
        # Apply filters
        if status:
            df = df[df['status'] == status]
        
        if category:
            df = df[df['type'] == category]
        
        if sport:
            df = df[df['sport'].str.lower() == sport.lower()]
        
        if min_roi > 0:
            df = df[df['roi'] >= min_roi]
        
        if min_profit > 0:
            df = df[df['profit_percentage'] >= min_profit]
        
        # Sort by ROI (highest first)
        df = df.sort_values('roi', ascending=False)
        
        # Limit results
        df = df.head(top_n)
        
        # Parse details JSON and return
        results = []
        for _, row in df.iterrows():
            try:
                details = json.loads(row['details'])
                results.append(details)
            except:
                continue
        
        return results
    
    @staticmethod
    def get_opportunity_by_id(opportunity_id: str) -> Optional[Dict[str, Any]]:
        """Get specific opportunity by ID"""
        df = safe_read_csv("opportunities.csv")
        
        if df.empty:
            return None
        
        result = df[df['id'] == opportunity_id]
        
        if result.empty:
            return None
        
        try:
            details = json.loads(result.iloc[0]['details'])
            return details
        except:
            return None
    
    @staticmethod
    def _cleanup_expired_opportunities():
        """
        Remove expired opportunities based on:
        1. expires_at timestamp
        2. Inactive odds (odds no longer exist or changed significantly)
        """
        df = safe_read_csv("opportunities.csv")
        
        if df.empty:
            return
        
        now = datetime.now()
        
        # Mark expired based on expires_at
        def is_expired(expires_at):
            if pd.isna(expires_at):
                return False
            try:
                expiry = datetime.fromisoformat(expires_at)
                return now > expiry
            except:
                return False
        
        df['is_expired'] = df['expires_at'].apply(is_expired)
        
        # Update status
        df.loc[df['is_expired'], 'status'] = 'expired'
        
        # Remove expired column
        df = df.drop('is_expired', axis=1)
        
        # Optional: Remove very old expired opportunities (keep last 24 hours)
        # For now, just mark as expired
        
        safe_write_csv("opportunities.csv", df)
    
    @staticmethod
    def mark_opportunity_as_used(opportunity_id: str) -> bool:
        """Mark opportunity as removed after being bet on"""
        df = safe_read_csv("opportunities.csv")
        
        if df.empty:
            return False
        
        # Find opportunity
        opp_idx = df[df['id'] == opportunity_id].index
        
        if opp_idx.empty:
            return False
        
        idx = opp_idx[0]
        df.at[idx, 'status'] = 'removed'
        
        safe_write_csv("opportunities.csv", df)
        return True
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get opportunity statistics"""
        df = safe_read_csv("opportunities.csv")
        
        if df.empty:
            return {
                "total_opportunities": 0,
                "by_type": {},
                "by_status": {},
                "avg_roi": 0,
                "max_roi": 0
            }
        
        stats = {
            "total_opportunities": len(df),
            "by_type": df['type'].value_counts().to_dict(),
            "by_status": df['status'].value_counts().to_dict(),
            "avg_roi": round(df['roi'].mean(), 2),
            "max_roi": round(df['roi'].max(), 2)
        }
        
        return stats