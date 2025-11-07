from fastapi import APIRouter
from app.utils.csv_io import safe_read_csv
from app.services.demo_seed import generate_demo_data
from app.services.arb_service import ArbitrageService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_stats():
    """
    Get comprehensive statistics from all CSV files.
    """
    # Read all CSV files
    odds_df = safe_read_csv("odds.csv")
    arb_df = safe_read_csv("arbitrage.csv")
    bets_df = safe_read_csv("bets.csv")
    sessions_df = safe_read_csv("sessions.csv")
    
    # Odds stats
    odds_stats = {
        "total_odds": len(odds_df),
        "sports": odds_df['sport'].unique().tolist() if not odds_df.empty else [],
        "bookmakers": odds_df['bookmaker'].unique().tolist() if not odds_df.empty else [],
        "matches": odds_df['match'].nunique() if not odds_df.empty else 0
    }
    
    # Arbitrage stats
    arb_stats = {
        "total_opportunities": len(arb_df),
        "avg_profit_percentage": round(arb_df['profit_percentage'].mean(), 2) if not arb_df.empty else 0,
        "max_profit_percentage": round(arb_df['profit_percentage'].max(), 2) if not arb_df.empty else 0,
        "min_profit_percentage": round(arb_df['profit_percentage'].min(), 2) if not arb_df.empty else 0
    }
    
    # Bets stats
    bets_stats = {
        "total_bets": len(bets_df),
        "total_stake": round(bets_df['stake'].sum(), 2) if not bets_df.empty else 0,
        "total_expected_profit": round(bets_df['expected_profit'].sum(), 2) if not bets_df.empty else 0,
        "avg_bet_size": round(bets_df['stake'].mean(), 2) if not bets_df.empty else 0
    }
    
    # Sessions stats
    sessions_stats = {
        "total_sessions": len(sessions_df),
        "active_sessions": len(sessions_df[sessions_df['total_bets'] > 0]) if not sessions_df.empty else 0
    }
    
    return {
        "success": True,
        "odds": odds_stats,
        "arbitrage": arb_stats,
        "bets": bets_stats,
        "sessions": sessions_stats
    }

@router.post("/seed")
async def seed_data(num_odds: int = 500):
    """
    Generate demo data for testing.
    Regenerates odds.csv and initializes other files.
    """
    result = generate_demo_data(num_odds=num_odds)
    
    # Compute arbitrage opportunities
    arb_count = ArbitrageService.compute_arbitrage()
    
    return {
        "success": True,
        "message": "Demo data generated successfully",
        "odds_generated": result['odds_count'],
        "arbitrage_found": arb_count,
        "sports": result['sports'],
        "bookmakers": result['bookmakers']
    }

@router.delete("/reset")
async def reset_data():
    """
    Reset all data files (dangerous operation).
    """
    import pandas as pd
    from app.utils.csv_io import safe_write_csv
    
    # Reset all files to empty
    safe_write_csv("odds.csv", pd.DataFrame(columns=[
        "id", "sport", "match", "market", "bookmaker", "outcome", "odds", "timestamp"
    ]))
    
    safe_write_csv("arbitrage.csv", pd.DataFrame(columns=[
        "id", "sport", "match", "market", "outcome1", "bookmaker1", "odds1",
        "outcome2", "bookmaker2", "odds2", "outcome3", "bookmaker3", "odds3",
        "arb_percentage", "profit_percentage", "timestamp"
    ]))
    
    safe_write_csv("bets.csv", pd.DataFrame(columns=[
        "bet_id", "session_id", "arbitrage_id", "bookmaker", "outcome",
        "stake", "odds", "expected_return", "expected_profit", "timestamp"
    ]))
    
    safe_write_csv("sessions.csv", pd.DataFrame(columns=[
        "session_id", "created_at", "total_bets", "total_stake", "total_expected_profit"
    ]))
    
    return {
        "success": True,
        "message": "All data has been reset"
    }