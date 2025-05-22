

class ProtoMorph:
    """
    Defines parameters and methods for stat look-up and name verification.

    current_clstype: Determines which table to match from.
    current_cls: Value of the current class, to be matched.
    target_stats: Stores the stats to be retrieved.
    history: Stores the history of a unit as a list of (Class, Lv) tuples.
    STAT_ORDERING: Stores the order of stat labels.
    """

    @property
    def home_dir(self):
        return self._home_dir

    def __init__(self, game_num: int):
        """
        Defines:
        current_clstype - For use in cross-referencing names in tables.
        current_cls - Stores current class
        target_stats - Temporary store for stat-augmenting arrays
        """
        # To be edited never
        self._game_num = game_num
        # To be edited never
        self._game_name = self.NUM_TO_NAME[game_num]
        # essential to set_targetstats method
        # TODO: To be edited only by program. Is set by `set_targetstats` method.
        #       How to restrict permissions on this field so that it can only be modified by `set_targetstats`?
        #       Perhaps a pd-Series equivalent of list.append?
        self.target_stats = None
        # Can be edited by user.
        self.current_stats = None
        # To be edited only by program
        # history (class, lv) tuples, and labels for comparison DataFrame
        self._history = []
        # To be edited only by program
        self._comparison_labels = {}
        # load tables
        # To be edited never
        self._home_dir = Path(self.DATADIR_ROOT).joinpath(self.game_name)
        # To be edited by user. Turned into class attribute.
        #self.tables_file = "cleaned_stats.db"


class BaseMorph(ProtoMorph):
    """
    """
    def __init__(self, game_num: int):
        ProtoMorph.__init__(self, game_num)
        # initialize instance attribute `url_to_tables`
        del self.url_to_tables
        # delete instance attribute `url_to_tables`, and allow class attribute `url_to_tables` to occupy namespace
        #if not self.url_to_tables:
        for urlpath in self.page_dict:
            self.load_tables(urlpath)

    def get_lynmode_options(self) -> List[str]:
        """
        Returns a List[str] of possible pseudo-booleans for a member of the Lyndis League.
        """
        lyn_options = [False, True]
        return [str(option) for option in lyn_options]

    def get_hardmode_options(self) -> List[str]:
        """
        Returns a List[str] of possible pseudo-booleans for a character with Hard Mode bonuses.
        """
        hm_options = [False, True]
        return [str(option) for option in hm_options]

    def get_character_list(self) -> List[str]:
        """
        Returns a List[str] of base!character names mapped to growths!character names.
        Raises:
        - FileNotFoundError: not home_dir.joinpath("characters__base_stats-JOIN-characters__growth_rates.json").exists()
        - json.decoder.JSONDecodeError: File is not in JSON form.
        """
        logging.info("BaseMorph.get_character_list(self)")
        ltable_url = "characters/base-stats"
        rtable_url = "characters/growth-rates"
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        # query character list from JSON (FileNotFoundError may be raised before that)
        with io.open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        chrlist = []
        # filter to include non-None entries
        for chrname, growth_equivalent in clsrecon_dict.items():
            if growth_equivalent is None:
                continue
            chrlist.append(chrname)
        # return keys mapped to non-None
        logging.info("%d names found: %s", len(chrlist), chrlist)
        return chrlist

    def get_fe4_unit_list(self, unit_type: str) -> List[str]:
        """
        Shortcut function to get a list of either FE4 kids or fathers.
        """
        assert self.game_num == 4
        tgt_colname = {
            "kid": "Name",
            "father": "Father",
        }[unit_type]
        tablename = "characters/growth-rates"
        src_tablelist = self.url_to_tables[tablename]
        src_table = src_tablelist[1]
        src_column = src_table[tgt_colname].copy()
        src_column.drop_duplicates(inplace=True)
        unit_list = src_column.to_list()
        return unit_list

class Morph(BaseMorph):
    """
    Defines methods to simulate level-ups and promotions for interactive user session.

    BRANCHED_PROMO_EXCEPTIONS: dict of fixed promotion paths, filled out manually.
    unit_name: The name of the unit.
    promo_cls: Determines which promotion path the unit must follow.
    current_stats: Stores the unit's current stats; the centerpiece, and object of most operations.
    """

    # declare promo-branch exceptions here as a dict-attribute
    BRANCHED_PROMO_EXCEPTIONS = {
        (4, "Ira"): "Swordmaster",
        (4, "Holyn"): "Forrest",
        (4, "Radney"): "Swordmaster",
        (4, "Roddlevan"): "Forrest",
        (4, "Azel"): "Mage Knight",
        (4, "Arthur"): "Mage Knight",
        (4, "Tinny"): "Mage Fighter (F)",
        (4, "Lakche"): "Swordmaster",
        (4, "Skasaher"): "Forrest",
        (5, "Rifis"): "Thief Fighter",
        (5, "Asvel"): "Sage",
        (5, "Miranda"): "Mage Knight",
        (5, "Tania"): "Sniper (F)",
        (5, "Ronan"): "Sniper (M)",
        (5, "Machua"): "Mercenary",
        (5, "Shiva"): "Swordmaster",
        (5, "Mareeta"): "Swordmaster",
        (5, "Trewd"): "Swordmaster",
    }

    url_to_tables = {}

    def __init__(self, game_num: int, unit_name: str, *, tableindex: int = 0, growths_tableindex: int = 0):
        """
        Loads tables, and initializes bases among other things.

        Defines: promo_cls, unit_name, current_stats
        """
        BaseMorph.__init__(self, game_num)
        # initialize bases
        self._unit_name = unit_name
        try:
            temp_bases = self.url_to_tables.pop("characters/base-stats")[tableindex].set_index("Name").loc[unit_name, :]
        except KeyError as unit_dne_err:
            print(f"'{unit_name}' is not in the list of FE{game_num} units: {self.get_character_list()}.")
            raise unit_dne_err
        logging.info("Morph(%d, '%s')", game_num, unit_name)
        self.current_clstype = "characters/base-stats"
        self.current_cls = temp_bases.pop("Class")
        self.current_lv = temp_bases.pop("Lv")
        # implicitly convert to float
        self.current_stats = temp_bases + 0.0
        assert set(self.STAT_ORDERING[self.game_num]) == set(self.current_stats.index)
        assert len(self.STAT_ORDERING[self.game_num]) == len(self.current_stats.index)
        self.current_stats.index = self.STAT_ORDERING[self.game_num]
        try:
            self.promo_cls = self.BRANCHED_PROMO_EXCEPTIONS[(game_num, unit_name)]
        except KeyError:
            self.promo_cls = None
        # set growth rates
        self.lookup(
            ("characters/base-stats", self.unit_name),
            ("characters/growth-rates", "Name"),
            growths_tableindex,
        )
        self.growth_rates = self.target_stats
        self.target_stats = None
        # test if unit has HM bonus
        if unit_name.replace(" (HM)", "") + " (HM)" in self.get_character_list():
            self.comparison_labels["Hard Mode"] = " (HM)" in unit_name
        # must save memory
        self.url_to_tables.pop("characters/growth-rates")
        #self.url_to_tables.pop("characters/base-stats")

    @property
    def unit_name(self) -> str:
        """
        The name of the unit whose stats are to be queried.
        """
        return self._unit_name

    def copy(self):
        """
        Returns a copy of self, with stat attributes, history,  and so forth.
        For use in web-development.
        """
        # economize on stuff to copy
        self.target_stats = None
        return copy.deepcopy(self)

    def level_up(self, target_lv: int):
        """
        Increases unit's level, and increments current_stats accordingly.
        Raises:
        - ValueError: (target_lv <= current_lv) or (target_lv > max_lv)
        """
        if target_lv > self.get_maxlv() or target_lv <= self.current_lv:
            if target_lv > self.get_maxlv():
                error_msg = f"The target level of {target_lv} exceeds the max level of {self.get_maxlv()}."
            else:
                error_msg = f"The target level of {target_lv} is less than or equal to the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        logging.info("Morph.level_up(%d)", target_lv)
        temp_growths = self.growth_rates.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)
        self.current_lv = target_lv

    def promote(self, tableindex: int = 0):
        """
        Applies promotion bonuses, then changes classes.
        Raises:
        - ValueError: Minimum promotion level not attained.
        - ValueError: Unit cannot promote.
        Sets:
        - current_stats += promo_bonus
        - history += (old_class, old_lv)
        - promo_cls = None
        - current_clstype = 'classes/promotion-gains'
        """
        # query for available promotions
        if self.current_clstype == "characters/base-stats":
            lindex_val = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lindex_val = self.current_cls
        self.lookup(
            (self.current_clstype, lindex_val),
            ("classes/promotion-gains", "Class"),
            tableindex,
        )
        if self.target_stats is None:
            raise ValueError(f"{self.unit_name} has no available promotions.")
        # check if unit is high enough a level to promote
        if self.current_lv < self.get_minpromolv():
            raise ValueError(f"{self.unit_name} must be at least level {self.get_minpromolv()} to promote. Current level: {self.current_lv}")
        logging.info("Morph.promote(tableindex=%d)", tableindex)
        # store for history
        old_cls = self.current_cls
        self.history.append( (old_cls, self.current_lv) )
        # if there is more than one result, get right statset
        # set current class
        if isinstance(self.target_stats, pd.DataFrame):
            try:
                self.target_stats = self.target_stats.set_index("Promotion").loc[self.promo_cls, :]
            except KeyError as key_err:
                print("Please select a valid promotion class:", self.target_stats["Promotion"].drop_duplicates().to_list())
                raise key_err
            # raises KeyError for split-promotions; utilize to advantage (i.e. SELECT from target_stats.loc[:, "Promotion"])
            self.current_cls = self.target_stats.name
        else:
            self.current_cls = self.target_stats.pop("Promotion")
        # set class to promote to to None
        self.promo_cls = None
        # change current_clstype for future queries
        self.current_clstype = "classes/promotion-gains"
        # increment stats
        temp_promo = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        self.current_stats += temp_promo
        # reset level
        self.current_lv = 1

    def cap_stats(self, tableindex: int = 0):
        """
        Caps a unit's current_stats in accordance with the class's maximum stats.
        """
        if self.current_clstype == "characters/base-stats":
            lindex_val = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lindex_val = self.current_cls
        self.lookup(
            (self.current_clstype, lindex_val),
            ("classes/maximum-stats", "Class"),
            tableindex,
        )
        logging.info("Morph.cap_stats(tableindex=%d)", tableindex)
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        self.current_stats.mask(self.current_stats > temp_maxes, other=temp_maxes, inplace=True)
        self.current_stats.mask(self.current_stats < 0, other=0, inplace=True)

    def __repr__(self) -> str:
        """
        Returns a pd.Series-str summarizing the stats, history, and more about a Morph instance.
        Raises:
        - no errors, hurrah!
        Returns a pd.Series-str of the form:
        - Name
        - {history}
        - Class
        - Lv
        - {numeric_stats}
        """
        return self.get_repr_series(["history", "comparison_labels"]).to_string()

    def get_repr_series(self, detail_list=()) -> pd.Series:
        """
        Creates the pd.Series for implementation in the __repr__ dunder.
        See Morph.__repr__ docstring for more information.
        """
        # create header rows
        header_rows = OrderedDict()
        header_rows["Name"] = self.unit_name.replace(" (HM)", "")
        if "comparison_labels" in detail_list:
            header_rows.update(self.comparison_labels)
        if "history" in detail_list:
            for index, entry in enumerate(self.history):
                header_rows["PrevClassLv" + str(index + 1)] = entry
        header_rows["Class"] = self.current_cls
        header_rows["Lv"] = self.current_lv
        return pd.concat([pd.Series(header_rows), self.current_stats])

    # TODO: Test this!
    def override_stats(self):
        """
        Accepts user input to update 'current_stats' attribute.
        """
        stat_labels = self.current_stats.index
        new_stats = {}
        def is_float(user_str: str):
            """
            Returns True if 'user_str' is a valid, finite float.
            """
            try:
                user_num = float(user_str)
                illegal_nums = (float('inf'), float('-inf'), float('nan'))
                return user_num not in illegal_nums
            except ValueError:
                return False
        for stat_label in stat_labels:
            new_stat = ""
            while not is_float(new_stat):
                new_stat = input("Please input a new '%s' value: " % stat_label)
            new_numstat = float(new_stat)
            new_stats[stat_label] = new_numstat
        self.current_stats = pd.Series(data=new_stats)

    def __lt__(self, other) -> pd.DataFrame:
        """
        Returns a pd.DataFrame summarizing the difference between one Morph and another.
        Raises:
        - no errors, hurrah!
        Returned pd.DataFrame is of the form:
        - {history}
        - Class
        - Lv
        - {numeric_stats}
        with name = self.unit_name
        """
        # TODO: Check out the orders and stuff. order is inverted.
        return other.__gt__(self)


class Morph4(Morph):
    """
    Inherits: aenir.morph.Morph.

    Modifies existing methods for collection of units in FE4.
    """

    url_to_tables = {}

    def __init__(self, unit_name: str, father_name: str = None):
        """
        Extends: Morph.__init__ (conditionally).

        FE4 child unit parameters are reinitialized using methods adopted from Morph superclass.
        Defines: father_name
        """
        game_num = 4
        BaseMorph.__init__(self, game_num)
        # inherits from Morph, which declares this a property
        #self.unit_name = unit_name
        try:
            assert unit_name in self.get_character_list()
        except AssertionError:
            raise KeyError(f"'{unit_name}' is not in the list of FE4 units: {self.get_character_list()}.")
        kid_tableindex = 1
        self.is_kid = unit_name in self.url_to_tables["characters/base-stats"][kid_tableindex]["Name"].to_list()
        if self.is_kid:
            self._father_name = father_name
        else:
            self._father_name = None
        logging.info("Morph4('%s', '%s')", unit_name, father_name)
        if self.is_kid:
            # initialize bases
            try:
                temp_bases = self.url_to_tables["characters/base-stats"][kid_tableindex].set_index(["Name", "Father"]).loc[(unit_name, father_name), :]
            except KeyError as unit_dne_err:
                father_list = list(self.url_to_tables.pop("characters/base-stats")[kid_tableindex]["Father"].unique())
                print(f"'{father_name}' is not in the list of FE4 fathers: {self.get_character_list()}.")
                raise unit_dne_err
            self.current_cls = temp_bases.pop("Class")
            self.current_lv = temp_bases.pop("Lv")
            self.current_stats = temp_bases + 0.0
            self.current_stats.name = unit_name
            self._unit_name = unit_name
            self.current_clstype = "characters/base-stats"
            # implicitly convert to float
            self.comparison_labels.update({"Father": father_name})
            self.growth_rates = self.url_to_tables.pop("characters/growth-rates")[kid_tableindex].set_index(["Name", "Father"]).loc[(self.unit_name, self.father_name), :]
        else:
            Morph.__init__(self, game_num, unit_name, tableindex=0)
        try:
            self.promo_cls = self.BRANCHED_PROMO_EXCEPTIONS[(game_num, unit_name)]
        except KeyError:
            self.promo_cls = None

    def get_maxlv(self) -> int:
        """
        Determines the maximum level for a given unit.
        """
        if self.current_clstype == "characters/base-stats":
            lindex_val = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lindex_val = self.current_cls
        tableindex = 0
        self.set_targetstats(
            (self.current_clstype, lindex_val),
            ("classes/promotion-gains", "Class"),
            tableindex,
        )
        if self.target_stats is None: # a.k.a. cannot promote
            maxlv = 30
        else:
            maxlv = 20
        return maxlv


    @property
    def unit_name(self) -> str:
        """
        The name of the unit whose stats are to be queried.
        """
        return self._unit_name

    @property
    def father_name(self) -> str:
        """
        The name of the father of the unit whose stats are to be queried.
        """
        return self._father_name

    def level_up(self, target_lv: int):
        """
        Extends: Morph.level_up (conditionally).

        Method for FE4 kids has a different implementation.
        Raises:
        - ValueError: (target_lv <= current_lv) or (target_lv > max_lv)
        """
        if target_lv > self.get_maxlv() or target_lv <= self.current_lv:
            if target_lv > self.get_maxlv():
                error_msg = f"The target level of {target_lv} exceeds the max level of {self.get_maxlv()}."
            else:
                error_msg = f"The target level of {target_lv} is less than the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        # target_stats is set directly instead via the usual method.
        logging.info("Morph4.level_up(%d)", target_lv)
        if self.is_kid:
            temp_growths = self.growth_rates.reindex(self.current_stats.index, fill_value=0.0)
            self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)
            self.current_lv = target_lv
        else:
            Morph.level_up(self, target_lv)

    def promote(self):
        """
        Extends: Morph.promote.

        Resets level to previous state pre-promotion.
        """
        previous_lv = self.current_lv
        Morph.promote(self, tableindex=0)
        self.current_lv = previous_lv


class Morph5(Morph):
    """
    Inherits: aenir.morph.Morph.
   
    Defines promotion exceptions, and extends level_up method.
    """

    url_to_tables = {}

    def __init__(self, unit_name: str):
        """
        Extends: Morph.__init__.

        Defines: equipped_scrolls := List[str]
        """
        game_num = 5
        Morph.__init__(self, game_num, unit_name, tableindex=0)
        self.equipped_scrolls = []

    def promote(self):
        """
        Extends: Morph.promote.

        Defines exceptions for Lara, who has two different promotion paths:
        - Thief -> Thief Fighter -> Dancer -> Thief Fighter
        - Thief -> Dancer -> Thief Fighter
        Ensures that Parne and Lifis don't promote into Dancers.
        Ensures that Lara receives the right promotions.
        """
        logging.info("Morph5.promote()")
        clslist = (cls for cls, lv in self.history)
        if self.current_cls == "Thief Fighter" and self.unit_name != "Lara":
            raise ValueError(f"{self.unit_name} has no available promotions.")
        elif self.unit_name == "Lara" and "Dancer" in clslist:
            raise ValueError(f"{self.unit_name} has no available promotions.")
        Morph.promote(self)

    def level_up(self, target_lv: int):
        """
        Extends: Morph.level_up

        Enables user to simulate scroll-boosted level-ups if equipped_scrolls list parameter is valid.
        """
        # pasted from Morph.level_up
        if target_lv > self.get_maxlv() or target_lv <= self.current_lv:
            if target_lv > self.get_maxlv():
                error_msg = f"The target level of {target_lv} exceeds the max level of {self.get_maxlv()}."
            else:
                error_msg = f"The target level of {target_lv} is less than or equal to the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        if self.equipped_scrolls:
            maximum_inventory_size = 7
            assert len(self.equipped_scrolls) <= 7
            temp_scrollbonus = pd.Series(index=self.current_stats.index, data=[0.0 for label in self.current_stats.index])
            # fetch table name, and table file
            load_path = self.home_dir.joinpath(self.tables_file)
            if not load_path.exists():
                raise FileNotFoundError(f"'{str(load_path)}' does not exist. Aborting.")
            load_file = str(load_path)
            table_name = "crusader_scrolls"
            con = "sqlite:///" + load_file
            scroll_table = pd.read_sql_table(table_name, con).set_index("Name")
            # accumulate bonuses
            for scroll_name in self.equipped_scrolls:
                try:
                    temp_scrollbonus += scroll_table.loc[scroll_name, :]
                except KeyError as keyerr:
                    print(f"'{scroll_name}' is not a valid Crusader name. Choose from the list: {list(scroll_table.index)}")
                    raise keyerr
            # cap bonus at zero if growths < 0
            #temp_scrollbonus.mask(temp_scrollbonus < 0, other=0, inplace=True)
            # increment
            self.current_stats += (temp_scrollbonus / 100) * (target_lv - self.current_lv)
        Morph.level_up(self, target_lv)

class Morph7(Morph):
    """
    Inherits: aenir.morph.Morph. Serves mainly to accommodate for Lyn Mode units.
    """

    url_to_tables = {}

    def __init__(self, unit_name: str, lyn_mode: bool = False):
        """
        Extends: Morph.__init__.

        - Adds promotion exception for Wallace
        - Allows user to choose Lyn Mode or otherwise
        """
        game_num = 7
        # if the user lists a non-LM unit, but puts lyn_mode=True, the program halts
        Morph.__init__(self, game_num, unit_name, tableindex=(0 if lyn_mode else 1))
        logging.info("Morph7.__init__('%s', %s)", unit_name, lyn_mode)
        self.lyn_mode = None
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
        if unit_name in lyndis_league:
            self.comparison_labels.update({"Campaign": ("Main" if not lyn_mode else "Tutorial")})
            self.lyn_mode = lyn_mode
        # TODO: minor patch. should provide permanent solution
        if not lyn_mode and unit_name == "Wallace":
            # must add in line with 'General (M)' -> None in promo-JOIN-promo JSON file
            self.current_clstype = "classes/promotion-gains"


# to interface with web-deploy layer better.
class Morph6(Morph):
    """
    Inherits: aenir.morph.Morph
    """

    url_to_tables = {}

    def __init__(self, unit_name: str):
        """
        Extends: Morph.__init__
        - game_num: 6
        """
        game_num = 6
        Morph.__init__(self, game_num, unit_name, tableindex=0)


class Morph8(Morph):
    """
    Inherits: aenir.morph.Morph
    """

    url_to_tables = {}

    def __init__(self, unit_name: str):
        """
        Extends: Morph.__init__
        - game_num: 8
        """
        game_num = 8
        Morph.__init__(self, game_num, unit_name, tableindex=0)


class Morph9(Morph):
    """
    Inherits: aenir.morph.Morph
    """

    url_to_tables = {}

    def __init__(self, unit_name: str):
        """
        Extends: Morph.__init__
        - game_num: 9
        """
        game_num = 9
        Morph.__init__(self, game_num, unit_name, tableindex=0)


    def cap_stats(self, *args):
        """
        """

    def get_maxlv(self) -> int:
        """
        Determines the maximum level for a given unit.
        """
        if self.game_num == 4:
            maxlv = 30
        elif self.unit_name in ("Ross", "Amelia", "Ewan") and not self.history:
            maxlv = 10
        else:
            maxlv = 20
        return maxlv

    def level_up(self, num_levels, *args):
        """
        """

    def get_minpromolv(self) -> int:
        """
        Determines the minimum promotion level for a given unit.
        All exceptional units are logged here.
        """
        if self.game_num == 4:
            minpromolv = 20
        elif (self.game_num, self.unit_name, self.promo_cls) == (5, "Lara", "Dancer"):
            # for Lara shenanigans
            minpromolv = 1
        else:
            try:
                minpromolv = {
                    (6, "Roy"): 1,
                    (7, "Hector"): 1,
                    (7, "Eliwood"): 1,
                    (5, "Linoan"): 1,
                    (5, "Leif"): 1,
                }[(self.game_num, self.unit_name)]
            except KeyError:
                minpromolv = 10
        return minpromolv

    def promote(self, *args):
        """
        """
        page_dict = {
            "classes/promotion-gains": "classes__promotion_gains",
        }
        promo_gains = None

    def __eq__(self, other):
        """
        Defines how two Morph objects are equal.
        Conditions:
        - Stats are equal
        - Game and unit names are the same
        - Classes and levels are the same
        - History is identical
        - Other attributes are the same.
        """
        stats_are_compatible = all(self.current_stats.index == other.current_stats.index)
        stats_are_equal = all(abs(self.current_stats - other.current_stats) < 0.01)
        scalar_attrs = [
            "unit_name",
            "game_num",
            "history",
            "comparison_labels",
            "current_cls",
            "current_lv",
            "current_clstype",
        ]
        equality_conditions = [stats_are_compatible, stats_are_equal]
        for attr in scalar_attrs:
            equality_conditions.append(
                getattr(self, attr) == getattr(other, attr)
            )
        return all(equality_conditions)

    def is_maxed(self, tableindex: int = 0) -> pd.Series:
        """
        Returns a pd.Series showing which of the Morph's stats are maxed.
        """
        if self.current_clstype == "characters/base-stats":
            lindex_val = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lindex_val = self.current_cls
        self.lookup(
            (self.current_clstype, lindex_val),
            ("classes/maximum-stats", "Class"),
            tableindex,
        )
        logging.info("Morph.is_maxed(tableindex=%d)", tableindex)
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        return temp_maxes == self.current_stats

    def __gt__(self, other) -> pd.DataFrame:
        """
        Returns a pd.DataFrame summarizing the difference between one Morph and another.
        Raises:
        - no errors, hurrah!
        Returned pd.DataFrame is of the form:
        - {history}
        - Class
        - Lv
        - {numeric_stats}
        with name = self.unit_name
        """
        # naming logistics here
        self_currentstats_name = self.unit_name.replace(" (HM)", "")
        other_currentstats_name = other.unit_name.replace(" (HM)", "")
        if other_currentstats_name == self_currentstats_name:
            other_currentstats_name += " (2)"
        diff = other.current_stats - self.current_stats
        diff.name = 'diff'
        #old_selfname, old_othername = self.current_stats.name, other.current_stats.name
        self_current_stats = self.current_stats.copy()
        other_current_stats = other.current_stats.copy()
        self_current_stats.name = self_currentstats_name
        other_current_stats.name = other_currentstats_name
        #self.current_stats.name = self_currentstats_name
        #other.current_stats.name = other_currentstats_name
        # create stat_df
        stat_df = pd.concat(
            [
                self_current_stats,
                diff,
                other_current_stats,
            ],
            axis=1,
        )
        # create clslv_rows
        self_clslv = [self.current_cls, self.current_lv]
        other_clslv = [other.current_cls, other.current_lv]
        # create history_rows
        max_histlen = max([len(self.history), len(other.history)])
        for index in range(max_histlen):
            self_clslv.insert(0, "-")
            other_clslv.insert(0, "-")
        for index, entry in enumerate(self.history):
            self_clslv[index] = entry
        for index, entry in enumerate(other.history):
            other_clslv[index] = entry
        #self_currentstats_name = self.current_stats.name.replace(" (HM)", "")
        #other_currentstats_name = other.current_stats.name.replace(" (HM)", "")
        clslv_df = pd.DataFrame(
            {
                self_currentstats_name: self_clslv,
                diff.name: ['-' for entry in self_clslv],
                other_currentstats_name: other_clslv,
            },
            index=["PrevClassLv" + str(index + 1) for index in range(max_histlen)] + ['Class', 'Lv']
        )
        # create rows for comparison_labels
        meta_labels = list(self.comparison_labels)
        for row_label in other.comparison_labels:
            if row_label in meta_labels:
                continue
            meta_labels.append(row_label)
        meta_map = {
            self_currentstats_name: self.comparison_labels,
            diff.name: {},
            other_currentstats_name: other.comparison_labels,
        }
        meta_rows = pd.DataFrame(meta_map, index=meta_labels).fillna("-")
        # This does not fail because (*.current_stats.name == *_currentstats_name)
        #stat_df[self.current_stats.name].name = self_currentstats_name
        #stat_df[other.current_stats.name].name = other_currentstats_name
        # Calculate cdiff.
        # TODO: Test this!
        csum_label = "-Cumulative-"
        csum_row = pd.DataFrame(
            {
                self_currentstats_name: {csum_label: ""},
                diff.name: {csum_label: round(sum(diff), 2)},
                other_currentstats_name: {csum_label: ""},
            }
        )
        comparison_df = pd.concat([meta_rows, clslv_df, stat_df, csum_row])
        #other.current_stats.name = other.current_stats.name.replace(" (2)", "")
        #self.current_stats.name, other.current_stats.name = old_selfname, old_othername
        return comparison_df
