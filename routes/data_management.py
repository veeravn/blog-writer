from fastapi import APIRouter
from services.blob_storage import delete_dataset

router = APIRouter()

@router.delete("/dataset/{filename}")
async def delete_dataset_route(filename: str):
    delete_dataset(filename)
    return {"message": f"Deleted {filename}"}
