from app.core.diagnostic_engine import DiagnosticEngine
from app.core.evidence_collector import EvidenceCollector
from app.core.failure_analyzer import FailureAnalyzer
from app.core.intent_consistency import IntentConsistencyAnalyzer
from app.core.intent_interpreter import IntentInterpreter
from app.core.project_intent import ProjectIntentStore
from app.models.diagnostic import EvidenceBundle, FailureType


def test_failure_analyzer_classifies_import_failure():
    analyzer = FailureAnalyzer()
    assert analyzer.classify_failure("import-check.log", "ModuleNotFoundError: missing") == FailureType.IMPORT


def test_failure_analyzer_preserves_import_exception_marker_through_analysis():
    analyzer = FailureAnalyzer()
    bundle = EvidenceBundle(files={"import-check.log": "ModuleNotFoundError: missing_module"})
    failures = analyzer.analyze(bundle)
    assert failures
    assert failures[0].message == "ModuleNotFoundError: missing_module"
    assert failures[0].failure_type == FailureType.IMPORT


def test_repository_analyzer_parses_project():
    from app.core.repository_analyzer import RepositoryAnalyzer
    result = RepositoryAnalyzer().scan_repository(".")
    assert "app/main.py" in result["files"]
    assert "app/main.py" in result["modules"]


def test_intent_interpreter_preserves_constraints():
    intent = IntentInterpreter().interpret("Add research without bypassing human approval")
    assert intent is not None
    assert intent.objective.startswith("Add research")
    assert intent.prohibited_changes


def test_intent_interpreter_recognizes_absent_intent():
    assert IntentInterpreter().interpret(None) is None
    assert IntentInterpreter().interpret("") is None
    assert IntentInterpreter().interpret("   ") is None


def test_intent_interpreter_recognizes_multiple_refined_intentions():
    request = """
    1. Improve the research engine.
    2. Preserve historical validation.
    3. Add robustness testing.
    4. Do not bypass human approval.
    5. Keep research separate from live execution.
    6. Measurement target: at least 500 candidate configurations.
    7. Acceptance: all required validation checks pass.
    """
    intent = IntentInterpreter().interpret(request)
    assert intent is not None
    assert len(intent.source_statements) == 7
    assert len(intent.objectives) >= 5
    assert any("500 candidate configurations" in item for item in intent.measurement_criteria)
    assert any("all required validation checks pass" in item for item in intent.acceptance_criteria)
    assert intent.prohibited_changes


def test_intent_interpreter_identifies_undefined_improvement_measurement():
    interpreter = IntentInterpreter()
    assert interpreter.resolve_ambiguity("Improve the research engine.")


def test_intent_consistency_detects_explicit_bypass():
    user = IntentInterpreter().interpret("Improve research")
    project = ProjectIntentStore().load_project_intent()
    assessment = IntentConsistencyAnalyzer().check_intent_consistency(user, project, ["bypass human approval before live authority"])
    assert not assessment.consistent


def test_intent_consistency_treats_missing_intent_as_neutral():
    project = ProjectIntentStore().load_project_intent()
    assessment = IntentConsistencyAnalyzer().check_intent_consistency(None, project, [])
    assert assessment.consistent
    assert not assessment.conflicts


def test_diagnostic_engine_produces_report():
    evidence = EvidenceBundle(files={"import-check.log": "ModuleNotFoundError: missing_module"})
    report = DiagnosticEngine().diagnose(evidence)
    assert report.failures
    assert report.failures[0].failure_type == FailureType.IMPORT
    assert report.root_causes


def test_diagnostic_engine_runs_without_user_intent():
    evidence = EvidenceBundle(files={"import-check.log": "ModuleNotFoundError: missing_module"})
    report = DiagnosticEngine().diagnose(evidence, user_intent=None)
    assert report.failures
    assert report.intent_consistent
    assert any("No current user intention was supplied" in finding.description for finding in report.findings)


def test_evidence_collector_reads_known_files(tmp_path):
    (tmp_path / "pytest.log").write_text("1 passed", encoding="utf-8")
    bundle = EvidenceCollector().collect_from_directory(tmp_path)
    assert bundle.files["pytest.log"] == "1 passed"
