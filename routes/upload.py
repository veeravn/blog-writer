from fastapi import APIRouter, UploadFile, File, HTTPException
from services.storage import save_to_temp
from scripts.preprocess_user_data import preprocess_and_upload

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        temp_path = save_to_temp(file)
        preprocess_and_upload(temp_path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
