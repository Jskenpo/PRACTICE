from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.controllers.auth_controller import get_current_user, login

router = APIRouter()


@router.post("/login")
def login_route(form: OAuth2PasswordRequestForm = Depends()):
    return login(form.username, form.password)


@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user
