import java.util.EnumMap;
import java.util.Map;

class EnumStats {
    public static void main(String[] args) {
        System.out.println("I've felt dead for the longest time.");
    }
}

enum RadiantStats {
    HP, Str, Mag;
}

class Stats {
    EnumMap<RadiantStats, Integer> core = null;
    Stats() {
        EnumMap<RadiantStats, Integer> core = new EnumMap<>();
        core.put(RadiantStats.HP, 0);
        core.put(RadiantStats.Str, 0);
        core.put(RadiantStats.Mag, 0);
    }
}
