import re

from app.models.intent import UserIntent


class IntentInterpreter:
    def interpret(self, request: str | None) -> UserIntent | None:
        """Interpret a refined user intention, preserving multiple requirements."""
        if request is None or not request.strip():
            return None

        statements = self.split_statements(request)
        text = request.strip()
        return UserIntent(
            objective=self.extract_objective(text),
            objectives=self.extract_objectives(statements),
            desired_capabilities=self.extract_required_capabilities(text),
            constraints=self.extract_constraints(text),
            prohibited_changes=self.extract_prohibited_changes(text),
            affected_components=[],
            measurement_criteria=self.extract_measurement_criteria(statements),
            acceptance_criteria=self.extract_acceptance_criteria(statements),
            source_statements=statements,
        )

    def split_statements(self, request: str) -> list[str]:
        statements: list[str] = []
        for line in request.strip().splitlines():
            item = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()
            if not item:
                continue
            parts = re.split(r"\s*;\s*", item)
            statements.extend(part.strip() for part in parts if part.strip())
        if not statements:
            statements = [part.strip() for part in re.split(r"\s*;\s*", request.strip()) if part.strip()]
        return statements

    def extract_objective(self, request: str) -> str:
        objectives = self.extract_objectives(self.split_statements(request))
        return objectives[0] if objectives else request.strip() or "Unspecified objective"

    def extract_objectives(self, statements: list[str]) -> list[str]:
        markers = ("want to", "need to", "aim to", "objective", "improve", "add", "enable", "support", "build", "change", "fix", "preserve", "retain")
        return [statement for statement in statements if any(re.search(rf"\b{re.escape(marker)}\b", statement, re.I) for marker in markers)]

    def extract_constraints(self, request: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"(?:must|should|without|keep|preserve)\s+([^.;\n]+)", request, re.I)]

    def extract_required_capabilities(self, request: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"(?:add|enable|support|retain|preserve)\s+([^.;\n]+)", request, re.I)]

    def extract_prohibited_changes(self, request: str) -> list[str]:
        patterns = (
            r"(?:do not|don't|never|avoid)\s+([^.;\n]+)",
            r"without\s+(?:bypassing|removing|disabling|deleting)\s+([^.;\n]+)",
        )
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(m.group(1).strip() for m in re.finditer(pattern, request, re.I))
        return list(dict.fromkeys(matches))

    def extract_measurement_criteria(self, statements: list[str]) -> list[str]:
        markers = ("measure", "metric", "measured", "threshold", "target", "at least", "at most", "exactly", "equals", "must be")
        return [statement for statement in statements if any(re.search(rf"\b{re.escape(marker)}\b", statement, re.I) for marker in markers)]

    def extract_acceptance_criteria(self, statements: list[str]) -> list[str]:
        markers = ("acceptance", "accepted", "success", "pass", "passes", "must produce", "considered complete", "done when")
        return [statement for statement in statements if any(re.search(rf"\b{re.escape(marker)}\b", statement, re.I) for marker in markers)]

    def identify_affected_components(self, request: str, components: list[str]) -> list[str]:
        text = request.lower()
        return [component for component in components if component.lower() in text]

    def resolve_ambiguity(self, request: str) -> list[str]:
        if not request.strip():
            return ["User intent was not supplied."]
        statements = self.split_statements(request)
        if any(statement.lower() in {"improve", "improve it", "make it better", "fix it"} for statement in statements):
            return ["The intention does not define the target behaviour or how improvement will be measured."]
        return []
