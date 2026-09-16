from app.models.intent import IntentAssessment, ProjectIntent, UserIntent


class IntentConsistencyAnalyzer:
    def check_intent_consistency(self, user_intent: UserIntent, project_intent: ProjectIntent, proposed_changes: list[str]) -> IntentAssessment:
        text = " ".join(proposed_changes).lower()
        prohibited = [item for item in user_intent.prohibited_changes if item.lower() in text]
        protected = [item for item in project_intent.protected_capabilities if self._conflicts_with(item, text)]
        conflicts = prohibited + protected
        return IntentAssessment(
            consistent=not conflicts,
            conflicts=conflicts,
            architectural_violations=protected,
            capability_loss=[],
            scope_creep=[],
            preserved_intentions=[item for item in user_intent.desired_capabilities if item.lower() not in text],
        )

    def compare_proposed_change_to_intent(self, user_intent: UserIntent, proposed_changes: list[str]) -> IntentAssessment:
        text = " ".join(proposed_changes).lower()
        conflicts = [item for item in user_intent.prohibited_changes if item.lower() in text]
        return IntentAssessment(consistent=not conflicts, conflicts=conflicts)

    def detect_capability_loss(self, current_capabilities: list[str], proposed_capabilities: list[str]) -> list[str]:
        proposed = {item.lower() for item in proposed_capabilities}
        return [item for item in current_capabilities if item.lower() not in proposed]

    def detect_architectural_violation(self, project_intent: ProjectIntent, proposed_changes: list[str]) -> list[str]:
        text = " ".join(proposed_changes).lower()
        return [item for item in project_intent.architectural_constraints if self._conflicts_with(item, text)]

    def detect_scope_creep(self, user_intent: UserIntent, proposed_changes: list[str]) -> list[str]:
        objective_terms = set(user_intent.objective.lower().split())
        return [change for change in proposed_changes if not objective_terms.intersection(change.lower().split())]

    @staticmethod
    def _conflicts_with(protected_item: str, text: str) -> bool:
        # Conservative default: only explicit removal/disable wording is considered a conflict.
        key_terms = [word for word in protected_item.lower().split() if len(word) > 4]
        return any(re.search(pattern, text) for word in key_terms for pattern in (rf"remove\s+\w*{word}", rf"disable\s+\w*{word}", rf"bypass\s+\w*{word}"))
