from pydantic_core import ValidationError

from src.apps.platform_rules.mappers import RULE_DATA_SCHEMAS


def validate_rule_data(key: str, data: dict):
    schema = RULE_DATA_SCHEMAS.get(key)
    if not schema:
        raise ValueError(f"Unsupported rule key: {key}.")
    try:
        return schema(**data)
    except ValidationError as err:
        raise ValueError(f"Invalid data for rule '{key}': {err}.")
