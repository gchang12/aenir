import java.util.Map;
import java.util.LinkedHashMap;

class Stats2 {
    public static void main(String[] args) {
        System.out.println("Too much pressure.");
    }
}

abstract class Stats implements Map {
}

class RadiantStats extends Stats {
    /**
      Stat list for FE9: Path of Radiance
    */
    entrySet() {
    }
    static String[] STAT_LIST = {
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
        "Wt",
    };
    /**
      List of stats that have zero growths.
    */
    static String[] ZERO_GROWTH_STAT_LIST = {
        "Mov",
        "Con",
        "Wt",
    };
}
