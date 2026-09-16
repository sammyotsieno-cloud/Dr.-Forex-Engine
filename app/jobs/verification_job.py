class VerificationJob:
    def run_verification(self, checks: list[callable]) -> dict:
        results = []
        for check in checks:
            try:
                value = check()
                results.append({"check": getattr(check, "__name__", str(check)), "passed": bool(value), "result": value})
            except Exception as exc:
                results.append({"check": getattr(check, "__name__", str(check)), "passed": False, "error": str(exc)})
        return {"passed": all(item["passed"] for item in results), "checks": results}

    def compare_before_and_after(self, before: dict, after: dict) -> dict:
        return {"before": before, "after": after, "changed": before != after}

    def evaluate_build_result(self, result: dict) -> bool:
        return bool(result.get("passed"))

    def evaluate_intent_preservation(self, assessment) -> bool:
        return bool(assessment.consistent)

    def produce_verification_report(self, result: dict, intent_preserved: bool = True) -> dict:
        return {"passed": bool(result.get("passed")) and intent_preserved, "build": result, "intent_preserved": intent_preserved}
