def ensure_has_primary(items, field="is_primary"):
    """
    Checks that at least one dict in items has field==True.
    Raises ValueError if not.
    """
    if not any(getattr(item, field, False) for item in items):
        raise ValueError(f"At least one item must have {field}=True.")

    return items
