"""
"""

import abc
import sqlite3
#import json
from typing import Tuple
import copy
from textwrap import indent

from aenir.games import FireEmblemGame
from aenir.stats import (
    GenealogyStats,
    GBAStats,
    ThraciaStats,
    #AbstractStats,
    RadiantStats,
)
from aenir._exceptions import (
    UnitNotFoundError,
    LevelUpError,
    PromotionError,
    StatBoosterError,
    ScrollError,
    BandError,
    GrowthsItemError,
    KnightWardError,
    InitError,
)
from aenir._logging import logger

class BaseMorph(abc.ABC):
    """
    """

    @classmethod
    @abc.abstractmethod
    def GAME(cls):
        """
        """
        # should return instance of FireEmblemGame
        raise NotImplementedError("Not implemented by design; implement in any subclass")

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
            9: RadiantStats,
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
        query = f"SELECT {', '.join(fields)} FROM '{table}'"
        if filters:
            conditions = " AND ".join(
                [
                    #(f"{field}={value}") for field, value in filters.items()
                    ("%s=%r" % (field, value)) for field, value in filters.items()
                ]
            )
            query += " WHERE " + conditions
        query += ";"
        logger.debug("Query: '%s'", query)
        logger.debug("File: '%s'", path_to_db)
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
        table_name = f"{home_table}-JOIN-{target_table}"
        logger.debug(
            "Checking if '%s' exists in the dict in '%s'",
            value_to_lookup, table_name,
        )
        path_to_db = self.path_to("cleaned_stats.db")
        with sqlite3.connect(path_to_db) as cnxn:
            #cnxn.row_factory = sqlite3.Row
            resultset = cnxn.execute("SELECT Alias FROM '%s' WHERE Name=\"%s\"" % (table_name, value_to_lookup))
            aliased_value = resultset.fetchone()
            if aliased_value is not None:
                (aliased_value,) = aliased_value
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
    game_no = None
    character_list_filter = lambda name: True

    @classmethod
    def get_true_character_list(cls):
        """
        """
        return filter(cls.character_list_filter, cls.CHARACTER_LIST())

    @classmethod
    def GAME(cls):
        """
        """
        return FireEmblemGame(cls.game_no)

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        #filename = "characters__base_stats-JOIN-characters__growth_rates.json"
        table_name = "characters__base_stats-JOIN-characters__growth_rates"
        path_to_db = cls.path_to("cleaned_stats.db")
        with sqlite3.connect(path_to_db) as cnxn:
            character_list = map(lambda nametuple: nametuple[0], cnxn.execute("SELECT Name FROM '%s';" % table_name))
        #with open(path_to_json, encoding='utf-8') as rfile:
            #character_list = tuple(json.load(rfile))
        return tuple(character_list)

    def __init__(self, name: str, *, which_bases: int, which_growths: int):
        #if self.__class__.__name__ == "Morph":
        #logger.warning("Instantiating Morph class; some features will be unavailable. Please use appropriate subclass of Morph for full functionality.")
        super().__init__()
        game = self.GAME()
        character_list = self.CHARACTER_LIST()
        if name not in character_list:
            raise UnitNotFoundError(
                f"{name} not found. List of characters from Fire Emblem: {game.formal_name}: {character_list}",
                unit_type=UnitNotFoundError.UnitType.NORMAL,
            )
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
        stat_dict = dict(basestats_query)
        current_cls = stat_dict.pop("Class")
        current_lv = stat_dict.pop("Lv")
        # bases
        current_stats = self.Stats(**stat_dict)
        # growths
        resultset = self.query_db(
            **self.lookup(
                ("characters__base_stats", name),
                ("characters__growth_rates", "Name"),
                which_growths,
            )
        ).fetchall()
        growth_rates = self.Stats(**resultset.pop(which_growths))
        # maximum
        current_clstype = "characters__base_stats"
        stat_dict2 = self.query_db(
            **self.lookup(
                (current_clstype, name),
                ("classes__maximum_stats", "Class"),
                tableindex=0,
            )
        ).fetchone()
        max_stats = self.Stats(**stat_dict2)
        # (miscellany)
        _meta = {"Stat Boosters": []}
        if name.replace(" (HM)", "") + " (HM)" in character_list:
            _meta['Hard Mode'] = " (HM)" in name
        # initialize all attributes here.
        self.game = game
        self.name = name
        self.current_cls = current_cls
        self.current_lv = current_lv
        self.current_stats = current_stats
        self.growth_rates = growth_rates
        self.current_clstype = current_clstype
        self.max_stats = max_stats
        self._meta = _meta
        self.history = []
        self.max_level = None
        self.min_promo_level = None
        self.promo_cls = None
        self.possible_promotions = None
        self.stat_boosters = None

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
            raise LevelUpError(f"Cannot level up from level {self.current_lv} to {self.current_lv + num_levels}. Max level: self.max_level.")
        # ! increase stats
        self.current_stats += self.growth_rates * 0.01 * num_levels
        # ! increase level
        self.current_lv += num_levels
        # cap stats
        self.current_stats.imin(self.max_stats)

    def _get_promo_query_kwargs(self):
        """
        """
        value_to_lookup = {
            "characters__base_stats": self.name,
            "classes__promotion_gains": self.current_cls,
        }[self.current_clstype]
        query_kwargs = self.lookup(
            (self.current_clstype, value_to_lookup),
            ("classes__promotion_gains", "Class"),
            tableindex=0,
        )
        return query_kwargs

    def promote(self):
        """
        """
        query_kwargs = self._get_promo_query_kwargs()
        # quit if resultset is empty
        if query_kwargs is None:
            raise PromotionError(
                f"{self.name} has no available promotions.",
                reason=PromotionError.Reason.NO_PROMOTIONS,
            )
        query_kwargs['fields'] += ("Promotion",)
        # check if unit's level is high enough to enable promotion
        if self.min_promo_level is None:
            self._set_min_promo_level()
        if self.current_lv < self.min_promo_level:
            # Wishful: Tell user what morph should promote to
            raise PromotionError(
                f"{self.name} must be at least level {self.min_promo_level} to promote. Current level: {self.current_lv}.",
                reason=PromotionError.Reason.LEVEL_TOO_LOW,
            )
        # get promotion data
        resultset = self.query_db(**query_kwargs).fetchall()
        # if resultset has length > 1, filter to relevant
        if len(resultset) > 1:
            new_resultset = list(
                filter(
                    lambda result: result['Promotion'] == self.promo_cls,
                    resultset,
                )
            )
            if not new_resultset:
                valid_promotions = tuple(result["Promotion"] for result in resultset)
                self.possible_promotions = valid_promotions
                raise PromotionError(
                    f"{self.promo_cls} is an invalid promotion. Valid promotions: {valid_promotions}",
                    reason=PromotionError.Reason.INVALID_PROMOTION,
                )
            else:
                resultset = new_resultset
        # ** PROMOTION START! **
        # record history
        self.history.append((self.current_lv, self.current_cls))
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
        self.possible_promotions = None

    def use_stat_booster(self, item_name: str, item_bonus_dict: dict):
        """
        """
        #item_bonus_dict = self.stat_boosters
        if item_bonus_dict is None:
            raise StatBoosterError(
                f"Stat boosters are not implemented for FE{self.game.value}.",
                reason=StatBoosterError.Reason.NO_IMPLEMENTATION,
            )
        increment = self.Stats(**self.Stats.get_stat_dict(0))
        if item_name not in item_bonus_dict:
            raise StatBoosterError(
                f"'{item_name}' is not a valid stat booster. Valid stat boosters: {list(item_bonus_dict.keys())}",
                reason=StatBoosterError.Reason.NOT_FOUND,
            )
        stat, bonus = item_bonus_dict[item_name]
        current_val = getattr(self.max_stats, stat)
        if current_val == getattr(self.current_stats, stat):
            raise StatBoosterError(
                f"{stat} is already maxed-out at {current_val}.",
                reason=StatBoosterError.Reason.STAT_IS_MAXED,
            )
        setattr(increment, stat, bonus)
        self.current_stats += increment
        self.current_stats.imin(self.max_stats)
        self._meta["Stat Boosters"].append((self.current_lv, self.current_cls, item_name))

    def copy(self):
        """
        """
        return copy.deepcopy(self)

    def _tare(self):
        """
        """
        self.name = None
        self.game = None
        self.current_cls = None
        self.current_lv = None
        self.current_stats = None
        self.growth_rates = None
        self.current_clstype = None
        self.max_stats = None
        self._meta = None
        self.max_level = None
        self.min_promo_level = None
        self.promo_cls = None
        self.possible_promotions = None
        self.stat_boosters = None

    def __gt__(self, other):
        """
        """
        # self - other
        # This should throw an error if the things don't match
        diff = self.current_stats - other.current_stats
        kishuna = self.copy()
        kishuna._tare()
        kishuna.current_stats = diff
        return kishuna

    def __iter__(self):
        """
        """
        return self.current_stats.__iter__()

    def as_string(self, *, header_data=None, miscellany=None):
        """
        """
        # header: game, name, init-params
        header = [
            ("Game", "FE%d" % self.game.value + "-" + self.game.formal_name),
            ("Unit", self.name),
        ]
        if header_data is not None:
            header.extend(header_data)
        # class-lv history: current, previous, etc.
        history = [
            (self.current_lv, self.current_cls),
        ]
        history.extend([(lv, cls) for lv, cls in self.history])
        # misc:
        #miscellany_ = []
        #self._meta = None
        #self.stat_boosters = None
        # stats:
        def datapair_to_string(keyval):
            """
            """
            format_str = "% 4s: %s"
            return format_str % keyval
        data_as_str = [
            "",
            "Profile\n=======",
            *map(datapair_to_string, header),
            "%",
            "Level Class\n----- -----",
            *map(lambda lvcls: "%5d %s" % lvcls, history),
            "%",
            "Stats\n-----",
            self.current_stats.__repr__(),
        ]
        if miscellany:
            data_as_str.append("%\nMiscellany\n----------")
            data_as_str.extend(list(map(datapair_to_string, miscellany)))
        return indent("\n".join(data_as_str), " " * 4)

    def __repr__(self):
        """
        """
        return self.__str__()

    @property
    def inventory_size(self):
        """
        """
        return 0

class Morph4(Morph):
    """
    """
    game_no = 4

    @property
    def inventory_size(self):
        """
        """
        return 7

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        return (
            'Sigurd',
            'Noish',
            'Alec',
            'Arden',
            'Cuan',
            'Ethlin',
            'Fin',
            'Lex',
            'Azel',
            'Midayle',
            'Adean',
            'Dew',
            'Ira',
            'Diadora',
            'Jamka',
            'Holyn',
            'Lachesis',
            'Levin',
            'Sylvia',
            'Fury',
            'Beowolf',
            'Briggid',
            'Claude',
            'Tiltyu',
            'Mana',
            'Radney',
            'Roddlevan',
            'Oifey',
            'Tristan',
            'Dimna',
            'Yuria',
            'Femina',
            'Amid',
            'Johan',
            'Johalva',
            'Shanan',
            'Daisy',
            'Janne',
            'Aless',
            'Laylea',
            'Linda',
            'Asaello',
            'Hawk',
            'Hannibal',
            'Sharlow',
            'Celice',
            'Leaf',
            'Altenna',
            'Rana',
            'Lakche',
            'Skasaher',
            'Delmud',
            'Lester',
            'Fee',
            'Arthur',
            'Patty',
            'Nanna',
            'Leen',
            'Tinny',
            'Faval',
            'Sety',
            'Corpul',
        )

    def __init__(self, name: str, *, father: str = None):
        """
        """
        # test if name refers to a child with father-dependent stats
        kid_list = (
            'Rana',
            'Lakche',
            'Skasaher',
            'Delmud',
            'Lester',
            'Fee',
            'Arthur',
            'Patty',
            'Nanna',
            'Leen',
            'Tinny',
            'Faval',
            'Sety',
            'Corpul',
        )
        if name not in kid_list:
            # if no: use default init method
            super().__init__(name, which_bases=0, which_growths=0)
            if father is not None:
                logger.warning("Father ('%s') specified for unit who has fixed stats ('%s'). Ignoring.", father, name)
            father = None
            #self._meta["Father"] = self.father
            _meta = self._meta
            game = self.game
            current_cls = self.current_cls
            current_lv = self.current_lv
            current_stats = self.current_stats
            growth_rates = self.growth_rates
            current_clstype = self.current_clstype
            max_stats = self.max_stats
            promo_cls = self.promo_cls
        else:
            father_list = (
                'Arden',
                'Azel',
                'Alec',
                'Claude',
                'Jamka',
                'Dew',
                'Noish',
                'Fin',
                'Beowolf',
                'Holyn',
                'Midayle',
                'Levin',
                'Lex',
            )
            if father not in father_list:
                raise UnitNotFoundError(
                    f"'{father}' is not a valid father. List of valid fathers: {father_list}",
                    unit_type=UnitNotFoundError.UnitType.FATHER,
                )
            # begin initialization here
            Stats = self.STATS()
            game = self.GAME()
            # begin query
            path_to_db = self.path_to("cleaned_stats.db")
            table = "characters__base_stats1"
            fields = Stats.STAT_LIST() + ("Class", "Lv", "Name", "Father")
            filters = {"Name": name, "Father": father}
            logger.debug("Morph4.query_db('%s', '%s', %r, %r)",
                path_to_db,
                table,
                fields,
                filters,
            )
            self.Stats = Stats
            stat_dict = dict(
                self.query_db(
                    path_to_db,
                    table,
                    fields,
                    filters,
                ).fetchone()
            )
            # class and level
            current_cls = stat_dict.pop("Class")
            current_lv = stat_dict.pop("Lv")
            # bases
            current_stats = Stats(**stat_dict)
            # growths
            stat_dict2 = dict(
                self.query_db(
                    path_to_db,
                    table="characters__growth_rates1",
                    fields=Stats.STAT_LIST(),
                    filters={"Name": name, "Father": father},
                ).fetchone()
            )
            growth_rates = Stats(**stat_dict2)
            # maximum
            current_clstype = "characters__base_stats"
            stat_dict3 = self.query_db(
                **self.lookup(
                    (current_clstype, name),
                    ("classes__maximum_stats", "Class"),
                    tableindex=0,
                )
            ).fetchone()
            max_stats = Stats(**stat_dict3)
            # (miscellany)
            #self._meta = {'History': [], "Father": father}
            _meta = {'History': []}
        try:
            promo_cls = {
                "Ira": "Swordmaster",
                "Holyn": "Forrest",
                "Radney": "Swordmaster",
                "Roddlevan": "Forrest",
                "Azel": "Mage Knight",
                "Arthur": "Mage Knight",
                "Tinny": "Mage Fighter (F)",
                "Lakche": "Swordmaster",
                "Skasaher": "Forrest",
            }[name]
        except KeyError:
            promo_cls = None
        _meta["Stat Boosters"] = None
        table_name = "characters__base_stats-JOIN-classes__promotion_gains"
        path_to_db = self.path_to("cleaned_stats.db")
        with sqlite3.connect(path_to_db) as cnxn:
            #cnxn.row_factory = sqlite3.Row
            resultset = cnxn.execute("SELECT Alias FROM '%s' WHERE Name='%s';" % (table_name, name))
            can_promote = resultset.fetchone()[0] is not None
        if can_promote:
            max_level = 20
        else:
            max_level = 30
        # set instance attributes
        self.min_promo_level = 20
        self.max_level = max_level
        self._meta = _meta
        self.father = father
        self.game = game
        self.name = name
        self.current_cls = current_cls
        self.current_lv = current_lv
        self.current_stats = current_stats
        self.growth_rates = growth_rates
        self.current_clstype = current_clstype
        self.max_stats = max_stats
        self.promo_cls = promo_cls
        self.history = []
        self._meta.pop("Stat Boosters")

    def promote(self):
        """
        """
        current_lv = self.current_lv
        super().promote()
        self.current_lv = current_lv
        self.max_level = 30
        self.min_promo_level = 20

    def __str__(self):
        """
        """
        header_data = []
        if self.father is not None:
            header_data.append(
                ("Sire", self.father),
            )
        return super().as_string(header_data=header_data)

class Morph5(Morph):
    """
    """
    game_no = 5

    @property
    def inventory_size(self):
        """
        """
        return 7

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        return (
            'Leaf',
            'Fin',
            'Evayle',
            'Halvan',
            'Othin',
            'Dagda',
            'Tania',
            'Marty',
            'Ronan',
            'Rifis',
            'Safy',
            'Brighton',
            'Machua',
            'Lara',
            'Felgus',
            'Karin',
            'Dalsin',
            'Asvel',
            'Nanna',
            'Hicks',
            'Shiva',
            'Carrion',
            'Selphina',
            'Kein',
            'Alva',
            'Robert',
            'Fred',
            'Olwen',
            'Mareeta',
            'Salem',
            'Pahn',
            'Tina',
            'Trewd',
            'Glade',
            'Dean',
            'Eda',
            'Homeros',
            'Linoan',
            'Ralph',
            'Eyrios',
            'Sleuf',
            'Sara',
            'Miranda',
            'Shanam',
            'Misha',
            'Xavier',
            'Amalda',
            'Conomore',
            'Delmud',
            'Cyas',
            'Sety',
            'Galzus',
        )

    def __init__(self, name: str):
        """
        """
        super().__init__(name, which_bases=0, which_growths=0)
        try:
            promo_cls = {
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
            promo_cls = None
        # set instance attributes
        self.promo_cls = promo_cls
        self._og_growth_rates = self.growth_rates.copy()
        self.equipped_scrolls = {}
        self.is_mounted = None

    def _set_min_promo_level(self):
        """
        """
        try:
            min_promo_level = {
                "Leif": 1,
                "Linoan": 1,
            }[self.name]
        except KeyError:
            min_promo_level = 10
        if self.name == "Lara" and (self.promo_cls == "Dancer" or self.current_cls == "Thief Fighter"):
            min_promo_level = 1
        self.min_promo_level = min_promo_level

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
            self.name == "Lara" and "Dancer" in map(lambda lvcls: lvcls[1], self.history),
        )
        if any(fail_conditions):
            raise PromotionError(
                f"{self.name} has no available promotions.",
                reason=PromotionError.Reason.NO_PROMOTIONS,
            )
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
        return super().use_stat_booster(item_name, item_bonus_dict)

    def _apply_scroll_bonuses(self):
        """
        """
        self.growth_rates = self._og_growth_rates.copy()
        for bonus in self.equipped_scrolls.values():
            self.growth_rates += bonus

    def unequip_scroll(self, scroll_name: str):
        """
        """
        if scroll_name in self.equipped_scrolls:
            self.equipped_scrolls.pop(scroll_name)
            self._apply_scroll_bonuses()
        else:
            raise ScrollError(
                f"'{scroll_name}' is not equipped. Equipped_scrolls: {tuple(self.equipped_scrolls.keys())}",
                reason=ScrollError.Reason.NOT_EQUIPPED,
            )

    def equip_scroll(self, scroll_name: str):
        """
        """
        # https://serenesforest.net/thracia-776/inventory/crusader-scrolls/
        if scroll_name in self.equipped_scrolls:
            raise ScrollError(
                f"'{scroll_name}' is already equipped. Equipped scrolls: {tuple(self.equipped_scrolls.keys())}.",
                reason=ScrollError.Reason.ALREADY_EQUIPPED,
            )
        if len(self.equipped_scrolls) >= self.inventory_size:
            raise ScrollError(
                f"You can equip at most {self.inventory_size} scrolls at once.",
                reason=ScrollError.Reason.NO_INVENTORY_SPACE,
            )
        path_to_db = self.path_to("cleaned_stats.db")
        table = "scroll_bonuses"
        stat_dict = self.query_db(
            path_to_db,
            table,
            fields=self.Stats.STAT_LIST(),
            filters={"Name": scroll_name},
        ).fetchone()
        if stat_dict is None:
            resultset = self.query_db(
                path_to_db,
                table,
                fields=["Name"],
                filters={},
            ).fetchall()
            scroll_list = [result["Name"] for result in resultset]
            raise ScrollError(
                f"'{scroll_name}' is not a valid scroll. List of valid scrolls: {scroll_list}.",
                reason=ScrollError.Reason.NOT_FOUND,
            )
        self.equipped_scrolls[scroll_name] = self.Stats(**stat_dict)
        self._apply_scroll_bonuses()

    def __str__(self):
        """
        """
        miscellany = []
        if self.equipped_scrolls:
            miscellany.append(
                ("Scrolls", ", ".join(self.equipped_scrolls)),
            )
        if self._meta["Stat Boosters"]:
            miscellany.append(
                ("Stat Boosters", ", ".join(str(lvclsitem) for lvclsitem in self._meta["Stat Boosters"])),
            )
        return super().as_string(miscellany=miscellany)

class Morph6(Morph):
    """
    """
    game_no = 6
    character_list_filter = lambda name: " (HM)" not in name

    @property
    def inventory_size(self):
        """
        """
        return 5

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        return (
            'Roy',
            'Marcus',
            'Allen',
            'Lance',
            'Wolt',
            'Bors',
            'Merlinus',
            'Ellen',
            'Dieck',
            'Wade',
            'Lott',
            'Thany',
            'Chad',
            'Lugh',
            'Clarine',
            'Rutger',
            'Rutger (HM)',
            'Saul',
            'Dorothy',
            'Sue',
            'Zealot',
            'Treck',
            'Noah',
            'Astohl',
            'Lilina',
            'Wendy',
            'Barth',
            'Oujay',
            'Fir',
            'Fir (HM)',
            'Shin',
            'Shin (HM)',
            'Gonzales',
            'Gonzales (HM)',
            'Geese',
            'Klein',
            'Klein (HM)',
            'Tate',
            'Tate (HM)',
            'Lalum',
            'Echidna',
            'Elphin',
            'Bartre',
            'Ray',
            'Cath',
            'Cath (HM)',
            'Miredy',
            'Miredy (HM)',
            'Percival',
            'Percival (HM)',
            'Cecilia',
            'Sofiya',
            'Igrene',
            'Garret',
            'Garret (HM)',
            'Fa',
            'Hugh',
            'Zeis',
            'Zeis (HM)',
            'Douglas',
            'Niime',
            'Dayan',
            'Juno',
            'Yodel',
            'Karel',
            'Narshen',
            'Gale',
            'Hector',
            'Brunya',
            'Eliwood',
            'Murdoch',
            'Zephiel',
            'Guinevere',
        )

    def __init__(self, name: str, *, hard_mode: bool = None):
        """
        """
        #self.name = name.replace(" (HM)", "")
        if name + " (HM)" in self.CHARACTER_LIST():
            if hard_mode is None:
                raise InitError(
                    f"Please specify a `hard_mode` boolean value for {name}.",
                    missing_value=InitError.MissingValue.HARD_MODE,
                )
            if hard_mode:
                name += " (HM)"
        else:
            if hard_mode:
                logger.warning("'%s' cannot be recruited as an enemy on hard mode.", name)
            hard_mode = None
        super().__init__(name, which_bases=0, which_growths=0)
        if name == "Hugh":
            num_declines = 0
        else:
            num_declines = None
        # set instance attributes
        self.name = name.replace(" (HM)", "")
        self._meta["Hard Mode"] = hard_mode
        self._meta["Number of Declines"] = num_declines

    def decline_hugh(self):
        """
        """
        if self.name != "Hugh":
            raise ValueError("Can only invoke this method on an instance whose name == 'Hugh'")
        if self._meta["Number of Declines"] == 3:
            raise OverflowError("Can invoke this method up to three times.")
        self._meta["Number of Declines"] += 1
        decrement = self.Stats(**self.Stats.get_stat_dict(-1))
        self.current_stats += decrement

    def _set_min_promo_level(self):
        """
        """
        if self.name == "Roy":
            min_promo_level = 1
        else:
            min_promo_level = 10
        self.min_promo_level = min_promo_level

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

    def __str__(self):
        """
        """
        _meta = self._meta
        miscellany = []
        if _meta["Stat Boosters"]:
            miscellany.append(
                ("Stat Boosters", ", ".join(str(lvclsitem) for lvclsitem in self._meta["Stat Boosters"])),
            )
        if _meta["Number of Declines"] is not None:
            miscellany.append(
                ("Number of Declines", _meta["Number of Declines"]),
            )
        header_data = []
        if _meta["Hard Mode"] is not None:
            header_data.append(
                ("HM", _meta["Hard Mode"]),
            )
        return super().as_string(header_data=header_data, miscellany=miscellany)

class Morph7(Morph):
    """
    """
    game_no = 7
    character_list_filter = lambda name: " (HM)" not in name

    @property
    def inventory_size(self):
        """
        """
        return 5

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        return (
            'Lyn',
            'Sain',
            'Kent',
            'Florina',
            'Wil',
            'Dorcas',
            'Serra',
            'Erk',
            'Rath',
            'Matthew',
            'Nils',
            'Lucius',
            'Wallace',
            'Eliwood',
            'Lowen',
            'Marcus',
            'Rebecca',
            'Bartre',
            'Hector',
            'Oswin',
            'Guy',
            'Guy (HM)',
            'Merlinus',
            'Priscilla',
            'Raven',
            'Raven (HM)',
            'Canas',
            'Dart',
            'Fiora',
            'Legault',
            'Legault (HM)',
            'Ninian',
            'Isadora',
            'Heath',
            'Hawkeye',
            'Geitz',
            'Geitz (HM)',
            'Farina',
            'Pent',
            'Louise',
            'Karel',
            'Harken',
            'Harken (HM)',
            'Nino',
            'Jaffar',
            'Vaida',
            'Vaida (HM)',
            'Karla',
            'Renault',
            'Athos',
        )

    def __init__(self, name: str, *, lyn_mode: bool = None, hard_mode: bool = None):
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
            "Lucius",
            "Wallace",
        )
        # check if unit is available in lyn-mode
        if name in lyndis_league:
            if lyn_mode is None:
                raise InitError(
                    f"Please specify a `lyn_mode` boolean value for {name}.",
                    missing_value=InitError.MissingValue.LYN_MODE,
                )
            which_bases = {
                True: 0,
                False: 1,
            }[lyn_mode]
            if not lyn_mode and name == "Nils":
                # test this.
                logger.warning("`lyn_mode` is False. Treating Morph as 'Ninian'.")
                name = "Ninian"
        else:
            if lyn_mode:
                logger.warning("'lyn_mode' = True when '%s' not in Lyn Mode. Ignoring.", name)
                if name == "Ninian":
                    raise UnitNotFoundError(
                        "Ninian is not in the Lyndis League.",
                        unit_type=UnitNotFoundError.UnitType.NORMAL,
                    )
                #name = "Nils"
            which_bases = 1
            lyn_mode = None
        # check if unit can be recruited on hard-mode
        if name + " (HM)" in self.CHARACTER_LIST():
            if hard_mode is None:
                raise InitError(
                    f"Please specify a `hard_mode` boolean value for {name}.",
                    missing_value=InitError.MissingValue.HARD_MODE,
                )
            if hard_mode:
                name += " (HM)"
        else:
            if hard_mode:
                logger.warning("'%s' cannot be recruited as an enemy on hard mode.")
            hard_mode = None
        # initialize as usual
        super().__init__(name, which_bases=which_bases, which_growths=0)
        if not lyn_mode and name == "Wallace":
            # directs lookup-function to max stats for the General class
            current_clstype = "classes__promotion_gains"
        else:
            current_clstype = self.current_clstype
        _growths_item = "Afa's Drops"
        # set instance attributes
        self.current_clstype = current_clstype
        self.name = name.replace(" (HM)", "")
        self._meta["Lyn Mode"] = lyn_mode
        self._meta["Hard Mode"] = hard_mode
        self._growths_item = _growths_item
        self._meta[_growths_item] = None

    def use_afas_drops(self):
        """
        """
        _growths_item = self._growths_item
        if self._meta[_growths_item] is not None:
            raise GrowthsItemError(
                f"{self.name} already used {_growths_item}.",
                reason=GrowthsItemError.Reason.ALREADY_CONSUMED,
            )
        growths_increment = self.Stats(**self.Stats.get_stat_dict(5))
        self.growth_rates += growths_increment
        self._meta[self._growths_item] = (self.current_lv, self.current_cls)

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

    def __str__(self):
        """
        """
        # header
        header_data = []
        header_fields = (
            "Lyn Mode",
            "Hard Mode",
        )
        _meta = self._meta
        def get_initials(name):
            """
            """
            initials = []
            for word in name.split(' '):
                initials.append(word[0])
            return "".join(initials)
        for field in filter(lambda field_: _meta[field_] is not None, header_fields):
            header_data.append(
                (get_initials(field), _meta[field]),
            )
        # miscellany
        miscellany = []
        if self._meta["Stat Boosters"]:
            miscellany.append(
                ("Stat Boosters", ", ".join(str(lvclsitem) for lvclsitem in self._meta["Stat Boosters"])),
            )
        _growths_item = self._growths_item
        if _meta[_growths_item]:
            miscellany.append(
                (_growths_item, _meta[_growths_item]),
            )
        return super().as_string(header_data=header_data, miscellany=miscellany)


class Morph8(Morph):
    """
    """
    game_no = 8

    @property
    def inventory_size(self):
        """
        """
        return 5

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        return (
            'Eirika',
            'Seth',
            'Franz',
            'Gilliam',
            'Vanessa',
            'Moulder',
            'Ross',
            'Garcia',
            'Neimi',
            'Colm',
            'Artur',
            'Lute',
            'Natasha',
            'Joshua',
            'Ephraim',
            'Forde',
            'Kyle',
            'Orson',
            'Tana',
            'Amelia',
            'Innes',
            'Gerik',
            'Tethys',
            'Marisa',
            "L'Arachel",
            'Dozla',
            'Saleh',
            'Ewan',
            'Cormag',
            'Rennac',
            'Duessel',
            'Knoll',
            'Myrrh',
            'Syrene',
            'Caellach',
            'Riev',
            'Ismaire',
            'Selena',
            'Glen',
            'Hayden',
            'Valter',
            'Fado',
            'Lyon',
        )

    def __init__(self, name: str):
        """
        """
        super().__init__(name, which_bases=0, which_growths=0)
        _growths_item = "Metis's Tome"
        # set instance attributes
        self._growths_item = _growths_item
        self._meta[_growths_item] = None

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
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

    def use_metiss_tome(self):
        """
        """
        _growths_item = self._growths_item
        if self._meta[_growths_item] is not None:
            raise GrowthsItemError(
                f"{self.name} already used {_growths_item}.",
                reason=GrowthsItemError.Reason.ALREADY_CONSUMED,
            )
        growths_increment = self.Stats(**self.Stats.get_stat_dict(5))
        self.growth_rates += growths_increment
        self._meta[_growths_item] = (self.current_lv, self.current_cls)

    def __str__(self):
        """
        """
        _meta = self._meta
        miscellany = []
        if _meta['Stat Boosters']:
            miscellany.append(
                ("Stat Boosters", ", ".join(str(lvclsitem) for lvclsitem in self._meta["Stat Boosters"])),
            )
        _growths_item = self._growths_item
        if _meta[_growths_item]:
            miscellany.append(
                (_growths_item, _meta[_growths_item]),
            )
        return super().as_string(miscellany=miscellany)

class Morph9(Morph):
    """
    """
    game_no = 9

    @property
    def inventory_size(self):
        """
        """
        return 8

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        return (
            'Ike',
            'Titania',
            'Oscar',
            'Boyd',
            'Rhys',
            'Shinon',
            'Gatrie',
            'Soren',
            'Mia',
            'Ilyana',
            'Marcia',
            'Mist',
            'Rolf',
            'Lethe',
            'Mordecai',
            'Volke',
            'Kieran',
            'Brom',
            'Nephenee',
            'Zihark',
            'Jill',
            'Sothe',
            'Astrid',
            'Makalov',
            'Stefan',
            'Muarim',
            'Tormod',
            'Devdan',
            'Tanith',
            'Reyson',
            'Janaff',
            'Ulki',
            'Calill',
            'Tauroneo',
            'Ranulf',
            'Haar',
            'Lucia',
            'Bastian',
            'Geoffrey',
            'Largo',
            'Elincia',
            'Ena',
            'Nasir',
            'Tibarn',
            'Naesala',
            'Giffca',
            'Sephiran',
            'Leanne',
        )

    def __init__(self, name: str):
        """
        """
        super().__init__(name, which_bases=0, which_growths=0)
        # conditionally determine if unit can equip it
        # Knights, Generals, horseback Knights, Paladins, Soldiers and Halberdiers only
        knights = (
            #'Ike',
            'Titania',
            'Oscar',
            #'Boyd',
            #'Rhys',
            #'Shinon',
            'Gatrie',
            #'Soren',
            #'Mia',
            #'Ilyana',
            #'Marcia',
            #'Mist',
            #'Rolf',
            #'Lethe',
            #'Mordecai',
            #'Volke',
            'Kieran',
            'Brom',
            'Nephenee',
            #'Zihark',
            #'Jill',
            #'Sothe',
            'Astrid',
            'Makalov',
            #'Stefan',
            #'Muarim',
            #'Tormod',
            'Devdan',
            #'Tanith',
            #'Reyson',
            #'Janaff',
            #'Ulki',
            #'Calill',
            'Tauroneo',
            #'Ranulf',
            #'Haar',
            #'Lucia',
            #'Bastian',
            'Geoffrey',
            #'Largo',
            #'Elincia',
            #'Ena',
            #'Nasir',
            #'Tibarn',
            #'Naesala',
            #'Giffca',
            #'Sephiran',
            #'Leanne',
        )
        if name in knights:
            knight_ward_is_equipped = False
        else:
            knight_ward_is_equipped = None
        # set instance attributes
        self.knight_ward_is_equipped = knight_ward_is_equipped 
        self.equipped_bands = {}
        self._og_growth_rates = self.growth_rates.copy()

    def use_stat_booster(self, item_name: str):
        """
        """
        item_bonus_dict = {
            "Seraph Robe": ("HP", 7),
            "Energy Drop": ("Str", 2),
            "Spirit Dust": ("Mag", 2),
            "Secret Book": ("Skl", 2),
            "Speedwing": ("Spd", 2),
            "Ashera Icon": ("Lck", 2),
            "Dracoshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

    def _apply_band_bonuses(self):
        """
        """
        self.growth_rates = self._og_growth_rates.copy()
        for bonus in self.equipped_bands.values():
            self.growth_rates += bonus

    def equip_band(self, band_name: str):
        """
        """
        # https://serenesforest.net/thracia-776/inventory/crusader-scrolls/
        if band_name in self.equipped_bands:
            raise BandError(
                f"{band_name} is already equipped. Equipped bands: {tuple(self.equipped_bands.keys())}.",
                reason=BandError.Reason.ALREADY_EQUIPPED,
            )
        if len(self.equipped_bands) == self.inventory_size:
            raise BandError(
                f"You can equip at most {self.inventory_size} scrolls at once.",
                reason=BandError.Reason.NO_INVENTORY_SPACE,
            )
        path_to_db = self.path_to("cleaned_stats.db")
        table = "band_growths"
        stat_dict = self.query_db(
            path_to_db,
            table,
            fields=self.Stats.STAT_LIST(),
            filters={"Name": band_name},
        ).fetchone()
        if stat_dict is None:
            resultset = self.query_db(
                path_to_db,
                table,
                fields=["Name"],
                filters={},
            ).fetchall()
            band_list = [result["Name"] for result in resultset]
            raise BandError(
                f"{band_name} is already equipped. Equipped bands: {tuple(self.equipped_bands.keys())}.",
                reason=BandError.Reason.NOT_FOUND,
            )
        self.equipped_bands[band_name] = self.Stats(**stat_dict)
        self._apply_band_bonuses()

    def unequip_band(self, band_name: str):
        """
        """
        if band_name in self.equipped_bands:
            self.equipped_bands.pop(band_name)
            self._apply_band_bonuses()
        else:
            raise BandError(
                f"{band_name} is not equipped. Equipped_bands: {tuple(self.equipped_bands.keys())}",
                reason=BandError.Reason.NOT_EQUIPPED,
            )

    def equip_knight_ward(self):
        """
        """
        if self.knight_ward_is_equipped is None:
            raise KnightWardError(
                f"{self.name} is not a knight; cannot equip Knight Ward.",
                reason=KnightWardError.Reason.NOT_A_KNIGHT,
            )
        if len(self.equipped_bands) == self.inventory_size:
            raise KnightWardError(
                f"Your inventory is full at: {self.inventory_size} items. Knight Band has not equipped.",
                reason=KnightWardError.Reason.NO_INVENTORY_SPACE,
            )
        if self.knight_ward_is_equipped is True:
            raise KnightWardError(
                f"{self.name} already has the Knight Ward equipped.",
                reason=KnightWardError.Reason.ALREADY_EQUIPPED,
            )
        # update stats
        self.growth_rates = self._og_growth_rates.copy()
        # look up knight band
        band_name = "Knight Ward"
        stat_dict = self.Stats.get_stat_dict(0)
        stat_dict['Spd'] = 30
        #path_to_db = self.path_to("cleaned_stats.db")
        #table = "band_growths"
        #stat_dict = self.query_db(
            #path_to_db,
            #table,
            #fields=self.Stats.STAT_LIST(),
            #filters={"Name": band_name},
        #).fetchone()
        # set to list of bands
        self.equipped_bands[band_name] = self.Stats(**stat_dict)
        self._apply_band_bonuses()
        # set the thing
        self.knight_ward_is_equipped = True

    def unequip_knight_ward(self):
        """
        """
        if self.knight_ward_is_equipped is None:
            raise KnightWardError(f"{self.name} is not a knight; cannot unequip Knight Ward.")
        if self.knight_ward_is_equipped is False:
            raise KnightWardError(
                f"{self.name} does not have the Knight Ward equipped.",
                reason=KnightWardError.Reason.NOT_EQUIPPED,
            )
        self.equipped_bands.pop(band_name)
        self._apply_band_bonuses()
        self.knight_ward_is_equipped = False

    def __str__(self):
        """
        """
        _meta = self._meta
        miscellany = []
        if self._meta["Stat Boosters"]:
            miscellany.append(
                ("Stat Boosters", ", ".join(str(lvclsitem) for lvclsitem in self._meta["Stat Boosters"])),
            )
        if self.equipped_bands:
            miscellany.append(
                ("Bands", ", ".join(self.equipped_bands)),
            )
        return super().as_string(miscellany=miscellany)

def get_morph(game_no: int, name: str, **kwargs):
    """
    """
    try:
        morph_cls = {
            4: Morph4,
            5: Morph5,
            6: Morph6,
            7: Morph7,
            8: Morph8,
            9: Morph9,
        }[game_no]
    except KeyError:
        raise NotImplementedError("Stat comparison for FE%s has not been implemented." % game_no)
    morph = morph_cls(name, **kwargs)
    return morph

