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

class AenirError(BaseException):
    """
    This indicates that something in this program didn't function as expected or intended.
    """

class UnitNotFoundError(AenirError):
    """
    To be raised if the unit name has not been recognized.
    """

    def __init__(self, msg: str, unit_list: Iterable[str]):
        """
        Declares `unit_type` in addition to usual initialization.
        """
        super().__init__(msg)
        self.unit_list = unit_list

class InitError(AenirError):
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
        CHAPTER = enum.auto()
        HARD_MODE_AND_CHAPTER = enum.auto()

    def __init__(self, msg: str, *, missing_value: Any, init_params: Mapping[str, Any]):
        """
        Declares `missing_value` in addition to usual initialization.
        """
        super().__init__(msg)
        self.missing_value = missing_value
        self.init_params = init_params

class LevelUpError(AenirError):
    """
    To be raised if an error occurred while levelling up a unit (e.g. level too high).
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to level-up.
        """
        NOT_POSITIVE = enum.auto()
        EXCEEDS_MAX = enum.auto()

    def __init__(self, msg: str, *, reason: Reason, level_range):
        """
        Declares `max_level`.
        """
        super().__init__(msg)
        self.reason = reason
        self.level_range = level_range

class PromotionError(AenirError):
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

class StatBoosterError(AenirError):
    """
    To be raised if an error occurred while using a stat booster.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to use a stat-booster.
        """
        NOT_FOUND = enum.auto()
        STAT_IS_MAXED = enum.auto()

    def __init__(self, msg: str, reason: Reason, *, max_stat: Tuple[str, int] | None = None, valid_stat_boosters: Iterable[str] | None = None):
        """
        Declares name and value of `max_stat` plus list of valid stat-boosters.
        """
        super().__init__(msg)
        self.reason = reason
        self.max_stat = max_stat
        self.valid_stat_boosters = valid_stat_boosters

class ScrollError(AenirError):
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

    def __init__(self, msg: str, reason: Reason, *, valid_scrolls: Mapping[str, bool] | Iterable[str] | None = None, invalid_scroll: str | None = None, equipped_scrolls: Iterable[str] | None = None):
        """
        Declares list of `valid_scrolls`, `equipped_scroll` and `absent_scroll`.
        """
        super().__init__(msg)
        self.reason = reason
        self.valid_scrolls = valid_scrolls
        self.invalid_scroll = invalid_scroll
        self.equipped_scrolls = equipped_scrolls

class GrowthsItemError(AenirError):
    """
    To be raised if an error occurred while using either Afa's Drops or Metis' Tome.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to consume a growths-enhancing item.
        """
        ALREADY_CONSUMED = enum.auto()

    def __init__(self, msg: str, reason: Reason, consumption_date):
        """
        No new attributes declared.
        """
        super().__init__(msg)
        self.reason = reason
        self.consumption_date = consumption_date

class BandError(AenirError):
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

    def __init__(self, msg: str, reason: Reason, *, valid_bands: Mapping[str, bool] | Iterable[str] | None = None, invalid_band: str | None = None, equipped_bands: Iterable[str] | None = None):
        """
        Declares list of `valid_bands`, `equipped_band` and `absent_band`.
        """
        super().__init__(msg)
        self.reason = reason
        self.valid_bands = valid_bands
        self.invalid_band = invalid_band
        self.equipped_bands = equipped_bands

class TransformationError(AenirError):
    """
    To be raised if an error occurred while trying to transform or revert an FE9 unit.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to transform or revert.
        """
        NOT_A_LAGUZ = enum.auto()
        ALREADY_TRANSFORMED = enum.auto()
        NOT_TRANSFORMED = enum.auto()

    def __init__(self, msg: str, reason: Reason):
        """
        Initialize 'reason' attribute.
        """
        super().__init__(msg)
        self.reason = reason

class DemiBandError(TransformationError):
    """
    To be raised if an error occurred while trying to equip the Demi Band in FE9.
    """

    class Reason(enum.Enum):
        """
        Declares all reasons why a unit wouldn't be able to equip the Demi Band.
        """
        ALREADY_EQUIPPED = enum.auto()
        NOT_EQUIPPED = enum.auto()
        NOT_A_LAGUZ = enum.auto()

    def __init__(self, msg: str, reason: Reason):
        """
        Initialize 'reason' attribute.
        """
        super().__init__(msg, reason)
        #self.reason = reason

class KnightWardError(AenirError):
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

    def __init__(self, msg: str, reason: Reason, *, knights: Iterable[str] | None = None, valid_bands = None):
        """
        Initialize 'reason' attribute.
        """
        super().__init__(msg)
        self.reason = reason
        self.knights = knights
        self.valid_bands = valid_bands

