import face_recognition as fr
import numpy as np
from fastapi import HTTPException
import os
from datetime import datetime

UPLOAD_DIR = "uploads/faces"

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_image(image_data: bytes, user_id: str) -> str:
    """Save the image to disk and return the path"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(image_data)
    
    return filepath

async def register_face(image_data: bytes, user_id: str):
    """Register a face for a user"""
    try:
        # Save the image
        image_path = await save_image(image_data, user_id)
        
        # Load and encode the face
        image = fr.load_image_file(image_path)
        face_locations = fr.face_locations(image)
        
        if not face_locations:
            raise HTTPException(status_code=400, detail="No face detected in the image")
        
        if len(face_locations) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected. Please ensure only one face is in the image")
        
        face_encoding = fr.face_encodings(image)[0]
        
        # Convert numpy array to list for storage
        return face_encoding.tolist()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def verify_face(image_data: bytes, stored_encoding: list):
    """Verify a face against a stored encoding"""
    try:
        # Save the image temporarily
        temp_path = os.path.join(UPLOAD_DIR, "temp_verify.jpg")
        with open(temp_path, "wb") as f:
            f.write(image_data)
        
        # Load and encode the face
        image = fr.load_image_file(temp_path)
        face_locations = fr.face_locations(image)
        
        if not face_locations:
            raise HTTPException(status_code=400, detail="No face detected in the image")
        
        if len(face_locations) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected. Please ensure only one face is in the image")
        
        face_encoding = fr.face_encodings(image)[0]
        
        # Convert stored encoding back to numpy array
        stored_encoding_array = np.array(stored_encoding)
        
        # Compare faces
        matches = fr.compare_faces([stored_encoding_array], face_encoding, tolerance=0.6)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return matches[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
