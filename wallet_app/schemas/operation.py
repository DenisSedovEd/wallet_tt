from enum import Enum


class OperationTypeSchema(str, Enum):
    """
    Схема аннотации видов операций. Позволяет добавить любую необходимую операцию.
    """

    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
