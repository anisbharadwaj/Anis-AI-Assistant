"""Simple permission rules.
Medium and high risk operations require explicit confirmation.
"""


def requires_confirmation(permission_level: str) -> bool:
    level = (permission_level or "low").lower()
    return level in ("medium", "high")
