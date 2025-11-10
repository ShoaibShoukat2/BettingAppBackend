from fastapi import APIRouter, HTTPException
from app.models.schemas import BetPlacement
from app.services.bet_service import BetService

router = APIRouter(prefix="/bets", tags=["Bets"])

@router.post("/place")
async def place_bet(bet_data: BetPlacement):
    """
    Place bets for an arbitrage opportunity.
    Calculates optimal stakes and records all bets.
    """
    result = BetService.place_bet(
        session_id=bet_data.session_id,
        arbitrage_id=bet_data.arbitrage_id,
        total_stake=bet_data.total_stake
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result

@router.get("/session/{session_id}")
async def get_session_bets(session_id: str):
    """Get all bets for a specific session."""
    bets = BetService.get_bets_by_session(session_id)
    
    return {
        "success": True,
        "count": len(bets),
        "bets": bets
    }

@router.get("/{bet_id}")
async def get_bet(bet_id: str):
    """Get specific bet by ID."""
    bet = BetService.get_bet_by_id(bet_id)
    
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    
    return {
        "success": True,
        "bet": bet
    }

@router.get("/")
async def get_all_bets():
    """Get all bets."""
    bets = BetService.get_all_bets()
    
    return {
        "success": True,
        "count": len(bets),
        "bets": bets
    }


