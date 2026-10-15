from enum import StrEnum, unique


@unique
class IsolationLevel(StrEnum):
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"
