from app.core.failure_analyzer import FailureAnalyzer
from app.core.intent_consistency import IntentConsistencyAnalyzer
from app.core.project_intent import ProjectIntentStore
from app.core.repository_analyzer import RepositoryAnalyzer
from app.core.root_cause import RootCauseInvestigator
from app.models.diagnostic import DiagnosticFinding, DiagnosticReport, EvidenceBundle
from app.models.intent import UserIntent


class DiagnosticEngine:
    def __init__(self, project_intent: ProjectIntentStore | None = None):
        self.failure_analyzer = FailureAnalyzer()
        self.repository_analyzer = RepositoryAnalyzer()
        self.root_cause = RootCauseInvestigator()
        self.intent_analyzer = IntentConsistencyAnalyzer()
        self.project_intent = project_intent or ProjectIntentStore()

    def diagnose(self, evidence: EvidenceBundle, repository_root: str | None = None, user_intent: UserIntent | None = None) -> DiagnosticReport:
        failures = self.failure_analyzer.analyze(evidence)
        repository = self.repository_analyzer.scan_repository(repository_root) if repository_root else {}
        roots = self.root_cause.find_root_causes(failures, repository)
        findings = [DiagnosticFinding(category="failure", description=f.message, evidence=f.evidence_sources) for f in failures]
        unknowns = []
        if not failures:
            unknowns.append("No recognizable failure was found in the supplied evidence.")
        if user_intent:
            assessment = self.intent_analyzer.check_intent_consistency(user_intent, self.project_intent.load_project_intent(), [])
            consistent = assessment.consistent
        else:
            consistent = True
        confidence = max((cause.confidence for cause in roots), default=0.0)
        return DiagnosticReport(failures=failures, root_causes=roots, findings=findings, intent_consistent=consistent, confidence=confidence, unknowns=unknowns)

    def assemble_evidence(self, evidence: EvidenceBundle) -> EvidenceBundle:
        return evidence

    def build_system_context(self, repository_root: str) -> dict:
        return self.repository_analyzer.scan_repository(repository_root)

    def evaluate_intent(self, user_intent: UserIntent, proposed_changes: list[str]):
        return self.intent_analyzer.check_intent_consistency(user_intent, self.project_intent.load_project_intent(), proposed_changes)

    def produce_diagnostic_report(self, evidence: EvidenceBundle, repository_root: str | None = None, user_intent: UserIntent | None = None) -> DiagnosticReport:
        return self.diagnose(evidence, repository_root, user_intent)
