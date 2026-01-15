import java.util.Map;
import java.util.LinkedHashMap;

class StatsDemo {
    public static void main(String[] args) {
        System.out.println("Hello world.");
        RadiantStats ike = new RadiantStats();
    }
}

/**
Defines methods for comparison, setting, and incrementation of numerical stats.
*/
class Stats {

    /**
    A kernel of the class; expects an array of the names of all stats.
    */
    static String[] STAT_LIST = null;

    /**
    A kernel of the class; expects an array of the names of stats that have zero growth rates.
    */
    static String[] ZERO_GROWTH_STAT_LIST = null;

    /**
    A kernel of the class; expects an array of the names of all stats.
    */
    int[] statValues = {};

    /**
    */
    private static int index(String arr[], String t, int start) {
        if (start == arr.length) {
            return -1;
        };
        // if element at index start equals t
        // we return start
        if (arr[start] == t)
            return start;
        return index(arr, t, start + 1);
    };

    /**
    */
    private static int findStat(String[] arr, String t, int[] values) throws ArrayIndexOutOfBoundsException {
        int stringLoc = index(arr, t, 0);
        try {
            return values[stringLoc];
        } catch (ArrayIndexOutOfBoundsException e) {
            throw e;
        }
    };

    /**
    Helper class for tests to retrieve stat values
    */
    int get(String statName) {
        int statValue = findStat(STAT_LIST, statName, statValues);
        return statValue;
    };

    /**
    Returns key-val pairs of stats as Map object.
    */
    Map<String, Integer> asMap() {
        Map<String, Integer> statsAsMap = new LinkedHashMap<>();
        for (int i=0; i<STAT_LIST.length; i++) {
            statsAsMap.put(STAT_LIST[i], statValues[i]);
        };
        return statsAsMap;
    };

    /**
    Returns key-val pairs of stats as list of 2-tuples.
    */
    Map<String, Integer> asList() {
        Map<String, Integer> statsAsList = new LinkedHashMap<>();
        for (int i=0; i<STAT_LIST.length; i++) {
            statsAsList.put(STAT_LIST[i], statValues[i]);
        };
        return statsAsList;
    };

    /**
    Reads current stats, multiplies each stat by a scalar, then returns the result in a new Stats object.
    */
    void imul(int factor) {
        for (int i=0; i<STAT_LIST.length; i++) {
            this.statValues[i] *= factor;
        };
    };

    /**
    Sets each stat in `this` to minimum of itself and corresponding stat in `that`.
    */
    void imin(Stats that) {
        int statValue;
        for (int i=0; i<STAT_LIST.length; i++) {
            statValue = findStat(that.STAT_LIST, this.STAT_LIST[i], that.statValues);
            this.statValues[i] = Math.min(this.statValues[i], statValue);
        };
    };

    /**
    Sets each stat in `this` to maximum of itself and corresponding stat in `that`.
    */
    void imax(Stats that) {
        int statValue;
        for (int i=0; i<STAT_LIST.length; i++) {
            statValue = findStat(that.STAT_LIST, this.STAT_LIST[i], that.statValues);
            try {
                this.statValues[i] = Math.max(this.statValues[i], statValue);
            } catch (ArrayIndexOutOfBoundsException e) {
                System.err.println("'" + this.STAT_LIST[i] + "' not in `that` STAT_LIST.");
                throw e;
            };
        };
    };

    /**
    Increments values of `this` by corresponding values in `that`.
    */
    void iadd(Stats that) {
        int statValue;
        for (int i=0; i<STAT_LIST.length; i++) {
            statValue = findStat(that.STAT_LIST, this.STAT_LIST[i], that.statValues);
            this.statValues[i] = this.statValues[i] + statValue;
        };
    };

    /**
    Obtains difference of growable stats of two Stats objects and returns the result in a new Stats object.
    Error is thrown if the Stats objects are not of the same type.
    */
    void isub(Stats that) {
        int statValue;
        for (int i=0; i<STAT_LIST.length; i++) {
            statValue = findStat(that.STAT_LIST, this.STAT_LIST[i], that.statValues);
            this.statValues[i] = this.statValues[i] - statValue;
        };
    };

    /**
    Returns iterable of stats with growth rates.
    */
    static String[] /* Stats */ getGrowableStats() {
        // TODO: Replace with actual blah blah blah.
        // return filter(lambda stat_: stat_ not in cls.ZERO_GROWTH_STAT_LIST(), cls.STAT_LIST())
        /* return STAT_LIST.filter(ZERO_GROWTH_STAT_LIST); */
        String[] growableStats = {"", ""};
        return growableStats;
    };

    /**
    Returns pretty-printed str-list of stats.
    */
    public final String toString() {
        return "";
        /*
        statlist = self.as_list()
        #format_str = "% 4s: %5.2s"
        def get_formatted_statlist(statval):
            """
            """
            format_str = "% 4s: %5.2f"
            field, value = statval
            value = value or 0
            return format_str % (field, value * 0.01)
        statlist_as_str = "\n".join(get_formatted_statlist(statval) for statval in statlist)
        header = self.__class__.__name__
        header_border = len(header) * "="
        statlist_as_str = "\n".join([header, header_border, statlist_as_str])
        return statlist_as_str
        */
    };

    /**
    Alerts user of which stats want declaration if `stat_dict` is incomplete.
    Warns user about unused kwargs.
    */
    /* Stats(Map<String, Integer> statMap) { */
        // TODO: Replace with actual thing.
        /*
        # check if statlist in statdict
        statlist = self.STAT_LIST()
        if not isinstance(statlist, tuple):
            raise NotImplementedError("`STAT_LIST` must return a tuple; instead it returns a %r", type(statlist))
        expected_stats = set(statlist)
        actual_stats = set(stat_dict)
        if not expected_stats.issubset(actual_stats):
            # get list of missing keywords and report to user
            def by_statlist_ordering(stat):
                """
                Returns position of `stat` in `cls.STAT_LIST()`.
                """
                return statlist.index(stat)
            missing_stats = sorted(
                expected_stats - actual_stats,
                key=by_statlist_ordering,
            )
            raise AttributeError("Please supply values for the following stats: %s" % missing_stats)
        # initialize
        for stat in statlist:
            stat_value = stat_dict[stat]
            if isinstance(stat_value, int):
                stat_value *= multiplier
            setattr(self, stat, stat_value)
        # warn user of unused kwargs
        unused_stats = set(stat_dict) - set(statlist)
        if unused_stats:
            logger.warning("These keyword arguments have gone unused: %s", unused_stats)
        */
    /* }; */

};

/**
Declares stats used for FE4: Genealogy of the Holy War.
*/
final class GenealogyStats extends Stats {
    static final String[] STAT_LIST = {
        "HP",
        "Str",
        "Mag",
        "Skl",
        "Spd",
        "Lck",
        "Def",
        "Res"
    };
    static final String[] ZERO_GROWTH_STAT_LIST = {};
};

/**
Declares stats used for FE5: Thracia 776.
*/
final class ThraciaStats extends Stats {
    static final String[] STAT_LIST = {
        "HP",
        "Str",
        "Mag",
        "Skl",
        "Spd",
        "Lck",
        "Def",
        "Con",
        "Mov",
        "Lead",
        "MS",
        "PC"
    };
    static final String[] ZERO_GROWTH_STAT_LIST = {
        "Lead",
        "MS",
        "PC"
    };
};

/**
Declares stats used for FE6, FE7, and FE8.
*/
final class GBAStats extends Stats {
    static final String[] STAT_LIST = {
        "HP",
        "Pow",
        "Skl",
        "Spd",
        "Lck",
        "Def",
        "Res",
        "Con",
        "Mov"
    };
    static final String[] ZERO_GROWTH_STAT_LIST = {
        "Con",
        "Mov"
    };
};

/**
Declares stats used for FE9.
*/
final class RadiantStats extends Stats {
    static final String[] STAT_LIST = {
        "HP",
        "Str",
        "Mag",
        "Skl",
        "Spd",
        "Lck",
        "Def",
        "Res",
        "Mov",
        "Con",
        "Wt"
    };
    static final String[] ZERO_GROWTH_STAT_LIST = {
        "Mov",
        "Con",
        "Wt"
    };
};

