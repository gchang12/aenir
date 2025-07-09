"""
Declares exceptions pertaining to virtual unit manipulation.
"""

import abc
import enum

class UnitNotFoundError(BaseException):
    """
    To be raised if the unit name has not been recognized.
    """

    class UnitType(enum.Enum):
        """
        Declares the different types of FE unit.
        """
        NORMAL = enum.auto()
        FATHER = enum.auto()

    def __init__(self, msg, *, unit_type):
        """
        Declares `unit_type` in addition to usual initialization.
        """
        super().__init__(msg)
        self.unit_type = unit_type

class InitError(BaseException):
    """
    To be raised if there was an error in initializing the virtualization of a given unit.
    """

    class MissingValue(enum.Enum):
        """
        Declares the types of info that can be missing.
        """
        LYN_MODE = enum.auto()
        HARD_MODE = enum.auto()

    def __init__(self, msg, *, missing_value):
        """
        Declares `missing_value` in addition to usual initialization.
        """
        super().__init__(msg)
        self.missing_value = missing_value

class LevelUpError(BaseException):
    """
    To be raised if an error occurred while levelling up a unit (e.g. level too high).
    """

class PromotionError(BaseException):
    """
    To be raised if an error occurred while promoting a unit.
    """

    class Reason(enum.Enum):
        """
        Declares all the types of reasons why a unit wouldn't be able to promote.
        """
        NO_PROMOTIONS = enum.auto()
        LEVEL_TOO_LOW = enum.auto()
        INVALID_PROMOTION = enum.auto()

    def __init__(self, msg, *, reason):
        """
        Declares `reason` in addition to usual initialization.
        """
        super().__init__(msg)
        self.reason = reason

class _ItemException(BaseException, abc.ABC):
    """
    To be subclassed; should never be instantiated directly.
    """

    def __init__(self, msg, *, reason):
        """
        Declares `reason` in addition to usual initialization.
        """
        super().__init__(msg)
        self.reason = reason

class StatBoosterError(_ItemException):
    """
    To be raised if an error occurred while using a stat booster.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to use a stat-booster.
        """
        NO_IMPLEMENTATION = enum.auto()
        NOT_FOUND = enum.auto()
        STAT_IS_MAXED = enum.auto()

class ScrollError(_ItemException):
    """
    To be raised if an error occurred while equipping an FE5 scroll.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to equip a given scroll.
        """
        NOT_EQUIPPED = enum.auto()
        ALREADY_EQUIPPED = enum.auto()
        NOT_FOUND = enum.auto()
        NO_INVENTORY_SPACE = enum.auto()

class GrowthsItemError(_ItemException):
    """
    To be raised if an error occurred while using either Afa's Drops or Metis' Tome.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to consume a growths-enhancing item.
        """
        ALREADY_CONSUMED = enum.auto()

class BandError(_ItemException):
    """
    To be raised if an error occurred while equipping an FE9 band.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to equip a given band.
        """
        NOT_EQUIPPED = enum.auto()
        ALREADY_EQUIPPED = enum.auto()
        NOT_FOUND = enum.auto()
        NO_INVENTORY_SPACE = enum.auto()

class KnightWardError(_ItemException):
    """
    To be raised if an error occurred while equipping the Knight Ward in FE9.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to equip the Knight Ward.
        """
        NOT_A_KNIGHT = enum.auto()
        ALREADY_EQUIPPED = enum.auto()
        NOT_EQUIPPED = enum.auto()
        NO_INVENTORY_SPACE = enum.auto()

