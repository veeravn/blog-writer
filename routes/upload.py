# routes/upload.py
import azure.functions as func
import json, os, tempfile, uuid
from function_app import app
from dao.blob_storage import upload_file_to_blob, append_to_blob_batch
from services.preprocess_data import preprocess_to_instruction_format

@app.function_name(name="upload")
@app.route(route="upload", methods=["POST"])
async def upload_and_preprocess(req: func.HttpRequest) -> func.HttpResponse:
    try:
        formdata = await req.form()
        file = formdata.get("file")
        if not file:
            return func.HttpResponse(json.dumps({"error": "Missing file upload."}), status_code=400)

        temp_dir = tempfile.gettempdir()
        file_id = uuid.uuid4()
        temp_path = os.path.join(temp_dir, f"{file_id}-{file.filename}")

        with open(temp_path, "wb") as f:
            f.write(file.file.read())

        upload_file_to_blob("datasets", file.filename, temp_path)
        processed = os.path.join(temp_dir, f"processed-{file_id}.jsonl")
        preprocess_to_instruction_format(temp_path, processed)
        append_to_blob_batch(processed)

        return func.HttpResponse(json.dumps({"status": "success"}), status_code=200)

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
