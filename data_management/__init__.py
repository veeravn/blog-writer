import azure.functions as func
from services.blob_storage import delete_dataset

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="delete_dataset")
@app.route(route="dataset/{filename}", methods=["DELETE"])
def delete_dataset_func(req: func.HttpRequest, filename: str) -> func.HttpResponse:
    try:
        delete_dataset(filename)
        return func.HttpResponse(f"Deleted {filename}", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error deleting file: {str(e)}", status_code=500)
