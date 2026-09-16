from app.models.repair import FileChange, RepairProposal


class RepairPlanner:
    def generate_repair_options(self, findings: list[str]) -> list[str]:
        return list(findings)

    def identify_minimal_change(self, affected_files: list[str]) -> list[str]:
        return list(dict.fromkeys(affected_files))

    def identify_required_files(self, root_causes: list[str], repository: dict | None = None) -> list[str]:
        files: list[str] = []
        for cause in root_causes:
            if repository:
                files.extend(path for path, info in repository.get("modules", {}).items() if cause in info.get("source", ""))
        return list(dict.fromkeys(files))

    def identify_required_functions(self, files: list[str], repository: dict | None = None) -> dict[str, list[str]]:
        return {path: repository.get("modules", {}).get(path, {}).get("functions", []) for path in files} if repository else {path: [] for path in files}

    def check_existing_capabilities(self, repository: dict | None = None) -> list[str]:
        return list(repository.get("files", [])) if repository else []

    def avoid_duplicate_implementation(self, existing_functions: dict[str, list[str]], proposed_function: str) -> bool:
        return not any(proposed_function in functions for functions in existing_functions.values())

    def check_dependency_impact(self, affected_files: list[str], dependency_graph: dict[str, list[str]]) -> list[str]:
        return [path for path, deps in dependency_graph.items() if any(dep in affected_files for dep in deps)]

    def build_repair_plan(self, summary: str, files: list[str], evidence: list[str]) -> RepairProposal:
        return RepairProposal(summary=summary, changes=[FileChange(path=path, reason=summary) for path in files], evidence=evidence)
