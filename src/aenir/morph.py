"""
"""

import abc
import sqlite3
import json
from typing import Tuple

from aenir.games import FireEmblemGame
from aenir.stats import (
    GenealogyStats,
    GBAStats,
    ThraciaStats,
    AbstractStats,
)
from aenir.logging import logger

class BaseMorph(abc.ABC):
    """
    """

    @classmethod
    @abc.abstractmethod
    def GAME(cls):
        """
        """
        # should return instance of FireEmblemGame
        raise NotImplementedError

    @classmethod
    def STATS(cls):
        """
        """
        return {
            4: GenealogyStats,
            5: ThraciaStats,
            6: GBAStats,
            7: GBAStats,
            8: GBAStats,
            9: GenealogyStats,
        }[cls.GAME().value]

    @classmethod
    def path_to(cls, file: str):
        """
        """
        return "/".join(("static", cls.GAME().url_name, file))

    @staticmethod
    def query_db(
            path_to_db: str,
            table: str,
            fields: Tuple[str],
            filters: dict[str, str],
        ):
        """
        """
        query = f"SELECT {', '.join(fields)} FROM {table}"
        if filters is not None:
            conditions = ", ".join(
                [
                    (f"{field}='{value}'") for field, value in filters.items()
                ]
            )
            query += " WHERE " + conditions
        query += ";"
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            return cnxn.execute(query)

    def __init__(self):
        """
        """
        self.Stats = self.STATS()

    def lookup(
            self,
            home_data: Tuple[str, str],
            target_data: Tuple[str, str],
            tableindex: int,
        ):
        """
        """
        # unpack arguments
        home_table, value_to_lookup = home_data
        target_table, field_to_scan = target_data
        logger.debug(
            "Checking if '%s' from %s[index] has an equivalent in %s[%s].",
            value_to_lookup, home_table, target_table, field_to_scan,
        )
        path_to_json = self.path_to(f"{home_table}-JOIN-{target_table}.json")
        logger.debug(
            "Checking if '%s' exists in the dict in '%s'",
            value_to_lookup, path_to_json,
        )
        with open(path_to_json, encoding='utf-8') as rfile:
            aliased_value = json.load(rfile).pop(value_to_lookup)
        logger.debug(
            "'%s' from %s[index] exists as %r in %s[%s]",
            value_to_lookup, home_table, aliased_value, target_table, field_to_scan,
        )
        if aliased_value is None:
            query_kwargs = None
        else:
            table = "%s%d" % (target_table, tableindex)
            filters = {field_to_scan: aliased_value}
            path_to_db = self.path_to("cleaned_stats.db")
            fields = self.Stats.STAT_LIST()
            logger.debug(
                "BaseMorph.lookup(self, %r, %r, %r, %r)",
                path_to_db,
                table,
                fields,
                filters,
            )
            query_kwargs = {
                "path_to_db": path_to_db,
                "table": table,
                "fields": fields,
                "filters": filters,
            }
        return query_kwargs

class Morph(BaseMorph):
    """
    """
    # NOTE: game_no to be set in each subclass of this class.
    game_no = None

    @classmethod
    def GAME(cls):
        """
        """
        if cls.__name__ == "Morph":
            logger.warning("Instantiating Morph class; some features will be unavailable. Please use appropriate subclass of Morph for full functionality.")
        return FireEmblemGame(cls.game_no)

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        filename = "characters__base_stats-JOIN-characters__growth_rates.json"
        path_to_json = cls.path_to(filename)
        with open(path_to_json, encoding='utf-8') as rfile:
            character_list = list(json.load(rfile))
        return character_list

    def __init__(self, name: str, *, which_bases: int, which_growths: int):
        super().__init__()
        self.game = self.GAME()
        character_list = self.CHARACTER_LIST()
        if name not in character_list:
            raise ValueError(
                "'%s' not found. List of Fire Emblem: %r characters: %r" \
                % (name, self.game.formal_name, character_list)
            )
        self.name = name
        # class and level
        path_to_db = self.path_to("cleaned_stats.db")
        table = "characters__base_stats%d" % which_bases
        fields = self.Stats.STAT_LIST() + ("Class", "Lv")
        filters = {"Name": name}
        basestats_query = self.query_db(
            path_to_db,
            table,
            fields,
            filters,
        ).fetchone()
        # NOTE: if basestats_query is None, then the code terminates here with a TypeError
        stat_dict = dict(basestats_query)
        self.current_cls = stat_dict.pop("Class")
        self.current_lv = stat_dict.pop("Lv")
        # bases
        self.current_stats = self.Stats(**stat_dict)
        # growths
        resultset = self.query_db(
            **self.lookup(
                ("characters__base_stats", name),
                ("characters__growth_rates", "Name"),
                which_growths,
            )
        ).fetchall()
        self.growth_rates = self.Stats(**resultset.pop(which_growths))
        # maximum
        self.current_clstype = "characters__base_stats"
        stat_dict2 = self.query_db(
            **self.lookup(
                (self.current_clstype, name),
                ("classes__maximum_stats", "Class"),
                tableindex=0,
            )
        ).fetchone()
        self.max_stats = self.Stats(**stat_dict2)
        # (miscellany)
        self._meta = {'History': []}
        if name.replace(" (HM)", "") + " (HM)" in character_list:
            self._meta['Hard Mode'] = " (HM)" in name
        self.max_level = None
        self.min_promo_level = None
        self.promo_cls = None

    def _set_max_level(self):
        """
        """
        # exceptions:
        # FE4: 30 for promoted, 20 for unpromoted
        # FE8: unpromoted trainees are capped at 10
        self.max_level = 20

    def _set_min_promo_level(self):
        """
        """
        # exceptions:
        # FE4: 20
        # FE5: for Lara if promo_cls == 'Dancer': 1
        # FE5: Leif, Linoan: 1
        # FE6: Roy: 1
        # FE7: Hector, Eliwood: 1
        self.min_promo_level = 10

    def level_up(self, num_levels: int):
        """
        """
        # get max level
        if self.max_level is None:
            self._set_max_level()
        # stop if user is going to overlevel
        if num_levels + self.current_lv > self.max_level:
            raise ValueError(f"Cannot level up from level {self.current_lv} to {self.current_lv + num_levels}. Max level: self.max_level.")
        # ! increase stats
        self.current_stats += self.growth_rates * 0.01 * num_levels
        # ! increase level
        self.current_lv += num_levels
        # cap stats
        self.current_stats.imin(self.max_stats)

    def promote(self):
        """
        """
        # check if unit's level is high enough to enable promotion
        if self.min_promo_level is None:
            self._set_min_promo_level()
        if self.current_lv < self.min_promo_level:
            raise ValueError(f"{self.name} must be at least level {self.min_promo_level} to promote. Current level: {self.current_lv}.")
        # get promotion data
        value_to_lookup = {
            "characters__base_stats": self.name,
            "classes__promotion_gains": self.current_cls,
        }[self.current_clstype]
        query_kwargs = self.lookup(
            (self.current_clstype, value_to_lookup),
            ("classes__promotion_gains", "Class"),
            tableindex=0,
        )
        query_kwargs['fields'] = list(query_kwargs['fields']) + ["Promotion"]
        resultset = self.query_db(**query_kwargs).fetchall()
        # quit if resultset is empty
        if not resultset:
            raise ValueError(f"{self.name} has no available promotions.")
        # if resultset has length > 1, filter to relevant
        elif len(resultset) > 1:
            resultset = list(
                filter(
                    lambda result: result['Promotion'] == self.promo_cls,
                    resultset,
                )
            )
        # ** PROMOTION START! **
        # record history
        self._meta["History"].append((self.current_lv, self.current_cls))
        # initialize stat_dict, then set attributes
        stat_dict = dict(resultset.pop())
        # set 'current_clstype' for future queries
        self.current_clstype = "classes__promotion_gains"
        # ! change class
        self.current_cls = stat_dict.pop('Promotion')
        # ! increment stats
        promo_bonuses = self.Stats(**stat_dict)
        self.current_stats += promo_bonuses
        # ! set max stats, then cap current stats
        query_kwargs2 = self.lookup(
            (self.current_clstype, self.current_cls),
            ("classes__maximum_stats", "Class"),
            tableindex=0,
        )
        stat_dict2 = self.query_db(**query_kwargs2).fetchall()
        self.max_stats = self.Stats(**stat_dict2.pop())
        self.current_stats.imin(self.max_stats)
        # ! reset level
        self.current_lv = 1
        # set promotion class to None
        self.promo_cls = None
        #self.min_promo_level = None
        #self.max_level = None

    # TODO: Test this!
    def use_stat_booster(self, item_name: str, item_bonus_dict: dict):
        """
        """
        increment = self.Stats(**self.Stats.get_stat_dict(0))
        if item_name not in item_bonus_dict:
            raise KeyError(f"'{item_name}' is not a valid stat booster. Valid stat boosters: {item_bonus_dict.keys()}")
        stat, bonus = item_bonus_dict[item_name]
        setattr(increment, stat, bonus)
        self.current_stats.imin(self.max_stats)

    # TODO: Flesh out informational methods

    def is_maxed(self):
        """
        """
        raise NotImplementedError
        return self.current_stats == self.max_stats

    def __lt__(self, other):
        """
        """
        raise NotImplementedError
        # TODO: put in data from _meta here... somehow
        if not type(self) == type(other):
            raise TypeError(f"Cannot compare stats of type {type(self)} with stats of type {type(other)}.")
        comparison = self.current_stats < other.current_stats
        return comparison

class Morph4(Morph):
    """
    """
    game_no = 4

    def __init__(self, name: str, father_name: str = None):
        """
        """
        path_to_db = self.path_to("cleaned_stats.db")
        table = "characters__base_stats1"
        fields = self.STAT_LIST() + ("Class", "Lv")
        filters = {}
        resultset = self.query_db(
            path_to_db,
            table,
            fields,
            filters,
        ).fetchall()
        # check if name in kid list
        if name not in (result["Name"] for result in resultset):
            # if no: use default init method
            super().__init__(name, which_bases=0, which_growths=0)
            self._meta["Father"] = None
        else:
            father_list = [result["Father"] for result in resultset]
            # if yes: check if father_name in father_list
            if father_name not in father_list:
                raise ValueError(f"'{father_name}' is not a valid father. List of valid fathers: {father_list}")
            # begin initialization here
            self.Stats = self.STATS()
            self.game = self.GAME()
            self.name = name
            stat_dict = dict(
                list(
                    filter(
                        lambda result: result["Name"] == name and result["Father"] == father_name,
                        resultset,
                    )
                ).pop()
            )
            self.current_cls = stat_dict.pop("Class")
            self.current_lv = stat_dict.pop("Lv")
            # bases
            self.current_stats = self.Stats(**stat_dict)
            # growths
            stat_dict2 = dict(
                self.query_db(
                    path_to_db,
                    table="characters__growth_rates1",
                    fields=self.STAT_LIST(),
                    filters={"Name": name, "Father": father_name},
                ).fetchone()
            )
            self.growth_rates = self.Stats(**stat_dict2)
            # maximum
            self.current_clstype = "characters__base_stats"
            stat_dict3 = self.query_db(
                **self.lookup(
                    (self.current_clstype, name),
                    ("classes__maximum_stats", "Class"),
                    tableindex=0,
                )
            ).fetchone()
            self.max_stats = self.Stats(**stat_dict3)
            # (miscellany)
            self._meta = {'History': [], "Father": father_name}
        try:
            self.promo_cls = {
                "Ira": "Swordmaster",
                "Holyn": "Forrest",
                "Radney": "Swordmaster",
                "Roddlevan": "Forrest",
                "Azel": "Mage Knight",
                "Arthur": "Mage Knight",
                "Tinny": "Mage Fighter (F)",
                "Lakche": "Swordmaster",
                "Skasaher": "Forrest",
            }
        except KeyError:
            self.promo_cls = None
        path_to_bases2promo = self.path_to("characters__base_stats-JOIN-classes__promotion_gains.json")
        with open(path_to_bases2promo) as rfile:
            can_promote = json.load(rfile).pop(name) is not None
        if can_promote:
            self.max_level = 20
            self.min_promo_level = 20
        else:
            self.max_level = 30
            self.min_promo_level = 0

    def promote(self):
        """
        """
        super().promote()
        self.max_level = None
        self.min_promo_level = None

    def use_stat_booster(self, item_name: str):
        """
        """
        raise NotImplementedError("FE4 has no stat boosters.")

class Morph5(Morph):
    """
    """
    game_no = 5

    def __init__(self, name: str):
        """
        """
        super().__init__(name, which_bases=0, which_growths=0)
        try:
            self.promo_cls = {
                "Rifis": "Thief Fighter",
                "Asvel": "Sage",
                "Miranda": "Mage Knight",
                "Tania": "Sniper (F)",
                "Ronan": "Sniper (M)",
                "Machua": "Mercenary",
                "Shiva": "Swordmaster",
                "Mareeta": "Swordmaster",
                "Trewd": "Swordmaster",
            }[self.name]
        except KeyError:
            pass
        self._meta["Original Growth Rates"] = self.growth_rates.copy()
        self.equipped_scrolls = {}

    def _set_min_promo_level(self):
        """
        """
        self.min_promo_level = 10
        try:
            self.min_promo_level = {
                "Leif": 1,
                "Linoan": 1,
            }[self.name]
        except KeyError:
            pass
        if self.name == "Lara" and self.promo_cls == "Dancer":
            self.min_promo_level = 1

    def level_up(self, num_levels: int):
        """
        """
        super().level_up(num_levels)
        self.current_stats.imax(self.Stats(**self.Stats.get_stat_dict(0)))

    def promote(self):
        """
        """
        fail_conditions = (
            self.name != "Lara" and self.current_cls == "Thief Fighter",
            self.name == "Lara" and "Dancer" in map(lambda lvcls: lvcls[1], self._meta["History"]),
        )
        if any(fail_conditions):
            raise ValueError(f"{self.name} has no available promotions.")
        super().promote()
        self.current_stats.imax(self.Stats(**self.Stats.get_stat_dict(0)))
        self.min_promo_level = None

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Luck Ring": ("Lck", 3),
            "Life Ring": ("HP", 7),
            "Speed Ring": ("Spd", 3),
            "Magic Ring": ("Mag", 2),
            "Power Ring": ("Str", 3),
            "Body Ring": ("Con", 3),
            "Shield Ring": ("Def", 2),
            "Skill Ring": ("Skl", 3),
            "Leg Ring": ("Mov", 2),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

    def _apply_scroll_bonuses(self):
        """
        """
        self.growth_rates = self._meta["Original Growth Rates"].copy()
        for bonus in self.equipped_scrolls.values():
            self.growth_rates += bonus

    # TODO: Test this
    def unequip_scroll(self, scroll_name: str):
        """
        """
        if scroll_name not in self.equipped_scrolls:
            self.equipped_scrolls.pop(scroll_name)
            self._apply_scroll_bonuses()
        else:
            raise KeyError(f"'{scroll_name}' is not equipped. Equipped_scrolls: {self.equipped_scrolls.keys()}")

    # TODO: Test this
    def equip_scroll(self, scroll_name: str):
        """
        """
        # https://serenesforest.net/thracia-776/inventory/crusader-scrolls/
        if scroll_name in self.equipped_scrolls:
            raise ValueError(f"'{scroll_name}' is already equipped. Equipped scrolls: {self.equipped_scrolls.keys()}.")
        path_to_db = self.path_to("cleaned_stats.db")
        table = "scroll_bonuses"
        stat_dict = query_db(
            path_to_db,
            table,
            fields=self.STAT_LIST(),
            filters={"Name": scroll_name},
        ).fetchone()
        if stat_dict is None:
            resultset = query_db(
                path_to_db,
                table,
                fields=["Name"],
                filters={},
            ).fetchall()
            scroll_list = [result["Name"] for result in resultset]
            raise KeyError(f"'{scroll_name}' is not a valid scroll. List of valid scrolls: {scroll_list}.")
        self.equipped_scrolls[scroll_name] = self.Stats(**scroll_dict)
        self._apply_scroll_bonuses()


# TODO: Implement hard-mode versions of characters.
class Morph6(Morph):
    """
    """
    game_no = 6

    def __init__(self, name: str, hard_mode: bool = False):
        """
        """
        super().__init__(name, which_bases=0, which_growths=0)
        self.name = name.replace(" (HM)", "")
        if self.name + " (HM)" in self.CHARACTER_LIST():
            self._meta["Hard Mode"] = hard_mode
        else:
            if hard_mode:
                logger.warning("'%s' cannot be recruited as an enemy on hard mode.")
            self._meta["Hard Mode"] = None
        if name == "Hugh":
            num_declines = 0
        else:
            num_declines = None
        self._meta["Number of Declines"] = num_declines

    # TODO: Test this
    def decline_hugh(self):
        """
        """
        if self.name != "Hugh":
            raise ValueError("Can only invoke this method on an instance whose name == 'Hugh'")
        self._meta["Number of Declines"] += 1
        if self._meta[decline_key] == 3:
            raise ValueError("Can invoke this method up to three times.")
        decrement = self.Stats(**self.Stats.get_stat_dict(-1))
        self.current_stats += decrement

    def _set_min_promo_level(self):
        """
        """
        if self.name == "Roy":
            self.min_promo_level = 1
        else:
            self.min_promo_level = 10

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 3),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

class Morph7(Morph):
    """
    """
    game_no = 7

    def __init__(self, name: str, lyn_mode: bool = False, hard_mode: bool = False):
        """
        """
        lyndis_league = (
            "Lyn",
            "Sain",
            "Kent",
            "Florina",
            "Wil",
            "Dorcas",
            "Serra",
            "Erk",
            "Rath",
            "Matthew",
            "Nils",
            "Lucius"
            "Wallace",
        )
        if name in lyndis_league:
            if lyn_mode:
                which_bases = 0
            else:
                which_bases = 1
        else:
            if lyn_mode:
                logger.warning("'lyn_mode' = True when '%s' not in Lyn Mode. Ignoring.", name)
            which_bases = 1
            lyn_mode = None
        super().__init__(name, which_bases=which_bases, which_growths=0)
        self._meta["Lyn Mode"] = lyn_mode
        if not lyn_mode and name == "Wallace":
            # directs lookup-function to max stats for the General class
            self.current_clstype = "classes__promotion_gains"
        # hard mode versions
        self.name = name.replace(" (HM)", "")
        if self.name + " (HM)" in self.CHARACTER_LIST():
            self._meta["Hard Mode"] = hard_mode
        else:
            if hard_mode:
                logger.warning("'%s' cannot be recruited as an enemy on hard mode.")
            self._meta["Hard Mode"] = None
        self.is_favorite = False

    def use_afas_drops(self):
        """
        """
        if self.is_favorite:
            raise ValueError(f"{self.name} already used {growths_item}.")
        growths_increment = self.Stats(**self.Stats.get_stat_dict(5))
        self.growth_rates += growths_increment
        self.is_favorite = True

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 3),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

class Morph8(Morph):
    """
    """
    game_no = 8

    def __init__(self, name: str):
        """
        """
        super().__init__(name, which_bases=0, which_growths=0)
        self.is_favorite = False

    def _set_max_level(self):
        """
        """
        # exceptions:
        # FE4: 30 for promoted, 20 for unpromoted
        # FE8: unpromoted trainees are capped at 10
        if self.name in ("Ross", "Amelia", "Ewan") and self.current_clstype == "characters__base_stats":
            self.max_level = 10
        else:
            self.max_level = 20

    def promote(self):
        """
        """
        super().promote()
        self.max_level = None

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 3),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

    def use_metiss_tome(self):
        """
        """
        if self.is_favorite:
            raise ValueError(f"{self.name} already used {growths_item}.")
        growths_increment = self.Stats(**self.Stats.get_stat_dict(5))
        self.growth_rates += growths_increment
        self.is_favorite = True

class Morph9(Morph):
    """
    """
    game_no = 9

    def __init__(self, name: str):
        """
        """
        super().__init__(name, which_bases=0, which_growths=0)

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Seraph Robe": ("HP", 7),
            "Energy Drop": ("Str", 2),
            "Spirit Dust": ("Mag", 2),
            "Secret Book": ("Skl", 2),
            "Speedwing": ("Spd", 3),
            "Ashera Icon": ("Lck", 2),
            "Dracoshield": ("Def", 2),
            "Talisman": ("Res", 2),
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

