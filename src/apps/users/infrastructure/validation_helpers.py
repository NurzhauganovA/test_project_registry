from typing import Any, Dict, List, Optional, Tuple, Type, Union

from src.core.i18n import _


def validate_user_client_roles(client_roles: list) -> list:
    if not isinstance(client_roles, list):
        raise ValueError(_("Client roles must be provided as a list."))
    if len(client_roles) != len(set(client_roles)):
        raise ValueError(_("Duplicate roles are not allowed."))

    return client_roles.copy()


def validate_profile_dict_field(
    field: Dict[str, Any],
    allowed_keys: List[str],
    types_map: Optional[Dict[str, Union[Type, tuple]]] = None,
) -> None:
    """
    Validates that the provided field is a dictionary with allowed keys and values of the correct types.
    By default, all values are checked to be bool unless a custom type is specified in types_map.

    Args:
        field (dict): Field to validate.
        allowed_keys (list): List of allowed keys for the field.
        types_map (dict, optional): Mapping key -> expected type (e.g., str, int, bool, or tuple of types).

    Raises:
        ValueError: If a field is not a dict, contains disallowed keys, or values are of the wrong type.
    """
    if not isinstance(field, dict):
        raise ValueError(f"Profile field must be dict, not {type(field).__name__}")

    for key, value in field.items():
        if key not in allowed_keys:
            raise ValueError(
                f"Invalid key '{key}' in profile data. Allowed keys are: {allowed_keys}"
            )

        expected_type: Union[Type[Any], Tuple[Type[Any], ...]] = bool
        if types_map is not None:
            expected_type = types_map.get(key, bool)

        if not isinstance(value, expected_type) and value is not None:
            if isinstance(expected_type, tuple):
                expected_names = ", ".join([t.__name__ for t in expected_type])
            else:
                expected_names = expected_type.__name__
            raise ValueError(
                f"Value for key '{key}' must be of type {expected_names}, not {type(value).__name__}"
            )
