import argparse
import json

from app.jobs.diagnostic_job import DiagnosticJob


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Dr. Forex Engine self-diagnostics.")
    parser.add_argument("diagnostics", help="Directory containing GitHub Actions diagnostic logs")
    parser.add_argument("--repository", default=".", help="Repository root to inspect")
    args = parser.parse_args()

    report = DiagnosticJob().run_diagnostic(args.diagnostics, args.repository)
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
