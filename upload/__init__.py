# azure_functions_app/upload/__init__.py
import azure.functions as func
from services.blob_storage import upload_to_blob
from scripts.preprocess_data import preprocess_to_instruction_format
import os
import tempfile
import uuid
import json

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        formdata = await req.form()
        file = formdata.get("file")

        if not file:
            return func.HttpResponse(
                json.dumps({"error": "Missing file upload."}),
                status_code=400,
                mimetype="application/json"
            )

        # Save to a temporary location
        temp_dir = tempfile.gettempdir()
        temp_filename = f"{uuid.uuid4()}-{file.filename}"
        temp_path = os.path.join(temp_dir, temp_filename)

        with open(temp_path, "wb") as f:
            f.write(file.file.read())

        # Upload to blob storage
        upload_to_blob(temp_path, temp_filename)

        # Preprocess and convert to instruction format
        preprocess_to_instruction_format(temp_path)

        return func.HttpResponse(
            json.dumps({"status": "success", "filename": temp_filename}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
