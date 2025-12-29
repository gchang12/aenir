"""
Declares exceptions pertaining to virtual unit manipulation.
"""

import abc
import enum
from typing import (
    #Unknown,
    Mapping,
    Any,
    Iterable,
    Tuple,
)

class UnitNotFoundError(BaseException):
    """
    To be raised if the unit name has not been recognized.
    """

    def __init__(self, msg: str):
        """
        Declares `unit_type` in addition to usual initialization.
        """
        super().__init__(msg)

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
        NUMBER_OF_DECLINES = enum.auto()
        ROUTE = enum.auto()
        FATHER = enum.auto()
        HARD_MODE_AND_ROUTE = enum.auto()

    def __init__(self, msg: str, *, missing_value: Any, init_params: Mapping[str, Any], init_params2: Mapping[str, Any] | None = None):
        """
        Declares `missing_value` in addition to usual initialization.
        """
        super().__init__(msg)
        self.missing_value = missing_value
        self.init_params = init_params
        self.init_params2 = init_params2

class LevelUpError(BaseException):
    """
    To be raised if an error occurred while levelling up a unit (e.g. level too high).
    """

    def __init__(self, msg: str, *, max_level: int | None):
        super().__init__(msg)
        self.max_level = max_level

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

    def __init__(self, msg: str, *, reason: Reason, promotion_list: Any | None = None, min_promo_level: int | None = None):
        """
        Declares `reason` in addition to usual initialization.
        """
        super().__init__(msg)
        self.reason = reason
        self.promotion_list = promotion_list
        self.min_promo_level = min_promo_level

class _ItemException(BaseException, abc.ABC):
    """
    To be subclassed; should never be instantiated directly.
    """

    def __init__(self, msg: str, reason: Any):
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

    def __init__(self, msg: str, reason: Reason, *, max_stat: Tuple[str, int] | None = None, valid_stat_boosters: Iterable[str] | None = None):
        """
        """
        super().__init__(msg, reason)
        self.max_stat = max_stat
        self.valid_stat_boosters = valid_stat_boosters

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

    def __init__(self, msg: str, reason: Reason, *, valid_scrolls: Iterable[str] | None = None, equipped_scroll: str | None = None, absent_scroll: str | None = None):
        """
        """
        super().__init__(msg, reason)
        self.valid_scrolls = valid_scrolls
        self.equipped_scroll = equipped_scroll
        self.absent_scroll = absent_scroll

class GrowthsItemError(_ItemException):
    """
    To be raised if an error occurred while using either Afa's Drops or Metis' Tome.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to consume a growths-enhancing item.
        """
        ALREADY_CONSUMED = enum.auto()

    def __init__(self, msg: str, reason: Reason):
        """
        """
        super().__init__(msg, reason)

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

    def __init__(self, msg: str, reason: Reason, *, valid_bands: Iterable[str] | None = None, equipped_band: str | None = None, absent_band: str | None = None):
        """
        """
        super().__init__(msg, reason)
        self.valid_bands = valid_bands
        self.equipped_band = equipped_band
        self.absent_band = absent_band

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

