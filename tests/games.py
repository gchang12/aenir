"""
"""

import unittest

from aenir.games import FireEmblemGame

class FireEmblemGameTest(unittest.TestCase):
    """
    """

    def test_is_gba_game__true(self):
        """
        """
        gba_games = (
            FireEmblemGame.SWORD_OF_SEALS,
            FireEmblemGame.BLAZING_SWORD,
            FireEmblemGame.THE_SACRED_STONES,
        )
        expected = True
        for game in gba_games:
            actual = game.is_gba_game()
            self.assertIs(actual, expected)

    def test_is_gba_game__false(self):
        """
        """
        non_gba_games = (
            FireEmblemGame.GENEALOGY_OF_THE_HOLY_WAR,
            FireEmblemGame.THRACIA_776,
            FireEmblemGame.PATH_OF_RADIANCE,
        )
        expected = False
        for game in non_gba_games:
            actual = game.is_gba_game()
            self.assertIs(actual, expected)

    def test_url_name(self):
        """
        """
        gamerank_to_urlname = {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "sword-of-seals",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
        }
        for game_rank, url_name in gamerank_to_urlname.items():
            game = FireEmblemGame(game_rank)
            expected = url_name
            actual = game.url_name
            self.assertEqual(actual, expected)

    def test_formal_name(self):
        """
        """
        gamerank_to_formalname = {
            4: "Genealogy of the Holy War",
            5: "Thracia 776",
            6: "Sword of Seals",
            7: "Blazing Sword",
            8: "The Sacred Stones",
            9: "Path of Radiance",
        }
        for game_rank, formal_name in gamerank_to_formalname.items():
            game = FireEmblemGame(game_rank)
            expected = formal_name
            actual = game.formal_name
            self.assertEqual(actual, expected)
