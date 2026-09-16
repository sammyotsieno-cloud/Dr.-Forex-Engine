from app.core.failure_analyzer import FailureAnalyzer
from app.core.intent_consistency import IntentConsistencyAnalyzer
from app.core.project_intent import ProjectIntentStore
from app.core.repository_analyzer import RepositoryAnalyzer
from app.core.repair_planner import RepairPlanner
from app.core.root_cause import RootCauseInvestigator
from app.core.verification_planner import VerificationPlanner
from app.models.diagnostic import DiagnosticFinding, DiagnosticReport, EvidenceBundle
from app.models.intent import UserIntent


class DiagnosticEngine:
    def __init__(self, project_intent: ProjectIntentStore | None = None):
        self.failure_analyzer = FailureAnalyzer()
        self.repository_analyzer = RepositoryAnalyzer()
        self.root_cause = RootCauseInvestigator()
        self.intent_analyzer = IntentConsistencyAnalyzer()
        self.repair_planner = RepairPlanner()
        self.verification_planner = VerificationPlanner()
        self.project_intent = project_intent or ProjectIntentStore()

    def diagnose(self, evidence: EvidenceBundle, repository_root: str | None = None, user_intent: UserIntent | None = None) -> DiagnosticReport:
        failures = self.failure_analyzer.analyze(evidence)
        repository = self.repository_analyzer.scan_repository(repository_root) if repository_root else {}
        roots = self.root_cause.find_root_causes(failures, repository)
        findings = [DiagnosticFinding(category="failure", description=f.message, evidence=f.evidence_sources) for f in failures]
        unknowns = []
        if not failures:
            unknowns.append("No recognizable failure was found in the supplied evidence.")

        project_intent = self.project_intent.load_project_intent()
        consistent = True
        if user_intent:
            assessment = self.intent_analyzer.check_intent_consistency(user_intent, project_intent, [])
            consistent = assessment.consistent

        affected_files = list(dict.fromkeys(
            failure.location.file for failure in failures if failure.location.file
        ))
        if roots and affected_files:
            proposal = self.repair_planner.build_repair_plan(
                "Investigate the identified root cause before applying a minimal repair.",
                affected_files,
                [item for root in roots for item in root.evidence],
            )
            proposed_descriptions = [change.reason for change in proposal.changes]
            if user_intent:
                assessment = self.intent_analyzer.check_intent_consistency(user_intent, project_intent, proposed_descriptions)
                proposal.intent_preserved = assessment.consistent
                if not assessment.consistent:
                    unknowns.extend(assessment.conflicts)
            verification = self.verification_planner.build_verification_plan(
                affected_files,
                self.verification_planner.identify_intent_checks(project_intent.protected_capabilities),
            )
        else:
            proposal = None
            verification = None

        confidence = max((cause.confidence for cause in roots), default=0.0)
        return DiagnosticReport(
            failures=failures,
            root_causes=roots,
            findings=findings,
            intent_consistent=consistent,
            confidence=confidence,
            unknowns=unknowns,
            repair_proposal=proposal,
            verification_plan=verification,
        )

    def assemble_evidence(self, evidence: EvidenceBundle) -> EvidenceBundle:
        return evidence

    def build_system_context(self, repository_root: str) -> dict:
        return self.repository_analyzer.scan_repository(repository_root)

    def evaluate_intent(self, user_intent: UserIntent, proposed_changes: list[str]):
        return self.intent_analyzer.check_intent_consistency(user_intent, self.project_intent.load_project_intent(), proposed_changes)

    def produce_diagnostic_report(self, evidence: EvidenceBundle, repository_root: str | None = None, user_intent: UserIntent | None = None) -> DiagnosticReport:
        return self.diagnose(evidence, repository_root, user_intent)
