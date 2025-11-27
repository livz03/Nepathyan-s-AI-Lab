from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.modules.face import service
from backend.utils.security import get_current_user
from backend.database.schemas import UserResponse

router = APIRouter(tags=["Face Recognition"])

@router.post("/register")
async def register_face_route(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    return await service.register_face(current_user["_id"], file)

@router.post("/recognize", response_model=UserResponse)
async def recognize_face_route(file: UploadFile = File(...)):
    user = await service.recognize_face(file)
    if not user:
        raise HTTPException(status_code=404, detail="User not recognized")
    return user
