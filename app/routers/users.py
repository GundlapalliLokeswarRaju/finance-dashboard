from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user [Admin only]",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.create_user(db, payload)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users [Admin only]",
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = user_service.get_all_users(db)
    return UserListResponse(total=len(users), users=users)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID [Admin only]",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.get_user_by_id(db, user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user role or status [Admin only]",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.update_user(db, user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete a user [Admin only]",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user_service.delete_user(db, user_id)
