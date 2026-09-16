from collections import Counter
import re

from app.models.diagnostic import DiagnosticFailure, RootCause


class RootCauseInvestigator:
    def find_root_causes(self, failures: list[DiagnosticFailure], repository: dict | None = None) -> list[RootCause]:
        if not failures:
            return []
        counts = Counter(f.message for f in failures)
        causes = []
        for message, count in counts.most_common():
            evidence = [f"failure:{failure.failure_type.value}:{failure.location.file or 'unknown'}" for failure in failures if failure.message == message]
            causes.append(RootCause(description=message, evidence=evidence, confidence=min(0.95, 0.5 + 0.1 * (count - 1)), primary=not causes))
        return causes

    def trace_exception_origin(self, failure: DiagnosticFailure) -> str | None:
        return failure.location.file

    def trace_dependency_chain(self, repository: dict, target: str) -> list[str]:
        graph = repository.get("dependencies", {})
        visited: set[str] = set()
        result: list[str] = []

        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            result.append(node)
            for dependency in graph.get(node, []):
                visit(dependency)

        visit(target)
        return result

    def correlate_failures(self, failures: list[DiagnosticFailure]) -> dict[str, list[DiagnosticFailure]]:
        groups: dict[str, list[DiagnosticFailure]] = {}
        for failure in failures:
            key = failure.location.file or failure.failure_type.value
            groups.setdefault(key, []).append(failure)
        return groups

    def identify_primary_failure(self, failures: list[DiagnosticFailure]) -> DiagnosticFailure | None:
        return failures[0] if failures else None

    def identify_secondary_failures(self, failures: list[DiagnosticFailure]) -> list[DiagnosticFailure]:
        return failures[1:]

    def reject_symptoms_as_causes(self, failures: list[DiagnosticFailure]) -> list[DiagnosticFailure]:
        return [failure for failure in failures if not re.search(r"downstream|follow-up|secondary", failure.message, re.I)]
