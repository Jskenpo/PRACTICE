from fastapi import APIRouter, HTTPException, Depends
from controllers.auth import get_current_user
router = APIRouter()

@router.get("/")
async def who_am_i(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Sesión válida",
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "sub": current_user.get("sub"),
        "scopes": current_user.get("scope"),
    }