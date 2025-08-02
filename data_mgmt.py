import azure.functions as func
import logging
import json
from dao.blob_storage import list_blob_files  # You must implement this helper

# Set up Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="data-mgmt/list", methods=["GET"])
def list_all_files(req: func.HttpRequest) -> func.HttpResponse:
    """
    List all files in the datasets and batch containers.
    You can add ?container=datasets or ?container=batch to filter.
    """
    try:
        container = req.params.get("container", "datasets")  # default to 'datasets'
        files = list_blob_files(container)
        return func.HttpResponse(
            json.dumps({"files": files}),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Error listing files")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )

@app.route(route="data-mgmt/batch", methods=["GET"])
def list_batch_files(req: func.HttpRequest) -> func.HttpResponse:
    """
    List all batch files (e.g., new_data.jsonl, archived batches) in the 'batch' container.
    """
    try:
        files = list_blob_files("batch")
        return func.HttpResponse(
            json.dumps({"files": files}),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Error listing batch files")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )
