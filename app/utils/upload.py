import os
import shutil
import uuid
from fastapi import UploadFile

# Define where files will be stored on your server
UPLOAD_DIR = "static/uploads/logos"

# Create the directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_upload_file(upload_file: UploadFile, folder: str = "logos") -> str:
    """
    Saves an uploaded file to the server and returns the relative path.
    """
    # 1. Generate a unique filename to prevent overwriting
    extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{extension}"
    
    # 2. Set the full path
    folder_path = os.path.join("static/uploads", folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    file_path = os.path.join(folder_path, unique_filename)

    # 3. Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    # 4. Return the path to be saved in the Database
    return f"/{file_path}"