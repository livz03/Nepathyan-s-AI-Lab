from backend.database.connection import get_database
from backend.database.schemas import UserCreate, UserInDB
from backend.utils.security import get_password_hash, verify_password
from fastapi import HTTPException, status

async def create_user(user: UserCreate):
    db = await get_database()
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(
        **user.dict(),
        hashed_password=hashed_password
    )
    
    new_user = await db.users.insert_one(user_in_db.dict())
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    
    return created_user

async def authenticate_user(email: str, password: str):
    db = await get_database()
    user = await db.users.find_one({"email": email})
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user
