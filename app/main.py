from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.services.recommendation_service import recommendation_service

app = FastAPI(title="AI Music Intelligence Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.on_event("startup")
def startup_event():
    # Start loading in background so Azure startup is not blocked
    recommendation_service.start_background_initialize()


@app.get("/")
def root():
    return {"message": "Music AI backend is running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "recommendation_service_initialized": recommendation_service.initialized,
        "recommendation_service_loading": recommendation_service.loading,
        "recommendation_service_error": recommendation_service.loading_error,
    }