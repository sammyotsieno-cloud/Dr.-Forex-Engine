import re

from app.models.intent import UserIntent


class IntentInterpreter:
    def interpret(self, request: str | None) -> UserIntent | None:
        """Interpret current user intent, returning None when no intent was supplied."""
        if request is None or not request.strip():
            return None

        text = request.strip()
        return UserIntent(
            objective=self.extract_objective(text),
            desired_capabilities=self.extract_required_capabilities(text),
            constraints=self.extract_constraints(text),
            prohibited_changes=self.extract_prohibited_changes(text),
        )

    def extract_objective(self, request: str) -> str:
        text = request.strip()
        return text or "Unspecified objective"

    def extract_constraints(self, request: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"(?:must|should|without|keep|preserve)\s+([^.;]+)", request, re.I)]

    def extract_required_capabilities(self, request: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"(?:add|enable|support|retain|preserve)\s+([^.;]+)", request, re.I)]

    def extract_prohibited_changes(self, request: str) -> list[str]:
        patterns = (
            r"(?:do not|don't|never|avoid)\s+([^.;]+)",
            r"without\s+(?:bypassing|removing|disabling|deleting)\s+([^.;]+)",
        )
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(m.group(1).strip() for m in re.finditer(pattern, request, re.I))
        return list(dict.fromkeys(matches))

    def identify_affected_components(self, request: str, components: list[str]) -> list[str]:
        text = request.lower()
        return [component for component in components if component.lower() in text]

    def resolve_ambiguity(self, request: str) -> list[str]:
        return ["User intent was not supplied."] if not request.strip() else []
