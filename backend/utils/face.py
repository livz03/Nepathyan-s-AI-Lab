try:
    import face_recognition
except ImportError:
    print("WARNING: face_recognition not installed. Face features will be disabled.")
    face_recognition = None

import numpy as np
import pickle
import os
from typing import List, Optional

FACE_MODEL_PATH = "face-models/encodings.pkl"

def load_face_encodings():
    if not os.path.exists(FACE_MODEL_PATH):
        return {}
    with open(FACE_MODEL_PATH, "rb") as f:
        return pickle.load(f)

def save_face_encodings(encodings):
    os.makedirs(os.path.dirname(FACE_MODEL_PATH), exist_ok=True)
    with open(FACE_MODEL_PATH, "wb") as f:
        pickle.dump(encodings, f)

def get_face_encoding(image_file) -> Optional[List[float]]:
    if face_recognition is None:
        return None # Mock behavior
        
    try:
        image = face_recognition.load_image_file(image_file)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            return encodings[0].tolist()
        return None
    except Exception as e:
        print(f"Error encoding face: {e}")
        return None

def compare_faces(known_encodings: List[List[float]], face_encoding: List[float], tolerance=0.6) -> List[bool]:
    if face_recognition is None:
        return [False] * len(known_encodings) # Mock behavior
        
    return face_recognition.compare_faces(known_encodings, np.array(face_encoding), tolerance=tolerance)
