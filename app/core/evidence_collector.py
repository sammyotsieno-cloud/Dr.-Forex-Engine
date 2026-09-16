from pathlib import Path

from app.models.diagnostic import EvidenceBundle


class EvidenceCollector:
    DEFAULT_FILES = (
        "environment.txt",
        "install.log",
        "import-check.log",
        "pytest.log",
        "package-build.log",
    )

    def collect_from_directory(self, directory: str | Path) -> EvidenceBundle:
        root = Path(directory)
        bundle = EvidenceBundle()
        for name in self.DEFAULT_FILES:
            path = root / name
            if path.is_file():
                bundle.add(name, path.read_text(encoding="utf-8", errors="replace"))
        return bundle

    def collect_files(self, files: dict[str, str]) -> EvidenceBundle:
        bundle = EvidenceBundle()
        for name, content in files.items():
            bundle.add(name, content)
        return bundle

    def build_evidence_bundle(self, files: dict[str, str], metadata: dict | None = None) -> EvidenceBundle:
        bundle = self.collect_files(files)
        if metadata:
            bundle.metadata.update(metadata)
        return bundle
