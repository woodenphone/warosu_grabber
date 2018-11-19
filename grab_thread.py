#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     20-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import time
import os
import random
import logging
import logging.handlers
import datetime
import json
import cookielib
import re
# Remote libraries
import requests# For talking to websites
import requests.exceptions
import sqlite3# Because spinning up a new DB is easier this way
import sqlalchemy# For talking to DBs
from sqlalchemy.ext.declarative import declarative_base
import bs4
# local
import common









def parse_ghost_post():
    ghost_post_data = []
    return ghost_post_data



def dev2(reqs_ses, db_ses):
    # Temporarily set values by hand
    dl_dir = u'dl'
    board_name = 'tg'
    thread_num = 40312936
    # Calculate values
    thread_url = u'https://warosu.org/{bn}/thread/{tn}'.format(bn=board_name, tn=thread_num)
    thread_filename = 'warosu.{bn}.{tn}.html'.format(bn=board_name, tn=thread_num)
    thread_filepath = os.path.join(dl_dir, u'{0}'.format(board_name), thread_filename)
    logging.debug(u'thread_url={0!r}'.format(thread_url))
    # Load thread
    thread_res = common.fetch( requests_session=reqs_ses, url=thread_url, )
    thread_html = thread_res.content
    # Save for debugging/hoarding
    logging.debug(u'thread_filepath={0!r}'.format(thread_filepath))
    common.write_file(# Store page to disk
        file_path=thread_filepath,
        data=main_res.content
    )
    # Parse thread (we only care about ghost posts)
    soup = bs4.BeautifulSoup(thread_html, 'html.parser')
    # Find posts
    soup.find_all(name='table', attrs={})

    for post in posts:# Process each post
        logging.debug(u'post={0!r}'.format(post))
        # Skip post if not ghost
        # Parse out information from ghost post
        pass

    return









def dev():
    logging.warning(u'running dev()')

    # Set run parameters
    board_name = u'pone'
    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
    connection_string = common.convert_filepath_to_connect_string(filepath=db_filepath)
    thread_id = 316521 # https://8ch.net/pone/res/316521.html
    dl_dir = os.path.join('dl', '8test', '{0}'.format(board_name))

    # Setup requests session
    reqs_ses = requests.Session()

##    # Prepare board DB classes/table mappers
##    Boards = tables_8ch_p4c.table_factory_boards(Base)
##    Threads = tables_8ch_p4c.table_factory_threads(Base, board_name)
##    Posts = tables_8ch_p4c.table_factory_posts(Base, board_name)
##    Files = tables_8ch_p4c.table_factory_files(Base, board_name)

    # Setup/start/connect to DB
    logging.debug(u'Connecting to DB')
    db_dir, db_filename = os.path.split(db_filepath)
    if len(db_dir) != 0:# Ensure DB has a dir to be put in
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    # Start the DB engine
    engine = sqlalchemy.create_engine(
        connection_string,# Points SQLAlchemy at a DB
        echo=True# Output DB commands to log
    )
    # Link table/class mapping to DB engine and make sure tables exist.
    Base.metadata.bind = engine# Link 'declarative' system to our DB
    Base.metadata.create_all(checkfirst=True)# Create tables based on classes
    # Create a session to interact with the DB
    SessionClass = sqlalchemy.orm.sessionmaker(bind=engine)
    db_ses = SessionClass()

    dev2(reqs_ses=reqs_ses, db_ses=db_ses,)

    # Persist data now that thread has been grabbed
    session.commit()

    logging.info(u'Ending DB session')
    session.close()# Release connection back to pool.
    engine.dispose()# Close all connections.

    logging.warning(u'exiting dev()')
    return


def main():
    dev()
    return


if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "grab_board_py8ch.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")










# globals for messing with bs4

reqs_ses = requests.Session()



# Temporarily set values by hand
dl_dir = u'dl'
board_name = 'tg'
thread_num = 40312936
# Calculate values
thread_url = u'https://warosu.org/{bn}/thread/{tn}'.format(bn=board_name, tn=thread_num)
thread_filename = 'warosu.{bn}.{tn}.html'.format(bn=board_name, tn=thread_num)
thread_filepath = os.path.join(dl_dir, u'{0}'.format(board_name), thread_filename)
logging.debug(u'thread_url={0!r}'.format(thread_url))
# Load thread
thread_res = common.fetch( requests_session=reqs_ses, url=thread_url, )
thread_html = thread_res.content
# Save for debugging/hoarding
logging.debug(u'thread_filepath={0!r}'.format(thread_filepath))
common.write_file(# Store page to disk
    file_path=thread_filepath,
    data=thread_res.content
)
# Parse thread (we only care about ghost posts)
soup = bs4.BeautifulSoup(thread_html, 'html.parser')
# Find posts
posts = soup.find_all(name='table', attrs={'itemtype':'http://schema.org/Comment',})

for post in posts:# Process each post
    logging.debug(u'post={0!r}'.format(post))
    # Get post num and subnum (Num is post ID, subnum is ghost ID thing)
    delete_element = post.find_all('input', {'name':'delete'})
    delete_element_string = unicode(delete_element)
    num_search = re.search('<input name="delete" type="checkbox" value="(\d+),(\d+)', delete_element_string)
    num_string = pid_search.group(1)
    subnum_string = pid_search.group(2)
    num = int(num_string)
    subnum = int(subnum_string)
    # Detect if ghost post
    is_ghost = (subnum != 0)# subnum is 0 for regular replies, positive for ghost replies
    if (not is_ghost):# Skip post if not ghost
        logging.debug(u'Skipping regular reply: num={0!r}, subnum={1!r}'.format(num, subnum))
        continue

    logging.debug(u'Found ghost reply: num={0!r}, subnum={1!r}'.format(num, subnum))
    post_html = unicode(post)# If we can't extract original values, maybe we can just store the whole post?
    # Parse out information from ghost post
    name = post.find(name='span', attrs={'itemprop':'name',}).text
    email = post.find(name='span', attrs={'itemprop':'name',}).text
    pass


















