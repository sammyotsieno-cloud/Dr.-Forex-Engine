from dataclasses import dataclass, field


@dataclass
class DiagnosticMemory:
    diagnostics: list[dict] = field(default_factory=list)
    repairs: list[dict] = field(default_factory=list)

    def save_diagnostic(self, diagnostic: dict) -> None:
        self.diagnostics.append(diagnostic)

    def load_diagnostic(self, index: int = -1) -> dict | None:
        if not self.diagnostics:
            return None
        return self.diagnostics[index]

    def save_root_cause(self, root_cause: dict) -> None:
        self.save_diagnostic({"type": "root_cause", **root_cause})

    def load_previous_root_causes(self) -> list[dict]:
        return [item for item in self.diagnostics if item.get("type") == "root_cause"]

    def save_repair_result(self, result: dict) -> None:
        self.repairs.append(result)

    def find_similar_diagnoses(self, description: str) -> list[dict]:
        terms = set(description.lower().split())
        return [item for item in self.diagnostics if terms.intersection(str(item.get("description", "")).lower().split())]

    def find_previous_solution(self, failure: str) -> list[dict]:
        return [item for item in self.repairs if failure.lower() in str(item).lower()]
