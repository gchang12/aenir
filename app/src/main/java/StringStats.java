import java.util.LinkedHashMap;

class StringStats {
    public static void main(String[] args) {
        Stats s = new Stats();
        s.imul(9);
    }
}

interface StatOperations {
    static String[] STAT_LIST = null;
    static String[] ZERO_GROWTH_STAT_LIST = null;
    LinkedHashMap<String, Integer> core = null;

    default void imul(int factor) {
        for (String key: core.keySet()) {
            System.out.println(key);
        }
    }
}

class Stats implements StatOperations {
    static String[] STAT_LIST = {
        "HP",
        "Str",
        "Mag",
        "Skl",
        "Spd",
    };
    static String[] ZERO_GROWTH_STAT_LIST = {
        "Spd",
    };
    LinkedHashMap<String, Integer> core;
    Stats() {
        LinkedHashMap<String, Integer> core = new LinkedHashMap<>();
        core.put("HP", 0);
    }
}
