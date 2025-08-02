# function_app.py
import azure.functions as func

app = func.FunctionApp()

# Import all route modules (these must reference the global 'app')
from routes import blog_post, data_mgmt, history, preferences, revise, upload, versioning
# Ensure all routes are registered

@app.on_startup()
def show_registered():
    print("Registered functions:")
    for f in app._function_builders:
        print(f"  - {f.name}")
