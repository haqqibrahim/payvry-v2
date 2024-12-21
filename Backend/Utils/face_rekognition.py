import boto3
import os
import io
from PIL import Image
from fastapi import HTTPException

# AWS Clients
s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

# Constants
S3_BUCKET = 'payvryusers-images'
FACES_FOLDER = 'uploads/faces'

# Helper: Create a directory for a specific user
def create_user_folder(user_id):
    folder_path = os.path.join(FACES_FOLDER, user_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

# Helper: Delete a directory
def delete_user_folder(user_id):
    folder_path = os.path.join(FACES_FOLDER, user_id)
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, file))
        os.rmdir(folder_path)

# Helper: Check for faces in an image
def validate_faces(image_binary):
    try:
        response = rekognition.detect_faces(
            Image={'Bytes': image_binary},
            Attributes=['ALL']
        )
        face_count = len(response['FaceDetails'])
        
        if face_count == 0:
            return {"status": False, "message": "No face detected in the image."}
        if face_count > 1:
            return {"status": False, "message": "More than one face detected in the image."}
            
        return {"status": True, "message": "Face validation successful"}
        
    except Exception as e:
        return {"status": False, "message": str(e)}

# Function 1: Register Face
def Register_Face(user_id, image_path):
    try:
        # Step 1: Load and validate the image
        with open(image_path, 'rb') as file:
            image_binary = file.read()
        validate_face_response = validate_faces(image_binary)
        if not validate_face_response["status"]:
            return validate_face_response["message"]
        
        # Step 2: Save image temporarily
        folder_path = create_user_folder(user_id)
        file_extension = os.path.splitext(image_path)[1]
        temp_image_path = os.path.join(folder_path, f"{user_id}{file_extension}")
        with open(temp_image_path, 'wb') as temp_file:
            temp_file.write(image_binary)

        # Step 3: Upload image to S3
        s3_object = s3.Object(S3_BUCKET, f'index/{user_id}{file_extension}')
        s3_object.put(
            Body=image_binary,
            Metadata={'user_id': user_id}
        )
        print(f"Image registered successfully for user_id: {user_id}")

        # Step 4: Clean up local folder
        delete_user_folder(user_id)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Function 2: Verify Face
def Verify_Face(user_id, image_path):
    try:
        # Step 1: Load and validate the image
        with open(image_path, 'rb') as file:
            image_binary = file.read()
        validate_face_response = validate_faces(image_binary)
        if not validate_face_response["status"]:
            return validate_face_response["message"]
        
        # Step 2: Save image temporarily
        folder_path = create_user_folder(user_id)
        temp_image_path = os.path.join(folder_path, os.path.basename(image_path))
        with open(temp_image_path, 'wb') as temp_file:
            temp_file.write(image_binary)

        # Step 3: Search for face in Rekognition
        response = rekognition.search_faces_by_image(
            CollectionId='payvryusers',
            Image={'Bytes': image_binary}
        )
        if not response['FaceMatches']:
            print("No matching face found.")
            delete_user_folder(user_id)
            return False

        # Step 4: Verify face and fetch user details
        for match in response['FaceMatches']:
            face_id = match['Face']['FaceId']
            confidence = match['Face']['Confidence']
            print(f"Match found with FaceId: {face_id}, Confidence: {confidence}%")

            face_details = dynamodb.get_item(
                TableName='payvryusers_recognition',
                Key={'RekognitionId': {'S': face_id}}
            )

            if 'Item' in face_details and face_details['Item']['user_id']['S'] == user_id:
                print(f"Face verified successfully for user_id: {user_id}")
                return True
            else:
                print(f"No match for user_id: {user_id}")

        # Step 5: Clean up local folder
        delete_user_folder(user_id)
        print(f"The user found: {user_id}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

