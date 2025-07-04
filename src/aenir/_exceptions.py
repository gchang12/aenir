"""
"""

import enum

class UnitNotFoundError(BaseException):
    """
    """

    class UnitType(enum.Enum):
        """
        """
        NORMAL = enum.auto()
        FATHER = enum.auto()

    def __init__(self, msg, *, unit_type):
        """
        """
        super().__init__(msg)
        self.unit_type = unit_type

class InitError(BaseException):
    """
    """

    class MissingValue(enum.Enum):
        """
        """
        LYN_MODE = enum.auto()
        HARD_MODE = enum.auto()

    def __init__(self, msg, *, missing_value):
        """
        """
        super().__init__(msg)
        self.missing_value = missing_value

class LevelUpError(BaseException):
    """
    """

class PromotionError(BaseException):
    """
    """

    class Reason(enum.Enum):
        """
        """
        NO_PROMOTIONS = enum.auto()
        LEVEL_TOO_LOW = enum.auto()
        INVALID_PROMOTION = enum.auto()

    def __init__(self, msg, *, reason):
        """
        """
        super().__init__(msg)
        self.reason = reason

class _ItemException(BaseException):
    """
    """

    def __init__(self, msg, *, reason):
        """
        """
        super().__init__(msg)
        self.reason = reason

class StatBoosterError(_ItemException):
    """
    """

    class Reason(enum.Enum):
        """
        """
        NO_IMPLEMENTATION = enum.auto()
        NOT_FOUND = enum.auto()
        STAT_IS_MAXED = enum.auto()

class ScrollError(_ItemException):
    """
    """

    class Reason(enum.Enum):
        """
        """
        NOT_EQUIPPED = enum.auto()
        ALREADY_EQUIPPED = enum.auto()
        NOT_FOUND = enum.auto()
        NO_INVENTORY_SPACE = enum.auto()

class GrowthsItemError(_ItemException):
    """
    """

    class Reason(enum.Enum):
        """
        """
        ALREADY_CONSUMED = enum.auto()

class BandError(_ItemException):
    """
    """

    class Reason(enum.Enum):
        """
        """
        NOT_EQUIPPED = enum.auto()
        ALREADY_EQUIPPED = enum.auto()
        NOT_FOUND = enum.auto()
        # TODO: Test this
        NO_INVENTORY_SPACE = enum.auto()

class KnightWardError(_ItemException):
    """
    """

    class Reason(enum.Enum):
        """
        """
        NOT_A_KNIGHT = enum.auto()
        ALREADY_EQUIPPED = enum.auto()
        NOT_EQUIPPED = enum.auto()
        # TODO: Test this
        NO_INVENTORY_SPACE = enum.auto()
