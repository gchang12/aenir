# TODO:
- Add in FE{Father,Campaign} for FE{4,7}.
- Update databases. Change some fields to Boolean.
- Merge aenir3 branch into master
- fillna in comparison df

# TODO: from aenir3
Create a dictionary of old names to new names for FE{4..6}
django.forms -- more than one submit button?
Write views.
Figure out how to store Morph objects.
Deploy to internet via django
- set up the index page and main design and layout
- home: explain what this is
- instructions: explain how to use, with screenshots
- feedback: input box for how to improve, any bugs, etc.
- application: create | edit | compare | (how-to) | (home)
- consider image-scraping for the extra pizazz

# TODO: aenir3_web - 2023-12-03
Implement database-based sessions to store Morph (model: DragonsGate)
Print stats in template
Add create-confirm page

DONE
====
Consider destroying bases/growths tables to economize on memory
- Involves lots and lots of test refactoring
- Also, what about if one day, we need to include FE11 units, which have growths that can change after initialization?
- Also, what about HM-bonus louts?
- 2023-11-01: Destroyed
Ask about why I need a full_history list parameter
- I don't
FE5 scroll support
Add docstrings to new test methods and __lt__ dunder
Add logging messages to new test methods
- Why?
Redo docstrings after reading PEP257
- Why?
Segregate tables from Morph objects post-initialization
Segregate io-tests from the main data