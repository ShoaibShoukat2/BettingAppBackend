"""
Enhanced Admin Routes
Stats, data management, and refresh operations
"""

from fastapi import APIRouter
from app.utils.csv_io import safe_read_csv
from app.services.demo_seed import generate_demo_data
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_comprehensive_stats():
    """
    Get comprehensive statistics from all data sources
    """
    # Read all CSV files
    odds_df = safe_read_csv("odds.csv")
    opportunities_df = safe_read_csv("opportunities.csv")
    bets_df = safe_read_csv("bets.csv")
    sessions_df = safe_read_csv("sessions.csv")
    
    # Odds stats
    odds_stats = {
        "total_odds": len(odds_df),
        "active_odds": len(odds_df[odds_df['is_active'] == True]) if not odds_df.empty else 0,
        "sports": odds_df['sport'].unique().tolist() if not odds_df.empty else [],
        "bookmakers": odds_df['bookmaker'].unique().tolist() if not odds_df.empty else [],
        "events": odds_df['event_id'].nunique() if not odds_df.empty else 0,
        "markets": odds_df['market'].nunique() if not odds_df.empty else 0
    }
    
    # Opportunities stats
    if not opportunities_df.empty:
        opp_stats = {
            "total_opportunities": len(opportunities_df),
            "active_opportunities": len(opportunities_df[opportunities_df['status'] == 'active']),
            "by_type": opportunities_df['type'].value_counts().to_dict(),
            "by_status": opportunities_df['status'].value_counts().to_dict(),
            "avg_roi": round(opportunities_df['roi'].mean(), 2),
            "max_roi": round(opportunities_df['roi'].max(), 2),
            "top_opportunities": opportunities_df.nlargest(5, 'roi')[['type', 'sport', 'match', 'roi']].to_dict('records')
        }
    else:
        opp_stats = {
            "total_opportunities": 0,
            "active_opportunities": 0,
            "by_type": {},
            "by_status": {},
            "avg_roi": 0,
            "max_roi": 0,
            "top_opportunities": []
        }
    
    # Bets stats
    if not bets_df.empty:
        bets_stats = {
            "total_bets": len(bets_df),
            "total_stake": round(bets_df['stake'].sum(), 2),
            "total_expected_profit": round(bets_df['expected_profit'].sum(), 2),
            "avg_bet_size": round(bets_df['stake'].mean(), 2),
            "by_type": bets_df['opportunity_type'].value_counts().to_dict() if 'opportunity_type' in bets_df.columns else {}
        }
    else:
        bets_stats = {
            "total_bets": 0,
            "total_stake": 0,
            "total_expected_profit": 0,
            "avg_bet_size": 0,
            "by_type": {}
        }
    
    # Sessions stats
    sessions_stats = {
        "total_sessions": len(sessions_df),
        "active_sessions": len(sessions_df[sessions_df['total_bets'] > 0]) if not sessions_df.empty else 0
    }
    
    return {
        "success": True,
        "timestamp": pd.Timestamp.now().isoformat(),
        "odds": odds_stats,
        "opportunities": opp_stats,
        "bets": bets_stats,
        "sessions": sessions_stats
    }

@router.post("/refresh")
async def refresh_opportunities():
    """
    Manually refresh all opportunities
    - Cleans up expired opportunities
    - Recomputes all detection algorithms
    - Updates opportunities.csv
    
    Use this endpoint to manually trigger a refresh cycle
    """
    counts = OpportunityService.compute_all_opportunities()
    
    return {
        "success": True,
        "message": "Opportunities refreshed successfully",
        "opportunities_found": counts
    }

@router.post("/seed")
async def seed_demo_data(num_events_per_sport: int = 5):
    """
    Generate demo data for testing
    - Regenerates odds.csv with realistic variance
    - Creates potential arbitrage, middle, EV, and low opportunities
    - Initializes other files if needed
    
    Warning: This will replace existing odds data
    """
    result = generate_demo_data(num_events_per_sport=num_events_per_sport)
    
    # Compute opportunities from new data
    counts = OpportunityService.compute_all_opportunities()
    
    return {
        "success": True,
        "message": "Demo data generated and opportunities computed",
        "odds_generated": result['odds_count'],
        "events_created": result['events_count'],
        "opportunities_found": counts,
        "sports": result['sports'],
        "bookmakers": result['bookmakers']
    }

@router.delete("/reset")
async def reset_all_data():
    """
    Reset all data files (DANGEROUS OPERATION)
    This will delete all odds, opportunities, bets, and sessions
    
    Use with caution - cannot be undone
    """
    import pandas as pd
    from app.utils.csv_io import safe_write_csv
    
    # Reset odds.csv
    safe_write_csv("odds.csv", pd.DataFrame(columns=[
        "odds_id", "event_id", "sport", "match", "market", "market_params",
        "bookmaker", "outcome", "odds", "timestamp", "is_active"
    ]))
    
    # Reset opportunities.csv
    safe_write_csv("opportunities.csv", pd.DataFrame(columns=[
        "id", "type", "event_id", "sport", "match", "roi", "profit_percentage",
        "status", "timestamp", "expires_at", "details"
    ]))
    
    # Reset bets.csv
    safe_write_csv("bets.csv", pd.DataFrame(columns=[
        "bet_id", "session_id", "opportunity_id", "opportunity_type",
        "bookmaker", "outcome", "stake", "odds", "expected_return",
        "expected_profit", "timestamp"
    ]))
    
    # Reset sessions.csv
    safe_write_csv("sessions.csv", pd.DataFrame(columns=[
        "session_id", "created_at", "total_bets", "total_stake", "total_expected_profit"
    ]))
    
    return {
        "success": True,
        "message": "All data has been reset",
        "warning": "This action cannot be undone"
    }

@router.get("/health")
async def health_check():
    """
    Check system health and data integrity
    """
    import os
    from pathlib import Path
    
    data_dir = Path("data")
    
    files_status = {}
    required_files = ["odds.csv", "opportunities.csv", "bets.csv", "sessions.csv"]
    
    for file in required_files:
        file_path = data_dir / file
        files_status[file] = {
            "exists": file_path.exists(),
            "size_kb": round(file_path.stat().st_size / 1024, 2) if file_path.exists() else 0
        }
    
    all_exist = all(status["exists"] for status in files_status.values())
    
    return {
        "success": True,
        "status": "healthy" if all_exist else "degraded",
        "files": files_status,
        "message": "All systems operational" if all_exist else "Some data files missing"
    }

import pandas as pd