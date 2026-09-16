from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.core.diagnostic_engine import DiagnosticEngine
from app.core.evidence_collector import EvidenceCollector
from app.core.intent_interpreter import IntentInterpreter

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
_engine = DiagnosticEngine()
_collector = EvidenceCollector()
_interpreter = IntentInterpreter()


@router.get("/health")
def diagnostic_health() -> dict:
    return {"status": "available"}


@router.get("/latest")
def get_latest_diagnostic(diagnostics_directory: str = Query("diagnostics")) -> dict:
    path = Path(diagnostics_directory)
    if not path.is_dir():
        raise HTTPException(status_code=404, detail="Diagnostics directory not found")
    report = _engine.diagnose(_collector.collect_from_directory(path), ".")
    return {
        "confidence": report.confidence,
        "intent_consistent": report.intent_consistent,
        "failures": [failure.__dict__ for failure in report.failures],
        "root_causes": [cause.__dict__ for cause in report.root_causes],
        "unknowns": report.unknowns,
    }


@router.post("/analyze")
def trigger_diagnosis(request: str, diagnostics_directory: str = "diagnostics") -> dict:
    path = Path(diagnostics_directory)
    if not path.is_dir():
        raise HTTPException(status_code=404, detail="Diagnostics directory not found")
    intent = _interpreter.interpret(request)
    report = _engine.diagnose(_collector.collect_from_directory(path), ".", intent)
    return {
        "confidence": report.confidence,
        "intent_consistent": report.intent_consistent,
        "failures": [failure.__dict__ for failure in report.failures],
        "root_causes": [cause.__dict__ for cause in report.root_causes],
        "unknowns": report.unknowns,
    }
