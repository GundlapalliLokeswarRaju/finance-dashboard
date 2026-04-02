from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.transaction import LoginRequest, TokenResponse
from app.services.auth import login

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Login and get JWT token")
def login_endpoint(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login with JSON body — use this from your frontend or curl."""
    result = login(db, payload.email, payload.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return result


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Login via Swagger UI Authorize button",
)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 form-compatible login used by Swagger UI Authorize button.
    Put your email in the 'username' field and password in 'password'.
    Leave client_id and client_secret blank.
    """
    result = login(db, form_data.username, form_data.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return result
