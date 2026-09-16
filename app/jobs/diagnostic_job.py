from app.core.diagnostic_engine import DiagnosticEngine
from app.core.evidence_collector import EvidenceCollector
from app.models.intent import UserIntent


class DiagnosticJob:
    def __init__(self, engine: DiagnosticEngine | None = None):
        self.engine = engine or DiagnosticEngine()
        self.collector = EvidenceCollector()

    def run_diagnostic(self, diagnostics_directory: str, repository_root: str | None = None, user_intent: UserIntent | None = None):
        evidence = self.collector.collect_from_directory(diagnostics_directory)
        return self.engine.diagnose(evidence, repository_root, user_intent)

    def load_latest_build(self, diagnostics_directory: str):
        return self.collector.collect_from_directory(diagnostics_directory)

    def collect_evidence(self, files: dict[str, str]):
        return self.collector.collect_files(files)

    def run_diagnosis(self, evidence, repository_root: str | None = None, user_intent: UserIntent | None = None):
        return self.engine.diagnose(evidence, repository_root, user_intent)
