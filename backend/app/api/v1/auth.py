"""Authentication endpoints: signup, login, and current-user retrieval."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_audit
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password, verify_token
from app.db.session import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorLogin, DoctorResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_doctor(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Doctor:
    """Decode the JWT and return the authenticated Doctor, or raise 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        doctor_id: str | None = payload.get("sub")
        if doctor_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if doctor is None:
        raise credentials_exception
    return doctor


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def signup(request: Request, body: DoctorCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Register a new doctor account and return a JWT.

    Raises 409 if the email is already registered.
    """
    existing = await db.execute(select(Doctor).where(Doctor.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A doctor with this email already exists.",
        )

    doctor = Doctor(
        full_name=body.full_name,
        email=body.email,
        phone=body.phone,
        password_hash=hash_password(body.password),
    )
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)

    access_token = create_access_token(data={"sub": str(doctor.id)})

    log_audit(action="signup", actor_id=str(doctor.id), resource="auth", details={"email": doctor.email})

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        status_code=status.HTTP_201_CREATED,
    )
    response.set_cookie(
        key="pp_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, body: DoctorLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate a doctor by email/password and return a JWT.

    Raises 401 on invalid credentials.
    """
    result = await db.execute(select(Doctor).where(Doctor.email == body.email))
    doctor = result.scalar_one_or_none()
    if not doctor or not verify_password(body.password, doctor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(data={"sub": str(doctor.id)})

    log_audit(action="login", actor_id=str(doctor.id), resource="auth", details={"email": doctor.email})

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
    )
    response.set_cookie(
        key="pp_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response


@router.get("/me", response_model=DoctorResponse)
async def get_me(doctor: Doctor = Depends(get_current_doctor)) -> DoctorResponse:
    """Return the profile of the currently authenticated doctor."""
    return DoctorResponse.model_validate(doctor)
