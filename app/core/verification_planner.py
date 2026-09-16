from app.models.repair import VerificationPlan


class VerificationPlanner:
    def build_verification_plan(self, affected_files: list[str], intent_checks: list[str] | None = None) -> VerificationPlan:
        checks = ["import check", "pytest", "package build"]
        checks.extend(intent_checks or [])
        checks.extend(f"regression check: {path}" for path in affected_files)
        return VerificationPlan(
            checks=list(dict.fromkeys(checks)),
            success_conditions=["all required checks pass", "no protected capability is lost"],
            failure_conditions=["any required check fails", "intent conflict detected"],
        )

    def identify_required_tests(self, affected_files: list[str]) -> list[str]:
        return [f"tests covering {path}" for path in affected_files]

    def identify_regression_checks(self, affected_files: list[str]) -> list[str]:
        return [f"regression check: {path}" for path in affected_files]

    def identify_intent_checks(self, protected_capabilities: list[str]) -> list[str]:
        return [f"preserve: {capability}" for capability in protected_capabilities]

    def define_success_conditions(self) -> list[str]:
        return ["required build and test checks pass", "no protected capability is lost"]

    def define_failure_conditions(self) -> list[str]:
        return ["required check fails", "intent consistency check fails"]
