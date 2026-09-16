import re

from app.models.intent import UserIntent


class IntentInterpreter:
    def interpret(self, request: str) -> UserIntent:
        text = request.strip()
        objective = text or "Unspecified objective"
        constraints = self.extract_constraints(text)
        desired = self.extract_required_capabilities(text)
        prohibited = self.extract_prohibited_changes(text)
        return UserIntent(objective=objective, desired_capabilities=desired, constraints=constraints, prohibited_changes=prohibited)

    def extract_objective(self, request: str) -> str:
        text = request.strip()
        return text or "Unspecified objective"

    def extract_constraints(self, request: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"(?:must|should|without|keep|preserve)\s+([^.;]+)", request, re.I)]

    def extract_required_capabilities(self, request: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"(?:add|enable|support|retain|preserve)\s+([^.;]+)", request, re.I)]

    def extract_prohibited_changes(self, request: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"(?:do not|don't|never|avoid)\s+([^.;]+)", request, re.I)]

    def identify_affected_components(self, request: str, components: list[str]) -> list[str]:
        text = request.lower()
        return [component for component in components if component.lower() in text]

    def resolve_ambiguity(self, request: str) -> list[str]:
        return ["User intent contains no explicit objective."] if not request.strip() else []
