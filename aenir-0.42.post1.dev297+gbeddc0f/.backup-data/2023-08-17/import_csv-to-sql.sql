.mode csv

CREATE TABLE BaseStats (Name TEXT, Class TEXT, Lv INTEGER, HP INTEGER, Pow INTEGER, Skl INTEGER, Spd INTEGER, Lck INTEGER, Def INTEGER, Res INTEGER, Con INTEGER, Mov INTEGER, Affin TEXT, WeaponRanks TEXT);
CREATE TABLE GrowthRates (Name TEXT, HP INTEGER, Pow INTEGER, Skl INTEGER, Spd INTEGER, Lck INTEGER, Def INTEGER, Res INTEGER);
CREATE TABLE classMaxes (Class TEXT, Pow INTEGER, Skl INTEGER, Spd INTEGER, Def INTEGER, Res INTEGER, Con INTEGER);
CREATE TABLE classPromo (Class TEXT, Promotion TEXT, HP INTEGER, Pow INTEGER, Skl INTEGER, Spd INTEGER, Def INTEGER, Res INTEGER, Con INTEGER, Mov INTEGER, WeaponRanks TEXT);
CREATE TABLE classGrowths (Class TEXT, HP INTEGER, Pow INTEGER, Skl INTEGER, Spd INTEGER, Def INTEGER, Res INTEGER, Lck INTEGER);

.import characters_base-stats.csv BaseStats
.import characters_growth-rates.csv GrowthRates
.import classes_maximum-stats.csv classMaxes
.import classes_promotion-gains.csv classPromo
.import classes_growth-rates.csv classGrowths

DELETE FROM BaseStats WHERE rowid=1;
DELETE FROM GrowthRates WHERE rowid=1;
DELETE FROM classMaxes WHERE rowid=1;
DELETE FROM classPromo WHERE rowid=1;
DELETE FROM classGrowths WHERE rowid=1;
