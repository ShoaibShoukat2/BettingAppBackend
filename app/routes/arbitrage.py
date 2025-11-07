from fastapi import APIRouter, Query
from typing import Optional
from app.services.arb_service import ArbitrageService

router = APIRouter(prefix="/arbitrage", tags=["Arbitrage"])

@router.get("/feed")
async def get_arbitrage_feed(
    min_arb: float = Query(0.0, description="Minimum profit percentage"),
    top_n: int = Query(100, description="Maximum number of results"),
    sport: Optional[str] = Query(None, description="Filter by sport")
):
    """
    Get arbitrage opportunities feed with filters.
    """
    arbs = ArbitrageService.get_arbitrage_feed(
        min_arb=min_arb,
        top_n=top_n,
        sport=sport
    )
    
    return {
        "success": True,
        "count": len(arbs),
        "arbitrage_opportunities": arbs
    }

@router.get("/{arb_id}")
async def get_arbitrage_by_id(arb_id: str):
    """Get specific arbitrage opportunity by ID."""
    arb = ArbitrageService.get_arbitrage_by_id(arb_id)
    
    if not arb:
        return {
            "success": False,
            "error": "Arbitrage opportunity not found"
        }
    
    return {
        "success": True,
        "arbitrage": arb
    }

@router.post("/compute")
async def compute_arbitrage():
    """
    Manually trigger arbitrage computation.
    Scans odds.csv and writes to arbitrage.csv.
    """
    count = ArbitrageService.compute_arbitrage()
    
    return {
        "success": True,
        "message": f"Computed {count} arbitrage opportunities",
        "count": count
    }

@router.get("/{arb_id}/calculate-stakes")
async def calculate_stakes(
    arb_id: str,
    total_stake: float = Query(..., gt=0, description="Total amount to stake")
):
    """
    Calculate optimal stake distribution for an arbitrage opportunity.
    """
    stakes = ArbitrageService.calculate_stakes(arb_id, total_stake)
    
    if not stakes:
        return {
            "success": False,
            "error": "Arbitrage opportunity not found"
        }
    
    return {
        "success": True,
        "calculation": stakes
    }