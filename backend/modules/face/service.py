from backend.database.connection import get_database
from backend.utils.face import get_face_encoding, save_face_encodings, load_face_encodings, compare_faces
from fastapi import UploadFile, HTTPException, status
import shutil
import os
import uuid

UPLOAD_DIR = "uploads/faces"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def register_face(user_id: str, file: UploadFile):
    # Save temp file
    file_extension = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{user_id}.{file_extension}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get encoding
    encoding = get_face_encoding(file_path)
    if not encoding:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="No face detected in image")
    
    # Save to global encodings file (simple approach for now)
    all_encodings = load_face_encodings()
    all_encodings[user_id] = encoding
    save_face_encodings(all_encodings)
    
    # Update user in DB
    db = await get_database()
    await db.users.update_one(
        {"_id": user_id},
        {"$set": {"face_registered": True, "face_image_path": file_path}}
    )
    
    return {"message": "Face registered successfully"}

async def recognize_face(file: UploadFile):
    # Save temp file for processing
    temp_filename = f"{uuid.uuid4()}.jpg"
    temp_path = f"{UPLOAD_DIR}/{temp_filename}"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        unknown_encoding = get_face_encoding(temp_path)
        if not unknown_encoding:
            raise HTTPException(status_code=400, detail="No face detected")
            
        known_encodings_dict = load_face_encodings()
        known_ids = list(known_encodings_dict.keys())
        known_encodings = list(known_encodings_dict.values())
        
        if not known_encodings:
             raise HTTPException(status_code=404, detail="No registered faces found")

        matches = compare_faces(known_encodings, unknown_encoding)
        
        if True in matches:
            first_match_index = matches.index(True)
            user_id = known_ids[first_match_index]
            
            db = await get_database()
            user = await db.users.find_one({"_id": user_id})
            return user
            
        return None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
