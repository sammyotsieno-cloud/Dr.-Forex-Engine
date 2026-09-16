import re

from app.models.diagnostic import DiagnosticFailure, EvidenceBundle, FailureLocation, FailureType


class FailureAnalyzer:
    _location = re.compile(r"(?P<file>[A-Za-z0-9_./-]+\.py)(?::(?P<line>\d+))?")

    def analyze(self, bundle: EvidenceBundle) -> list[DiagnosticFailure]:
        failures: list[DiagnosticFailure] = []
        for name, content in bundle.files.items():
            failures.extend(self._analyze_log(name, content))
        return self._deduplicate(failures)

    def classify_failure(self, source: str, message: str) -> FailureType:
        text = f"{source}\n{message}".lower()
        if "pip install" in text or "could not find a version" in text or "metadata-generation-failed" in text:
            return FailureType.INSTALLATION
        if "importerror" in text or "modulenotfounderror" in text or "import check" in text:
            return FailureType.IMPORT
        if "pytest" in text or "failed" in text and ("test" in text or "assert" in text):
            return FailureType.TEST
        if "python -m build" in text or "package build" in text or "buildexception" in text:
            return FailureType.PACKAGE
        return FailureType.UNKNOWN

    def extract_error_messages(self, content: str) -> list[str]:
        patterns = (
            r"(?:ERROR|Error|E)[: ]+(.+)",
            r"((?:ImportError|ModuleNotFoundError|SyntaxError|TypeError|ValueError|AssertionError):\s*.+)",
        )
        messages: list[str] = []
        for pattern in patterns:
            messages.extend(match.group(1).strip() for match in re.finditer(pattern, content))
        return messages

    def identify_first_failure(self, content: str) -> str | None:
        messages = self.extract_error_messages(content)
        return messages[0] if messages else None

    def _analyze_log(self, source: str, content: str) -> list[DiagnosticFailure]:
        messages = self.extract_error_messages(content)
        result: list[DiagnosticFailure] = []
        for message in messages:
            location = self._extract_location(content, message)
            result.append(DiagnosticFailure(
                failure_type=self.classify_failure(source, message),
                message=message,
                location=location,
                evidence_sources=[source],
            ))
        return result

    def _extract_location(self, content: str, message: str) -> FailureLocation:
        position = content.find(message)
        prefix = content[max(0, position - 500):position] if position >= 0 else content
        matches = list(self._location.finditer(prefix))
        if not matches:
            return FailureLocation()
        match = matches[-1]
        return FailureLocation(
            file=match.group("file"),
            line=int(match.group("line")) if match.group("line") else None,
        )

    @staticmethod
    def _deduplicate(failures: list[DiagnosticFailure]) -> list[DiagnosticFailure]:
        seen: set[tuple] = set()
        result: list[DiagnosticFailure] = []
        for failure in failures:
            key = (failure.failure_type, failure.message, failure.location.file, failure.location.line)
            if key not in seen:
                seen.add(key)
                result.append(failure)
        return result
