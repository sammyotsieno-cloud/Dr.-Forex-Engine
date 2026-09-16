from dataclasses import dataclass, field


@dataclass
class BuildHistory:
    builds: list[dict] = field(default_factory=list)

    def record_build(self, build: dict) -> None:
        self.builds.append(build)

    def get_build(self, index: int) -> dict | None:
        return self.builds[index] if 0 <= index < len(self.builds) else None

    def get_previous_build(self) -> dict | None:
        return self.builds[-2] if len(self.builds) >= 2 else None

    def compare_builds(self, current: dict, previous: dict | None = None) -> dict:
        previous = previous or self.get_previous_build() or {}
        return {"current": current, "previous": previous}

    def find_recurring_failure(self, message: str) -> list[dict]:
        return [build for build in self.builds if message in str(build)]

    def find_regression(self, current_failures: list[str]) -> list[str]:
        previous = self.builds[-2] if len(self.builds) >= 2 else {}
        old = set(previous.get("failures", []))
        return [failure for failure in current_failures if failure not in old]

    def find_fixed_failure(self, current_failures: list[str]) -> list[str]:
        if len(self.builds) < 2:
            return []
        old = set(self.builds[-2].get("failures", []))
        return sorted(old - set(current_failures))

    def get_failure_history(self) -> list[dict]:
        return [build for build in self.builds if build.get("failures")]
