"""
Unified Opportunities Routes
Handles all opportunity types: Arbitrage, Middles, EV, Lows
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.opportunity_service import OpportunityService
from app.models.schemas import OpportunityType, OpportunityStatus

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("/feed")
async def get_opportunities_feed(
    category: Optional[OpportunityType] = Query(None, description="Filter by opportunity type"),
    sport: Optional[str] = Query(None, description="Filter by sport"),
    min_roi: float = Query(0.0, description="Minimum ROI percentage"),
    min_profit: float = Query(0.0, description="Minimum profit percentage"),
    top_n: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    status: OpportunityStatus = Query(OpportunityStatus.ACTIVE, description="Filter by status")
):
    """
    Get unified opportunities feed with filters
    
    Categories:
    - arbitrage: Risk-free profit opportunities
    - middle: Overlapping line opportunities (win-win scenarios)
    - ev: Positive expected value bets
    - low: Low-hold markets (low bookmaker margin)
    
    Example queries:
    - /opportunities/feed?category=arbitrage&min_roi=2.0
    - /opportunities/feed?sport=Football&min_profit=1.5
    - /opportunities/feed?category=ev&top_n=20
    """
    opportunities = OpportunityService.get_opportunities(
        category=category.value if category else None,
        sport=sport,
        min_roi=min_roi,
        min_profit=min_profit,
        top_n=top_n,
        status=status.value
    )
    
    return {
        "success": True,
        "count": len(opportunities),
        "filters": {
            "category": category,
            "sport": sport,
            "min_roi": min_roi,
            "min_profit": min_profit,
            "status": status
        },
        "opportunities": opportunities
    }

@router.get("/{opportunity_id}")
async def get_opportunity_by_id(opportunity_id: str):
    """
    Get specific opportunity by ID
    Returns full details of the opportunity
    """
    opportunity = OpportunityService.get_opportunity_by_id(opportunity_id)
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return {
        "success": True,
        "opportunity": opportunity
    }

@router.post("/compute")
async def compute_opportunities():
    """
    Manually trigger opportunity detection
    Runs all detection algorithms:
    - Arbitrage detection
    - Middle detection
    - EV detection
    - Low-hold detection
    
    Also performs cleanup of expired opportunities
    """
    counts = OpportunityService.compute_all_opportunities()
    
    return {
        "success": True,
        "message": f"Computed {counts['total']} opportunities",
        "breakdown": counts
    }

@router.get("/stats/summary")
async def get_opportunity_stats():
    """Get statistics about opportunities"""
    stats = OpportunityService.get_stats()
    
    return {
        "success": True,
        "stats": stats
    }

@router.delete("/{opportunity_id}")
async def remove_opportunity(opportunity_id: str):
    """
    Mark opportunity as removed
    Used when opportunity is no longer valid or has been bet on
    """
    success = OpportunityService.mark_opportunity_as_used(opportunity_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return {
        "success": True,
        "message": "Opportunity marked as removed"
    }

# Legacy endpoint for backward compatibility
@router.get("/arbitrage/feed")
async def get_arbitrage_feed_legacy(
    min_arb: float = Query(0.0, description="Minimum profit percentage"),
    top_n: int = Query(100, description="Maximum number of results"),
    sport: Optional[str] = Query(None, description="Filter by sport")
):
    """
    Legacy arbitrage feed endpoint
    Redirects to unified opportunities feed with arbitrage filter
    """
    opportunities = OpportunityService.get_opportunities(
        category="arbitrage",
        sport=sport,
        min_profit=min_arb,
        top_n=top_n
    )
    
    return {
        "success": True,
        "count": len(opportunities),
        "arbitrage_opportunities": opportunities
    }