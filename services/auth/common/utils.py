from datetime import UTC, datetime


def datetime_with_tz() -> datetime:
    return datetime.now(tz=UTC)
