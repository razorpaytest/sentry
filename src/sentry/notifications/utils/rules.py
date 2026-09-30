from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from sentry.models.rule import Rule
from sentry.notifications.types import NotificationRule

RuleIdType = Literal["workflow_id", "legacy_rule_id"]


def get_legacy_rule_id(rule: Rule | NotificationRule) -> int | None:
    if isinstance(rule, Rule):
        return rule.id
    return rule.legacy_rule_id


def get_key_from_rule_data(rule: Rule | NotificationRule, key: str) -> str:
    if isinstance(rule, NotificationRule):
        if key == "legacy_rule_id":
            value = rule.legacy_rule_id
        elif key == "workflow_id":
            value = rule.workflow_id
        else:
            raise KeyError(key)
        assert value is not None
        return str(value)

    value = rule.data.get("actions", [{}])[0].get(key)
    assert value is not None
    return value


@dataclass
class RulesAndWorkflows[RuleT: Rule | NotificationRule]:
    rules: list[RuleT]
    workflow_rules: list[RuleT]


def split_rules_by_rule_workflow_id[RuleT: Rule | NotificationRule](
    rules: Sequence[RuleT],
) -> RulesAndWorkflows[RuleT]:
    parsed_rules = []
    workflow_rules = []
    for rule in rules:
        key, _ = get_rule_or_workflow_id(rule)
        match key:
            case "workflow_id":
                workflow_rules.append(rule)
            case "legacy_rule_id":
                parsed_rules.append(rule)
    return RulesAndWorkflows(rules=parsed_rules, workflow_rules=workflow_rules)


def get_rule_or_workflow_id(rule: Rule | NotificationRule) -> tuple[RuleIdType, str]:
    if isinstance(rule, NotificationRule):
        if rule.legacy_rule_id is not None:
            return ("legacy_rule_id", str(rule.legacy_rule_id))
        assert rule.workflow_id is not None
        return ("workflow_id", str(rule.workflow_id))

    try:
        return ("legacy_rule_id", get_key_from_rule_data(rule, "legacy_rule_id"))
    except AssertionError:
        pass

    try:
        return ("workflow_id", get_key_from_rule_data(rule, "workflow_id"))
    except AssertionError:
        return ("legacy_rule_id", str(rule.id))
