# Warosu grabber thing

# !NOT SUITABLE FOR USAGE OUTSIDE TESTING!
This code is still under development.

# Usage
TODO

## Thread discovery
To save threads from thread ID DB:
python save_threads_fuuka.py

## Thread saving
To search for threads and add them to the thread ID DB
python scan_for_threads.py

# Installation
TODO
pip install yaml
pip install bs4
pip install requests
pip install sqlalchemy
pip install sqlite3

# What each file does

## scan_for_threads.py
Find threads with ghostposts.
Almost ready for use.

## common.py
Utility functions.
Functions used in multiple other modules.
Ready for use.

## save_threads_asagi.py
Save threads into an asagi-style DB
Not working yet.

## save_threads_fuuka.py
Save threads into a Fuuka-style DB.
Mostly ready.

## save_thread_simpleposts.py
Save a thread using the SimplePosts style DB schema.
Might not work.

## tables_asagi.py
Asagi / Foolfuuka style DB definitions.

## tables_fuuka.py
Fuuka style DB definitions.

## tables_reallysimple.py
Extremely simplistic DB definitions.

## tables_simple.py
Simplistic DB definitions.

## thread_parsers.py
Parse / extract information from posts.
Split thread pages into posts.
Ready for use.

## unformat_comment.py
Supposed to be for reverrsing formatting applied to posts.
Not working.
