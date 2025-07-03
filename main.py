from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.generate import router as generate_router
from routes.upload import router as upload_router
from routes.revise_post import router as revise_router
from routes.history import router as history_router
from routes.data_management import router as data_router

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "healthy"}

@app.post("/score")
def score(data: dict):
    return {"result": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router, prefix="/generate")
app.include_router(upload_router, prefix="/upload")
app.include_router(revise_router, prefix="/revise")
app.include_router(history_router, prefix="/history")
app.include_router(data_router, prefix="/data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=False)