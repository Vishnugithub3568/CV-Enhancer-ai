from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.upload import router as upload_router
from app.parse_resume import router as parse_router
from app.enhance_resume import router as enhance_router
from app.generate_resume import router as generate_router
from app.download_resume import router as download_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(parse_router)
app.include_router(enhance_router)
app.include_router(generate_router)
app.include_router(download_router)

@app.get("/")
def read_root():
    return {"message": "CV Enhancer AI Backend Running"}
