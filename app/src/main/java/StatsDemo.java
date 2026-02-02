package aenir;

import java.lang.Enum;
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

class Stats<K extends Enum> {
    EnumMap<K, Integer> core;
    Stats() {
        EnumMap<K, Integer> core = new EnumMap<>(K.class);
        this.core = core;
        core.put(K.HP, 0);
        System.out.println(core);
    };
    Integer get(String key) {
        K normalizedKey = K.valueOf(key);
        return core.get(normalizedKey);
    };
    Integer put(String key, Integer value) {
        K normalizedKey = K.valueOf(key);
        return core.put(normalizedKey, value);
    };
    void fill(Integer value) {
        for (K normalizedKey: core.keySet()) {
            System.out.println(normalizedKey);
            this.core.put(normalizedKey, value);
        };
    };
    void putAll(Map<String, Integer> m) {
        K normalizedKey;
        Integer value;
        for (String key: m.keySet()) {
            normalizedKey = K.valueOf(key);
            value = m.get(key);
            core.put(normalizedKey, value);
        };
    };
}

enum GenealogyOfTheHolyWar {
    HP,
    Str,
    Mag,
    Skl,
    Spd,
    Lck,
    Def,
    Res;
    boolean isGBAGame = false;
    static String[] ZERO_GROWTH_STAT_LIST = {
    };
}

/*

abstract class Game {
    enum StatList {};
    enum ZeroGrowthStatList {};
    boolean isGBAGame;
}
class Thracia776 extends Game {
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
    enum ZeroGrowthStatList {
        Lead,
        MS,
        PC;
    }
}
class SwordOfSeals extends Game {
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
    enum ZeroGrowthStatList {
        Con,
        Mov;
    };
}
class BlazingSword extends Game {
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
    enum ZeroGrowthStatList {
        Con,
        Mov;
    };
}
class TheSacredStones extends Game {
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
    enum ZeroGrowthStatList {
        Con,
        Mov;
    };
}
class PathOfRadiance extends Game {
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
    boolean isGBAGame = false;
    enum ZeroGrowthStatList {
        Mov,
        Con,
        Wt;
    };
}
*/
