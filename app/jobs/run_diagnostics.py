import argparse
import json

from app.core.intent_interpreter import IntentInterpreter
from app.jobs.diagnostic_job import DiagnosticJob


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Dr. Forex Engine self-diagnostics.")
    parser.add_argument("diagnostics", help="Directory containing GitHub Actions diagnostic logs")
    parser.add_argument("--repository", default=".", help="Repository root to inspect")
    parser.add_argument("--intent", default="", help="Current user intention for this diagnostic pass")
    args = parser.parse_args()

    user_intent = IntentInterpreter().interpret(args.intent) if args.intent.strip() else None
    report = DiagnosticJob().run_diagnostic(args.diagnostics, args.repository, user_intent)
    print(json.dumps({
        "confidence": report.confidence,
        "intent_consistent": report.intent_consistent,
        "failures": [failure.message for failure in report.failures],
        "root_causes": [cause.description for cause in report.root_causes],
        "unknowns": report.unknowns,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
