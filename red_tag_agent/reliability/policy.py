from dataclasses import dataclass

from red_tag_agent.models import Incident, Severity


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    allowed: bool
    requires_approval: bool
    reason: str


class ActionPolicy:
    SAFE_ACTIONS = frozenset({"restart", "rollback", "scale_up", "clear_cache"})
    HIGH_RISK_ACTIONS = frozenset({"delete", "drop_database", "rotate_credentials"})

    def evaluate(self, incident: Incident, action: str) -> PolicyDecision:
        normalized = action.strip().lower()
        if normalized in self.HIGH_RISK_ACTIONS:
            return PolicyDecision(
                action=normalized,
                allowed=False,
                requires_approval=True,
                reason="High-risk action is never executed autonomously.",
            )
        if normalized not in self.SAFE_ACTIONS:
            return PolicyDecision(
                action=normalized,
                allowed=False,
                requires_approval=True,
                reason="Action is outside the autonomous execution allowlist.",
            )
        if incident.severity == Severity.SEV1:
            return PolicyDecision(
                action=normalized,
                allowed=False,
                requires_approval=True,
                reason="SEV1 incidents require a human approval checkpoint.",
            )
        return PolicyDecision(
            action=normalized,
            allowed=True,
            requires_approval=False,
            reason="Action is allowlisted for this severity.",
        )
