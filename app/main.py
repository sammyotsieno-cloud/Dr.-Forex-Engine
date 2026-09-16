"""FastAPI application entry point."""

from fastapi import FastAPI

from app import __version__
from app.api.diagnostics import router as diagnostics_router
from app.api.intent import router as intent_router

app = FastAPI(
    title="Dr. Forex Engine",
    description=(
        "Quantitative research and controlled execution engine "
        "for systematic Forex strategy development."
    ),
    version=__version__,
)

app.include_router(diagnostics_router)
app.include_router(intent_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the current API health status."""
    return {
        "status": "ok",
        "service": "dr-forex-engine",
        "version": __version__,
    }
