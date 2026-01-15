/**
Defines tests for FireEmblemGame
*/
package aenir;

import java.util.Map;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/* import aenir.FireEmblemGame; */

/*
from aenir.games import FireEmblemGame
from aenir._logging import (
    configure_logging,
    logger,
    time_logger,
)

configure_logging()
time_logger.critical("")
*/

/**
Contains all test cases (i.e., all six).
*/
class FireEmblemGameTest {
    /**
    Prints test-id for test-demarcation purposes.
    */
    void setUp() {
        // logger.critical("%s", self.id())
        System.out.println("TODO: Print test-id to log here.");
    };
    /**
    Tests `isGbaGame` method.
    */
    @Test
    void isGBAGame_true() {
        FireEmblemGame[] gbaGames = {
            FireEmblemGame.SWORD_OF_SEALS,
            FireEmblemGame.BLAZING_SWORD,
            FireEmblemGame.THE_SACRED_STONES,
        };
        for (FireEmblemGame game : gbaGames) {
            assertTrue(game.isGBAGame());
        };
    };
    /**
    Tests `isGBAGame` method.
    */
    @Test
    void isGBAGame_false() {
        FireEmblemGame[] nonGbaGames = {
            FireEmblemGame.GENEALOGY_OF_THE_HOLY_WAR,
            FireEmblemGame.THRACIA_776,
            FireEmblemGame.PATH_OF_RADIANCE,
        };
        for (FireEmblemGame game : nonGbaGames) {
            assertFalse(game.isGBAGame());
        };
    };
    /**
    Affirms values defined for `getUrlName` property.
    */
    @Test
    void getUrlName() {
        Map<Integer, String> gameNo_urlName = Map.of(
            4, "genealogy-of-the-holy-war",
            5, "thracia-776",
            6, "binding-blade",
            7, "blazing-sword",
            8, "the-sacred-stones",
            9, "path-of-radiance"
        );
        int gameNo;
        String urlName;
        /* FireEmblemGame feGame; */
        for (FireEmblemGame feGame : FireEmblemGame.values()) {
        /* for (Map.Entry<Integer, String> entry : gameNo_urlName.entrySet()) { */
            gameNo = feGame.gameNo;
            urlName = gameNo_urlName.get(gameNo);
            /* feGame = FireEmblemGame(gameNo); */
            assertEquals(feGame.getUrlName(), urlName);
        };
    };
    /**
    Affirms values defined for `formal_name` property.
    */
    @Test
    void getFormalName() {
        Map<Integer, String> gameNo_formalName = Map.of(
            4, "Genealogy of the Holy War",
            5, "Thracia 776",
            6, "Sword of Seals",
            7, "Blazing Sword",
            8, "The Sacred Stones",
            9, "Path of Radiance"
        );
        int gameNo;
        String formalName;
        /* FireEmblemGame feGame; */
        for (FireEmblemGame feGame : FireEmblemGame.values()) {
        /* for (Map.Entry<Integer, String> entry : gameNo_formalName.entrySet()) { */
            gameNo = feGame.gameNo;
            formalName = gameNo_formalName.get(gameNo);
            /* feGame = FireEmblemGame(gameNo); */
            assertEquals(feGame.getFormalName(), formalName);
            /* gameNo = entry.getKey(); */
            /* formalName = entry.getValue(); */
            /* feGame = FireEmblemGame(gameNo); */
            /* assertEquals(feGame.getFormalName(), formalName); */
        };
    };
};

