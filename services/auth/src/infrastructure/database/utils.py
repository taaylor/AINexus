def fetch_constraint_name(exc: Exception) -> str | None:
    """Return a database constraint name from a wrapped exception.

    SQLAlchemy stores the original driver exception in ``exc.orig``. Psycopg
    provides the constraint name as ``exc.orig.diag.constraint_name``, which
    is checked first. If that diagnostic is unavailable, this function checks
    ``exc.orig.__cause__.constraint_name``. It returns ``None`` if neither
    location contains a string name.

    Args:
        exc: An exception that may wrap a database driver error.

    Returns:
        The constraint name, or ``None`` when no name is available.

    Examples:
        >>> from types import SimpleNamespace
        >>> from sqlalchemy.exc import IntegrityError
        >>> driver_error = SimpleNamespace(
        ...     diag=SimpleNamespace(constraint_name="uq_users_cred_email")
        ... )
        >>> exc = IntegrityError("insert failed", {}, driver_error)
        >>> fetch_constraint_name(exc)
        'uq_users_cred_email'

        >>> exc = IntegrityError("insert failed", {}, object())
        >>> fetch_constraint_name(exc) is None
        True
    """

    original_error = getattr(exc, "orig", None)
    diagnostic = getattr(original_error, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)

    if isinstance(constraint_name, str):
        return constraint_name

    caused_error = getattr(original_error, "__cause__", None)
    constraint_name = getattr(caused_error, "constraint_name", None)

    return constraint_name if isinstance(constraint_name, str) else None
