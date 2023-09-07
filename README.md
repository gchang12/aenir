// 2023-09-06
create module to nix:
-comments
-docstrings
-logging calls

logging
docstrings
comments
int df - nix columns option
handle errors properly

single-quoted mismatches

4
-rm growth-table0
-match [child,father] via multiindex
9
beware the broken html tag for sothe in growths
7
concat class to promotable0
concat two bases together after adding multiindex

pop class and lv from pd.Series <- [gamenum,unitname]
store remaining fields into register
add fail-safes for when methods are not called in the right order
more tests

scraper
-scrape tables
--what if the webpage dne
-save tables
--what if there are no tables to save
-load tables
--what if there is no file to load from

cleaner
-create fieldrecon file
--what if there are no tables loaded
--what if the columns have no names
# aside: what if the parent directories dne
-drop nonnumeric rows
--what if there are no tables to drop from
-apply fieldrecon file
--what if it dne
--what if there is nothing to apply it to
-replace with int df
--what if there's nothing to replace
--what if some cells arent even strings

reconciler
-create clsrecon file
--what if either table dne
--what if the columns dne
-verify clsrecon file
--what if the tables dne
--what if the columns dne
--what if the file dne


// 2023-09-07
assert converted url is in keys
write tests for ScraperTest
rewrite tests
delete comments and docstrings
remove subclassing of aseMorph
--on the other hand if it works, why fix it?
  --need to know everything that can go wrong
    --everything encompasses a large universe of scenariosthat will happen onlyon the dev-side of things
        --put it like this: only one fnction can permanently damageyou=r work
