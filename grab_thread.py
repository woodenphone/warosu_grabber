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
import warosu_tables


Base = declarative_base()# Setup system to keep track of tables and classes












def is_post_in_results(results, thread_num, num, subnum):
    """Check if the specified post is in the results rows.
    If it is, return that row.
    else, return None
    """
    if len(results) == 0:
        return None
    for result in results:
        tn = (result.thread_num == thread_num)
        pn = (result.num == num)
        sn = (result.subnum == subnum)
        logging.debug(u'tn={0!r}, pn={1!r}, sn={2!r}'.format(tn, pn, sn))# PERFOMANCE: Disable this
        if (tn and pn and sn):
            return result
    return None


""


##def count_search_ranges(date_from, date_to):
##    pass


##def scan_board_range(req_ses, board_name, dl_dir,
##    date_from, date_to):
##    logging.debug(u'save_board_range() args={0!r}'.format(locals()))# Record arguments.
##
##    # Iterate over range
##    weekdelta = datetime.timedelta(days=7)# One week's difference in time towards the future
##    working_date = date_from# Initialise at low end
##    all_thread_ids = []
##    while working_date < date_to:
##        logging.debug(u'working_date={0!r}'.format(working_date))
##        fut_date = working_date + weekdelta
##        logging.debug(u'fut_date={0!r}'.format(fut_date))
##        for page_counter in xrange(1, 1000):
##            offset = page_counter * 24# 24 posts per search page
##            logging.debug(u'offset={0!r}'.format(offset))
##            # Read one search page
##            res = search_for_threads(
##                req_ses=req_ses,
##                board_name=board_name,
##                dl_dir=dl_dir,
##                date_from=common.date_to_warosu(date=working_date),
##                date_to=common.date_to_warosu(date=fut_date),
##                offset=offset
##            )
##            # Extract thread numbers
##            thread_ids = re.findall('/\w+/thread/S?(\d+)', res.content)
##            logging.debug(u'thread_ids={0!r}'.format(thread_ids))
##            # Store thread numbers
##            all_thread_ids += thread_ids
##            logging.debug(u'len(all_thread_ids)={0!r}'.format(len(all_thread_ids)))
##            # Check if end of results reached
##            if len(thread_ids) == 0:
##                logging.info('No threads found on this page, moving on to next date range')
##                break
##            continue
##        # Go forward a week
##        logging.debug('Incrementing working date')
##        working_date += weekdelta
##        continue
##    logging.info(u'Finished searching')
##    return


def remove_cf_email_garbage(html):
    # erase cloudflare email hiding junk
    clean_html = re.sub('<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="\w+">\[email&#160;protected\]</a>', '', html)
    return clean_html


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
    board_name = u'tg'
    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
    connection_string = common.convert_filepath_to_connect_string(filepath=db_filepath)
    logging.debug(u'connection_string={0!r}'.format(connection_string))
    thread_num = 40312936 # https://warosu.org/tg/thread/40312936
    dl_dir = os.path.join(u'dl', u'wtest', u'{0}'.format(board_name))

    # Setup requests session
    req_ses = requests.Session()

##    scan_board_range(
##        req_ses=req_ses,
##        board_name=board_name,
##        dl_dir=dl_dir,
##        date_from = datetime.date(2018, 11, 1),# Year, month, day of month
##        date_to = datetime.date(2019, 1, 1),
####        date_from = u'2018-1-1',
####        date_to = u'2019-1-1',
##    )
##    return

    # Prepare board DB classes/table mappers
    Boards = None# warosu_tables.table_factory_simple_boards(Base)
    Threads = None# warosu_tables.table_factory_simple_threads(Base, board_name)
    Posts = warosu_tables.table_factory_simple_posts(Base, board_name)

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
    session = SessionClass()

##    # Save a thread
##    simple_save_thread(
##        db_ses=session,
##        req_ses=req_ses,
##        Threads=Threads,
##        Posts=Posts,
##        board_name=board_name,
##        thread_num=thread_num,
##        dl_dir=dl_dir
##    )

    # Persist data now that thread has been grabbed
    logging.info(u'Committing')
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
    common.setup_logging(os.path.join("debug", "grab_thread.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
