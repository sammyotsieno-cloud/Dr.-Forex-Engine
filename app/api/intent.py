from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.intent_interpreter import IntentInterpreter
from app.core.project_intent import ProjectIntentStore
from app.models.intent import UserIntent

router = APIRouter(prefix="/intent", tags=["intent"])
_interpreter = IntentInterpreter()
_project = ProjectIntentStore()
_current: UserIntent | None = None


class IntentRequest(BaseModel):
    request: str = Field(min_length=1)


@router.post("")
def set_user_intent(payload: IntentRequest) -> dict:
    global _current
    _current = _interpreter.interpret(payload.request)
    return {"intent": _current.__dict__}


@router.get("")
def get_current_intent() -> dict:
    return {"intent": _current.__dict__ if _current else None}


@router.get("/project")
def get_project_intent() -> dict:
    return {"intent": _project.load_project_intent().__dict__}


@router.get("/health")
def intent_health() -> dict:
    return {"status": "available"}
