from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.schemas.common import StandardResponse
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new patient or doctor user."""
    user = AuthService.register_user(db, data)
    user_dto = AuthService.get_user_dto(user)
    return StandardResponse(
        success=True,
        message="User account registered successfully",
        data=user_dto
    )


@router.post("/login", response_model=StandardResponse[Token])
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password to receive JWT."""
    token = AuthService.authenticate_user(db, data)
    return StandardResponse(
        success=True,
        message="Authentication successful",
        data=token
    )


@router.get("/me", response_model=StandardResponse[UserResponse])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile and role details for the authenticated user."""
    user_dto = AuthService.get_user_dto(current_user)
    return StandardResponse(
        success=True,
        message="User profile retrieved",
        data=user_dto
    )
