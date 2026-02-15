"""
Authentication API Router
Handles user registration, login, and JWT token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import sqlite3

from app.core.logging_config import get_logger
from app.core.config import settings
from app.core.models.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from app.core.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    TokenInvalidException
)


logger = get_logger(__name__)
router = APIRouter()


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================================================================
# Helper Functions
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(settings.DATABASE_URL.replace("sqlite:///", ""))
    conn.row_factory = sqlite3.Row
    return conn


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user from database by username"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user from database by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get current user from JWT token
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User dictionary
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise TokenInvalidException("Token missing required fields")
        
        token_data = TokenData(username=username, user_id=user_id)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(token_data.username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """
    Register a new user
    
    Args:
        user: User registration data
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user already exists
    """
    logger.info(f"📝 Registration attempt | Username: {user.username}")
    
    # Check if user exists
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user in database
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, hashed_password, full_name, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user.username, user.email, hashed_password, user.full_name, "student")
        )
        
        conn.commit()
        user_id = cursor.lastrowid
        
        logger.info(f"✅ User registered | ID: {user_id} | Username: {user.username}")
        
        # Fetch created user
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        created_user = dict(cursor.fetchone())
        
        conn.close()
        
        return UserResponse(**created_user)
        
    except sqlite3.IntegrityError as e:
        conn.close()
        logger.error(f"❌ Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login and get access token
    
    Args:
        form_data: Username and password
        
    Returns:
        Access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    logger.info(f"🔐 Login attempt | Username: {form_data.username}")
    
    # Get user
    user = get_user_by_username(form_data.username)
    
    if not user:
        logger.warning(f"⚠️ Login failed | User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        logger.warning(f"⚠️ Login failed | Invalid password: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["id"]}
    )
    
    logger.info(f"✅ Login successful | User: {form_data.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(**current_user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (client-side token deletion)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    logger.info(f"👋 User logged out | Username: {current_user['username']}")
    
    return {
        "message": "Successfully logged out",
        "username": current_user["username"]
    }


# ============================================================================
# Database Initialization
# ============================================================================

def init_database():
    """Initialize database with schema"""
    conn = get_db()
    
    # Read and execute schema
    with open("database_schema.sql", "r") as f:
        schema = f.read()
        conn.executescript(schema)
    
    conn.close()
    logger.info("✅ Database initialized")


if __name__ == "__main__":
    # Initialize database
    init_database()
    print("✅ Database initialized successfully")
