import ast
from pathlib import Path


class RepositoryAnalyzer:
    def scan_repository(self, root: str | Path) -> dict:
        root = Path(root)
        files = sorted(str(path.relative_to(root)) for path in root.rglob("*.py") if ".git" not in path.parts and ".venv" not in path.parts)
        modules = {}
        for relative in files:
            path = root / relative
            modules[relative] = self._parse_file(path)
        return {"files": files, "modules": modules, "dependencies": self.build_dependency_graph(modules)}

    def build_file_map(self, root: str | Path) -> dict[str, dict]:
        return self.scan_repository(root)["modules"]

    def parse_python_file(self, path: str | Path) -> dict:
        return self._parse_file(Path(path))

    def extract_functions(self, tree: ast.AST) -> list[str]:
        return [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    def extract_classes(self, tree: ast.AST) -> list[str]:
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    def extract_imports(self, tree: ast.AST) -> list[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return sorted(set(imports))

    def build_dependency_graph(self, modules: dict[str, dict]) -> dict[str, list[str]]:
        return {path: info["imports"] for path, info in modules.items()}

    def identify_entry_points(self, modules: dict[str, dict]) -> list[str]:
        return [path for path, info in modules.items() if path.endswith("main.py") or "if __name__ == '__main__'" in info["source"]]

    def find_related_files(self, modules: dict[str, dict], target: str) -> list[str]:
        normalized = target.replace("/", ".").removesuffix(".py")
        return [path for path, info in modules.items() if normalized in info["imports"] or any(normalized in imp for imp in info["imports"])]

    def _parse_file(self, path: Path) -> dict:
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=str(path))
            return {"source": source, "functions": self.extract_functions(tree), "classes": self.extract_classes(tree), "imports": self.extract_imports(tree)}
        except SyntaxError as exc:
            return {"source": source, "functions": [], "classes": [], "imports": [], "syntax_error": str(exc)}
