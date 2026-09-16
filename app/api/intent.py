from fastapi import APIRouter

router = APIRouter(prefix="/intent", tags=["intent"])


@router.get("/health")
def intent_health() -> dict:
    return {"status": "available"}
