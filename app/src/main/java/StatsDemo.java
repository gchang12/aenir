package aenir;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;

class StatsDemo {
    public static void main(String[] args) {
        HashMap<String, Integer> hm = new HashMap<>();
        hm.put("HP", 18);
        Stats<GenealogyOfTheHolyWar> stats = new Stats<>(hm);
    }
}

class Stats<G extends Game> /*implements Map*/ {
    EnumMap<G.StatList, Integer> core;
    Stats(Map<String, Integer> kwargs) {
        EnumMap<G.StatList, Integer> core = new EnumMap<>(G.StatList.class);
        // for each kwarg in kwargs
    };
    Integer get(String key) {
        G.StatList normalizedKey = G.StatList.valueOf(key);
        return core.get(normalizedKey);
    };
    Integer put(String key, Integer value) {
        G.StatList normalizedKey = G.StatList.valueOf(key);
        return core.put(normalizedKey, value);
    };
    void putAll(Map<String, Integer> m) {
        G.StatList normalizedKey;
        Integer value;
        for (String key: m.keySet()) {
            normalizedKey = G.StatList.valueOf(key);
            value = m.get(key);
            core.put(normalizedKey, value);
        };
    };
        /* for (String key: kwargs.keySet()) { */
            // load value into `value` if key is present
            /* System.out.println(key); */
            /* System.out.println(kwargs.get(key)); */
            /* G.StatList.valueOf(G.StatList.class, key); */
            // o.w. raise error.
        /* } */
    /* } */
}

abstract class Game {
    enum StatList {};
    enum ZeroGrowthStatList {};
    boolean isGBAGame;
}

class GenealogyOfTheHolyWar extends Game {
    /**
      Stat list for FE4: Genealogy of the Holy War
    */
    enum StatList {
        HP,
        Str,
        Mag,
        Skl,
        Spd,
        Lck,
        Def,
        Res;
    }
    boolean isGBAGame = false;
    /**
      List of stats that have zero growths.
    */
    static String[] ZERO_GROWTH_STAT_LIST = {
    };
}

class Thracia776 extends Game {
    /**
      Stat list for FE5: Thracia 776
    */
    enum StatList {
        HP,
        Str,
        Mag,
        Skl,
        Spd,
        Lck,
        Def,
        Con,
        Mov,
        Lead,
        MS,
        PC;
    }
    boolean isGBAGame = false;
    /**
      List of stats that have zero growths.
    */
    enum ZeroGrowthStatList {
        Lead,
        MS,
        PC;
    }
}

class SwordOfSeals extends Game {
    /**
      Stat list for FE6: Sword of Seals
    */
    enum StatList {
        HP,
        Pow,
        Skl,
        Spd,
        Lck,
        Def,
        Res,
        Con,
        Mov;
    }
    boolean isGBAGame = true;
    /**
      List of stats that have zero growths.
    */
    enum ZeroGrowthStatList {
        Con,
        Mov;
    };
}

class BlazingSword extends Game {
    /**
      Stat list for FE7: Blazing Sword
    */
    enum StatList {
        HP,
        Pow,
        Skl,
        Spd,
        Lck,
        Def,
        Res,
        Con,
        Mov;
    }
    boolean isGBAGame = true;
    /**
      List of stats that have zero growths.
    */
    enum ZeroGrowthStatList {
        Con,
        Mov;
    };
}


class TheSacredStones extends Game {
    /**
      Stat list for FE8: The Sacred Stones
    */
    enum StatList {
        HP,
        Pow,
        Skl,
        Spd,
        Lck,
        Def,
        Res,
        Con,
        Mov;
    }
    boolean isGBAGame = true;
    /**
      List of stats that have zero growths.
    */
    enum ZeroGrowthStatList {
        Con,
        Mov;
    };
}

class PathOfRadiance extends Game {
    /**
      Stat list for FE9: Path of Radiance
    */
    enum StatList {
        HP,
        Str,
        Mag,
        Skl,
        Spd,
        Lck,
        Def,
        Res,
        Mov,
        Con,
        Wt;
    }
    /**
      List of stats that have zero growths.
    */
    boolean isGBAGame = false;
    enum ZeroGrowthStatList {
        Mov,
        Con,
        Wt;
    };
}

