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




def search_for_threads(req_ses, board_name, dl_dir,
    date_from, date_to, offset):
    """Load one search page, save it for debugging, and return the response object."""
    logging.debug(u'search_for_threads() args={0!r}'.format(locals()))# Record arguments.
    # Generate url for search page
    current_page_template = (
        u'https://warosu.org/g/?task=search2'
        u'&ghost=yes'
        u'&search_text='
        u'&search_subject='
        u'&search_username='
        u'&search_tripcode='
        u'&search_email='
        u'&search_filename='
        u'&search_datefrom={date_from}'
        u'&search_dateto={date_to}'
        u'&search_op=all'
        u'&search_del=dontcare'
        u'&search_int=dontcare'
        u'&search_ord=new'
        u'&search_capcode=all'
        u'&search_res=post'
        u'&offset={offset}'
    )
    current_page_url = current_page_template.format(
        date_from=date_from, date_to=date_to, offset=offset)
    logging.debug(u'current_page_url={0!r}'.format(current_page_url))

    # Load page
    page_res = common.fetch(requests_session=req_ses, url=current_page_url)

##    current_page_filename = u'df{df}.dt{dt}.html'.format(df=date_from, dt=date_to)
##    # <base>/thread_listings/<board_name>/html/<offset>.html
##    current_page_filepath = os.path.join(
##        dl_dir,
##        u'thread_listings',
##        u'{0}'.format(board_name),
##        u'html',
##        current_page_filename
##    )
##    current_page_filepath = os.path.join(# TODO: Put normal dl path generration back in
##        dl_dir,
##        u'temp',
##        current_page_filename
##    )
##    logging.debug(u'current_page_filename={0!r}'.format(current_page_filename))
##    logging.debug(u'current_page_filepath={0!r}'.format(current_page_filepath))

##    # Save page for debug
##    common.write_file(file_path=current_page_filepath, data=page_res.content)
    return page_res


def date_to_warosu(date):
    """Convert datetime objects to YYYY-MM-DD strings"""
    return date.strftime('%Y-%m-%d')


def convert_list_str_to_int(values):
    out_list = []
    for value in values:
        out_list.append(int(value))
    return out_list


def scan_board_range(db_ses, req_ses, board_name,
    dl_dir, date_from, date_to):
    logging.debug(u'save_board_range() args={0!r}'.format(locals()))# Record arguments.
    # Iterate over range
    weekdelta = datetime.timedelta(days=7)# One week's difference in time towards the future
    working_date = date_from# Initialise at low end
    all_thread_ids = []
    while working_date < date_to:
        # Generate our current date range
        logging.debug(u'working_date={0!r}'.format(working_date))
        fut_date = working_date + weekdelta
        logging.debug(u'fut_date={0!r}'.format(fut_date))
        # Iterate over offsets in the current date range
        for page_counter in xrange(1, 1000):
            offset = page_counter * 24# 24 posts per search page
            logging.debug(u'offset={0!r}'.format(offset))
            # Read one search page
            res = search_for_threads(
                req_ses=req_ses,
                board_name=board_name,
                dl_dir=dl_dir,
                date_from=date_to_warosu(date=working_date),
                date_to=date_to_warosu(date=fut_date),
                offset=offset
            )
            # Extract thread numbers
            thread_ids = re.findall('/\w+/thread/S?(\d+)', res.content)
            logging.debug(u'thread_ids={0!r}'.format(thread_ids))
            # Store thread numbers
            all_thread_ids += thread_ids
            # Check if end of results reached
            if len(thread_ids) == 0:
                break
            continue
        # Go forward a week
        working_date += weekdelta
        continue
    # Save threadIDs to file as a backup
    with open(thread_ids_dump_path, 'w') as df:
        for thread_id_out in all_thread_ids:
            df.append('{0}'.format(thread_id_out))
    logging.info(u'Finished searching')
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
    # Prepare board DB classes/table mappers
    Threads = table_factory_really_simple_threads(Base, board_name)
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
    # Scan the range
    scan_board_range(
        db_ses=db_ses,
        req_ses=req_ses,
        board_name=board_name,
        dl_dir=dl_dir,
        date_from = datetime.date(2018, 1, 1),# Year, month, day of month
        date_to = datetime.date(2019, 1, 1),
    )
    # Persist data now that thread has been grabbed
    logging.info(u'Committing')
    db_ses.commit()
    # Gracefully disconnect from DB
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
