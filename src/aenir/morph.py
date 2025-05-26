"""
"""
#

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
    game_no = None
    character_list_filter = None

    @classmethod
    def get_true_character_list(cls):
        """
        """
        if cls.character_list_filter is not None:
            character_list_filter = cls.character_list_filter
        else:
            character_list_filter = lambda name: True
        return filter(character_list_filter, cls.CHARACTER_LIST())

    @classmethod
    def GAME(cls):
        """
        """
        return FireEmblemGame(cls.game_no)

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        filename = "characters__base_stats-JOIN-characters__growth_rates.json"
        path_to_json = cls.path_to(filename)
        with open(path_to_json, encoding='utf-8') as rfile:
            character_list = tuple(json.load(rfile))
        return character_list

    def __init__(self, name: str, *, which_bases: int, which_growths: int):
        #if self.__class__.__name__ == "Morph":
        #logger.warning("Instantiating Morph class; some features will be unavailable. Please use appropriate subclass of Morph for full functionality.")
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
        self._meta = {'History': [], "Stat Boosters": []}
        if name.replace(" (HM)", "") + " (HM)" in character_list:
            self._meta['Hard Mode'] = " (HM)" in name
        self.max_level = None
        self.min_promo_level = None
        self.promo_cls = None
        self.possible_promotions = None

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
        # quit if resultset is empty
        if query_kwargs is None:
            raise ValueError(f"{self.name} has no available promotions.")
        # check if unit's level is high enough to enable promotion
        if self.min_promo_level is None:
            self._set_min_promo_level()
        if self.current_lv < self.min_promo_level:
            raise ValueError(f"{self.name} must be at least level {self.min_promo_level} to promote. Current level: {self.current_lv}.")
        query_kwargs['fields'] = list(query_kwargs['fields']) + ["Promotion"]
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
                raise KeyError("%r is an invalid promotion. Valid promotions: %r" % (self.promo_cls, valid_promotions))
            else:
                resultset = new_resultset
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
        self.possible_promotions = None

    def use_stat_booster(self, item_name: str, item_bonus_dict: dict):
        """
        """
        increment = self.Stats(**self.Stats.get_stat_dict(0))
        if item_name not in item_bonus_dict:
            raise KeyError(f"'{item_name}' is not a valid stat booster. Valid stat boosters: {item_bonus_dict.keys()}")
        stat, bonus = item_bonus_dict[item_name]
        setattr(increment, stat, bonus)
        self.current_stats += increment
        self.current_stats.imin(self.max_stats)
        self._meta["Stat Boosters"].append((self.current_lv, self.current_cls, item_name))

class Morph4(Morph):
    """
    """
    game_no = 4

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
            self.father = None
            #self._meta["Father"] = self.father
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
                raise KeyError(f"'{father}' is not a valid father. List of valid fathers: {father_list}")
            # begin initialization here
            self.Stats = self.STATS()
            self.game = self.GAME()
            self.name = name
            self.father = father
            # begin query
            path_to_db = self.path_to("cleaned_stats.db")
            table = "characters__base_stats1"
            fields = self.Stats.STAT_LIST() + ("Class", "Lv", "Name", "Father")
            filters = {"Name": name, "Father": father}
            logger.debug("Morph4.query_db('%s', '%s', %r, %r)",
                path_to_db,
                table,
                fields,
                filters,
            )
            stat_dict = dict(
                self.query_db(
                    path_to_db,
                    table,
                    fields,
                    filters,
                ).fetchone()
            )
            # class and level
            self.current_cls = stat_dict.pop("Class")
            self.current_lv = stat_dict.pop("Lv")
            # bases
            self.current_stats = self.Stats(**stat_dict)
            # growths
            stat_dict2 = dict(
                self.query_db(
                    path_to_db,
                    table="characters__growth_rates1",
                    fields=self.Stats.STAT_LIST(),
                    filters={"Name": name, "Father": father},
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
            #self._meta = {'History': [], "Father": father}
            self._meta = {'History': []}
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
            }[self.name]
        except KeyError:
            self.promo_cls = None
        path_to_bases2promo = self.path_to("characters__base_stats-JOIN-classes__promotion_gains.json")
        with open(path_to_bases2promo) as rfile:
            can_promote = json.load(rfile).pop(name) is not None
        if can_promote:
            self.max_level = 20
        else:
            self.max_level = 30
        self.min_promo_level = 20
        self._meta["Stat Boosters"] = None

    def promote(self):
        """
        """
        current_lv = self.current_lv
        super().promote()
        self.current_lv = current_lv
        self.max_level = 30
        self.min_promo_level = 20

    def use_stat_booster(self, item_name: str):
        """
        """
        raise NotImplementedError("Not implemented by design; FE4 has no permanent stat booster items.")

class Morph5(Morph):
    """
    """
    game_no = 5

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
        self._og_growth_rates = self.growth_rates.copy()
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
        if self.name == "Lara" and (self.promo_cls == "Dancer" or self.current_cls == "Thief Fighter"):
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
            raise KeyError(f"'{scroll_name}' is not equipped. Equipped_scrolls: {tuple(self.equipped_scrolls.keys())}")

    def equip_scroll(self, scroll_name: str):
        """
        """
        # https://serenesforest.net/thracia-776/inventory/crusader-scrolls/
        if scroll_name in self.equipped_scrolls:
            raise ValueError(f"'{scroll_name}' is already equipped. Equipped scrolls: {tuple(self.equipped_scrolls.keys())}.")
        path_to_db = self.path_to("cleaned_stats.db")
        table = "scroll_bonuses"
        stat_dict = self.query_db(
            path_to_db,
            table,
            fields=self.Stats.STAT_LIST(),
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
        self.equipped_scrolls[scroll_name] = self.Stats(**stat_dict)
        self._apply_scroll_bonuses()

    def mount(self):
        """
        """
        raise NotImplementedError("Implementing this will result in more convolution than I can be arsed to deal with.")

    def unmount(self):
        """
        """
        raise NotImplementedError("Implementing this will result in more convolution than I can be arsed to deal with.")

class Morph6(Morph):
    """
    """
    game_no = 6
    character_list_filter = lambda name: " (HM)" not in name

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

    def __init__(self, name: str, *, hard_mode: bool = False):
        """
        """
        #self.name = name.replace(" (HM)", "")
        if name + " (HM)" in self.CHARACTER_LIST():
            if hard_mode:
                name += " (HM)"
        else:
            if hard_mode:
                logger.warning("'%s' cannot be recruited as an enemy on hard mode.")
            hard_mode = None
        super().__init__(name, which_bases=0, which_growths=0)
        self.name = name.replace(" (HM)", "")
        self._meta["Hard Mode"] = hard_mode
        if name == "Hugh":
            num_declines = 0
        else:
            num_declines = None
        self._meta["Number of Declines"] = num_declines

    def decline_hugh(self):
        """
        """
        if self.name != "Hugh":
            raise ValueError("Can only invoke this method on an instance whose name == 'Hugh'")
        if self._meta["Number of Declines"] == 3:
            raise ValueError("Can invoke this method up to three times.")
        self._meta["Number of Declines"] += 1
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
            "Speedwings": ("Spd", 2),
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
    character_list_filter = lambda name: " (HM)" not in name

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

    def __init__(self, name: str, *, lyn_mode: bool = False, hard_mode: bool = False):
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
        if name in lyndis_league:
            which_bases = {
                True: 0,
                False: 1,
            }[lyn_mode]
            if not lyn_mode and name == "Nils":
                name = "Ninian"
        else:
            if lyn_mode:
                logger.warning("'lyn_mode' = True when '%s' not in Lyn Mode. Ignoring.", name)
                if name == "Ninian":
                    name = "Nils"
            which_bases = 1
            lyn_mode = None
        if name + " (HM)" in self.CHARACTER_LIST():
            if hard_mode:
                name += " (HM)"
        else:
            if hard_mode:
                logger.warning("'%s' cannot be recruited as an enemy on hard mode.")
            hard_mode = None
        super().__init__(name, which_bases=which_bases, which_growths=0)
        self.name = name.replace(" (HM)", "")
        self._meta["Lyn Mode"] = lyn_mode
        self._meta["Hard Mode"] = hard_mode
        if not lyn_mode and name == "Wallace":
            # directs lookup-function to max stats for the General class
            self.current_clstype = "classes__promotion_gains"
        # hard mode versions
        self._growths_item = "Afa's Drops"
        self._meta[self._growths_item] = None

    def use_growths_item(self):
        """
        """
        if self._meta[self._growths_item] is not None:
            raise ValueError(f"{self.name} already used {self._growths_item}.")
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
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

class Morph8(Morph):
    """
    """
    game_no = 8

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
        self._growths_item = "Metis's Tome"
        self._meta[self._growths_item] = None

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
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

    def use_growths_item(self):
        """
        """
        if self._meta[self._growths_item] is not None:
            raise ValueError(f"{self.name} already used {self._growths_item}.")
        growths_increment = self.Stats(**self.Stats.get_stat_dict(5))
        self.growth_rates += growths_increment
        self._meta[self._growths_item] = (self.current_lv, self.current_cls)

class Morph9(Morph):
    """
    """
    game_no = 9

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
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        super().use_stat_booster(item_name, item_bonus_dict)

