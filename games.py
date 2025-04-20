import enum

class FireEmblemGame(enum.IntEnum):
    """
    """
    GENEALOGY_OF_THE_HOLY_WAR = 4
    THRACIA_776 = enum.auto()
    SWORD_OF_SEALS = enum.auto()
    BLAZING_SWORD = enum.auto()
    THE_SACRED_STONES = enum.auto()
    PATH_OF_RADIANCE = enum.auto()

    @property
    def url_name(self):
        """
        """
        return {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "sword-of-seals",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
        }[self.value]

    @property
    def display_name(self):
        """
        """
        return {
            4: "Genealogy of the Holy War",
            5: "Thracia 776",
            6: "Sword of Seals",
            7: "Blazing Sword",
            8: "The Sacred Stones",
            9: "Path of Radiance",
        }[self.value]

    def is_gba_game(self):
        """
        """
        return self in (
            self.SWORD_OF_SEALS,
            self.BLAZING_SWORD,
            self.THE_SACRED_STONES,
        )

