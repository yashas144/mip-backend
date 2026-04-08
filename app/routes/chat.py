from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.recommendation_service import recommendation_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        # Start background initialization if it has not started yet
        if not recommendation_service.initialized and not recommendation_service.loading:
            recommendation_service.start_background_initialize()

        # If still loading, return a safe warm-up response
        if recommendation_service.loading:
            return {
                "response": "The recommendation engine is warming up. Please try again in a few seconds.",
                "songs": [],
                "evidence": [],
                "grounded": False,
            }

        # If initialization failed earlier, show a helpful error
        if recommendation_service.loading_error:
            raise HTTPException(
                status_code=500,
                detail=f"Initialization failed: {recommendation_service.loading_error}",
            )

        # If not initialized yet, trigger background init and ask user to retry
        if not recommendation_service.initialized:
            recommendation_service.start_background_initialize()
            return {
                "response": "The recommendation engine is starting. Please try again in a few seconds.",
                "songs": [],
                "evidence": [],
                "grounded": False,
            }

        return recommendation_service.recommend(req.message, top_k=5)

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Artifacts missing: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))