import azure.functions as func
from dao.blob_storage import upload_to_blob, append_to_blob_batch
from services.preprocess_data import preprocess_to_instruction_format
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

        # Save uploaded file to a temporary location
        temp_dir = tempfile.gettempdir()
        temp_filename = f"{uuid.uuid4()}-{file.filename}"
        temp_path = os.path.join(temp_dir, temp_filename)

        with open(temp_path, "wb") as f:
            f.write(file.file.read())

        # Optional: Upload the raw file to blob storage for audit/logs
        upload_to_blob(temp_path, temp_filename)

        # Preprocess to another temp file (in instruction format)
        instruction_file = os.path.join(temp_dir, f"processed-{uuid.uuid4()}.jsonl")
        preprocess_to_instruction_format(temp_path, instruction_file)

        # Append the processed file to the batch blob (new_data.jsonl)
        append_to_blob_batch(instruction_file)

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
