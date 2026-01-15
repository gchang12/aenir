package aenir;

public enum FireEmblemGame {
    GENEALOGY_OF_THE_HOLY_WAR(4),
    THRACIA_776(5),
    SWORD_OF_SEALS(6),
    BLAZING_SWORD(7),
    THE_SACRED_STONES(8),
    PATH_OF_RADIANCE(9);

    public final int gameNo;

    FireEmblemGame(int gameNo) {
        this.gameNo = gameNo;
    };

    public String getUrlName() {
        return switch(this) {
            case GENEALOGY_OF_THE_HOLY_WAR -> "genealogy-of-the-holy-war";
            case THRACIA_776 -> "thracia-776";
            case SWORD_OF_SEALS -> "binding-blade";
            case BLAZING_SWORD -> "blazing-sword";
            case THE_SACRED_STONES -> "the-sacred-stones";
            case PATH_OF_RADIANCE -> "path-of-radiance";
        };
    };

    public String getFormalName() {
        return switch(this) {
            case GENEALOGY_OF_THE_HOLY_WAR -> "Genealogy of the Holy War";
            case THRACIA_776 -> "Thracia 776";
            case SWORD_OF_SEALS -> "Sword of Seals";
            case BLAZING_SWORD -> "Blazing Sword";
            case THE_SACRED_STONES -> "The Sacred Stones";
            case PATH_OF_RADIANCE -> "Path of Radiance";
        };
    };

    public boolean isGBAGame() {
        boolean isGBA;
        switch(this) {
            case SWORD_OF_SEALS:
            case BLAZING_SWORD:
            case THE_SACRED_STONES:
                isGBA = true;
                break;
            default:
                isGBA = false;
        };
        return isGBA;
    };

};
