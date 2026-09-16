from app.models.intent import ProjectIntent


class ProjectIntentStore:
    DEFAULT_INTENT = ProjectIntent(
        objectives=[
            "systematic strategy research and validation",
            "controlled progression from research to any authorized execution",
        ],
        required_capabilities=[
            "historical research",
            "validation",
            "robustness evaluation",
            "human review",
            "controlled monitoring",
        ],
        protected_capabilities=[
            "explicit human approval before live authority",
            "separation of research and live execution",
        ],
        architectural_constraints=[
            "evidence before belief",
            "validation before live authority",
            "approval must be explicit and revocable",
        ],
    )

    def __init__(self, intent: ProjectIntent | None = None):
        self._intent = intent or self.DEFAULT_INTENT

    def load_project_intent(self) -> ProjectIntent:
        return self._intent

    def get_architectural_constraints(self) -> list[str]:
        return list(self._intent.architectural_constraints)

    def get_required_capabilities(self) -> list[str]:
        return list(self._intent.required_capabilities)

    def get_protected_capabilities(self) -> list[str]:
        return list(self._intent.protected_capabilities)

    def get_dependency_expectations(self) -> dict[str, list[str]]:
        return dict(self._intent.dependency_expectations)

    def compare_with_current_state(self, capabilities: list[str]) -> list[str]:
        current = {item.lower() for item in capabilities}
        return [item for item in self._intent.required_capabilities if item.lower() not in current]

    def record_intent_change(self, intent: ProjectIntent) -> None:
        self._intent = intent
