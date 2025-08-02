import azure.functions as func
from dao.blob_storage import delete_dataset

def main(req: func.HttpRequest) -> func.HttpResponse:
    filename = req.route_params.get("filename")
    try:
        delete_dataset(filename)
        return func.HttpResponse(f"Deleted {filename}", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error deleting file: {str(e)}", status_code=500)
