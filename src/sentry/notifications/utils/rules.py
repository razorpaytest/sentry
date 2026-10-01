from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from sentry.models.rule import Rule
from sentry.notifications.types import NotificationRule

RuleIdType = Literal["workflow_id", "legacy_rule_id"]


@dataclass
class RulesAndWorkflows:
    rules: list[NotificationRule]
    workflow_rules: list[NotificationRule]


def split_rules_by_rule_workflow_id(
    rules: Sequence[Rule | NotificationRule],
) -> RulesAndWorkflows:
    parsed_rules = []
    workflow_rules = []
    for rule in rules:
        if isinstance(rule, Rule):
            rule = NotificationRule.from_deprecated_legacy_rule(rule)
        key, _ = get_rule_or_workflow_id(rule)
        match key:
            case "workflow_id":
                workflow_rules.append(rule)
            case "legacy_rule_id":
                parsed_rules.append(rule)
    return RulesAndWorkflows(rules=parsed_rules, workflow_rules=workflow_rules)


def get_rule_or_workflow_id(rule: NotificationRule) -> tuple[RuleIdType, str]:
    if rule.legacy_rule_id is not None:
        return ("legacy_rule_id", str(rule.legacy_rule_id))
    assert rule.workflow_id is not None
    return ("workflow_id", str(rule.workflow_id))
