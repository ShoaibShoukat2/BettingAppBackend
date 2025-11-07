from fastapi import APIRouter, HTTPException
from app.models.schemas import SessionInit
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["Sessions"])

@router.post("/init")
async def init_session(session_data: SessionInit = SessionInit()):
    """
    Initialize a new betting session.
    Generates a unique session ID and stores in sessions.csv.
    """
    result = SessionService.create_session(user_name=session_data.user_name)
    
    return {
        "success": True,
        "session": result
    }

@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get session details by ID."""
    session = SessionService.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "session": session
    }

@router.get("/")
async def get_all_sessions():
    """Get all sessions."""
    sessions = SessionService.get_all_sessions()
    
    return {
        "success": True,
        "count": len(sessions),
        "sessions": sessions
    }