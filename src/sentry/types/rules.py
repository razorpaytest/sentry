from dataclasses import dataclass


@dataclass
class NotificationRuleDetails:
    """
    Dataclass to pass around rule details.
    """

    id: int
    label: str
    status_url: str
