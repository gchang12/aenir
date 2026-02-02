package aenir;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;

class StatsDemo {
    public static void main(String[] args) {
        HashMap<String, Integer> hm = new HashMap<>();
        hm.put("HP", 0);
        Stats<GenealogyOfTheHolyWar> stats = new Stats<>();
        stats.fill(0);
        System.out.println(stats.core);
    }
}

class Stats<G extends Game> /*implements Map*/ {
    EnumMap<G.StatList, Integer> core;
    Stats() {
        EnumMap<G.StatList, Integer> core = new EnumMap<>(G.StatList.class);
        this.core = core;
        core.put(G.StatList.HP, 0);
        System.out.println(core);
    };
    Integer get(String key) {
        G.StatList normalizedKey = G.StatList.valueOf(key);
        return core.get(normalizedKey);
    };
    Integer put(String key, Integer value) {
        G.StatList normalizedKey = G.StatList.valueOf(key);
        return core.put(normalizedKey, value);
    };
    void fill(Integer value) {
        for (G.StatList normalizedKey: core.keySet()) {
            System.out.println(normalizedKey);
            this.core.put(normalizedKey, value);
        };
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

