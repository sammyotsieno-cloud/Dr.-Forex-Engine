from fastapi import APIRouter

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/health")
def diagnostic_health() -> dict:
    return {"status": "available"}
