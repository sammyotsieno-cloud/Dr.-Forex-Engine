import subprocess


class ChangeAnalyzer:
    def compare_commits(self, base: str, head: str, root: str = ".") -> str:
        result = subprocess.run(["git", "diff", "--name-status", base, head], cwd=root, capture_output=True, text=True, check=False)
        return result.stdout

    def identify_changed_files(self, diff: str) -> list[str]:
        return [line.split("\t", 1)[-1] for line in diff.splitlines() if line.strip()]

    def identify_changed_functions(self, diff: str) -> list[str]:
        return [line.strip()[1:].strip() for line in diff.splitlines() if line.startswith("+") and "def " in line]

    def identify_changed_dependencies(self, diff: str) -> list[str]:
        return [line.strip()[1:].strip() for line in diff.splitlines() if line.startswith("+") and (line.lstrip("+").startswith("import ") or line.lstrip("+").startswith("from "))]

    def correlate_changes_with_failures(self, changed_files: list[str], failures: list[str]) -> dict:
        return {failure: [path for path in changed_files if path in failure] for failure in failures}

    def detect_regression(self, current_failures: list[str], previous_failures: list[str]) -> list[str]:
        return sorted(set(current_failures) - set(previous_failures))
