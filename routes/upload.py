from fastapi import APIRouter, UploadFile, File, HTTPException
from services.blob_storage import save_to_temp, upload_file
from scripts.preprocess_data import preprocess_to_instruction_format
from datetime import datetime
import os

router = APIRouter()

@router.post("/")
async def upload_file_to_blob(file: UploadFile = File(...)):
    try:
        # Step 1: Save to temp
        temp_path = save_to_temp(file)

        # Step 2: Create timestamped blob filename
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"uploads/{timestamp}_{file.filename}"

        # Step 3: Upload to blob storage
        upload_file(temp_path, filename)

        # Step 4: Run preprocessing (fine-tuning prep)
        preprocess_to_instruction_format(temp_path)

        # Optional cleanup
        os.remove(temp_path)

        return {"status": "success", "blob_path": filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

