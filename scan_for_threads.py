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
import yaml
# local
import common
import tables_reallysimple


Base = declarative_base()# Setup system to keep track of tables and classes



class YAMLConfigScanForThreads():
    """Handle reading, writing, and creating YAML config files."""
    def __init__(self, config_path=None):
        # Set default values
        self.board_name = 'board_shortname'
        self.db_filepath = 'db/filepath/if.sqlite'
        self.connection_string = 'engine://sqlalchemy_parameters'
        self.dl_dir = 'download/filepath/'
        self.date_from = datetime.date(1970,1,1)# 1st Jan 1970, classic dummy date.
        self.date_to = datetime.date(1970,1,1)# 1st Jan 1970, classic dummy date.
        self.step_days = 1
        self.echo_sql = False
        if config_path:
            config_dir = os.path.dirname(config_path)
            if len(config_dir) > 0:# Only try to make a dir if ther is a dir to make.
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)# Ensure config dir exists.
            if os.path.exists(config_path):
                self.load(config_path)# Load config file if it exists.
            else:
                self.save(config_path, self.__class__())# Create an example config file if no file exists.
        return
    def load(self, config_path):
        """Load configuration from YAML file."""
        logging.debug('Reading from config_path={0!r}'.format(config_path))
        with open(config_path, 'rb') as load_f:# Read the config from file.
            config = yaml.safe_load(load_f)
        for key in config.keys():# Store values to class instance.
            setattr(self, key, config[key])# Sets self.key to config[key]
        return
    def save(self, config_path, instance):
        """Save current configuration to YAML file."""
        logging.debug('Saving to config_path = {0!r}'.format(config_path))
        with open(config_path, 'wb') as save_f:# Write data to file.
            yaml.dump(
                data=vars(instance),# All vars in object 'instance' as dict
                stream=save_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False)# Output as multiple lines
        return



def search_for_threads(req_ses, board_name, dl_dir,
    date_from, date_to, offset):
    """Load one search page, save it for debugging, and return the response object."""
    logging.debug(u'search_for_threads() args={0!r}'.format(locals()))# Record arguments.
    # Generate url for search page
    current_page_template = (# Search for all threads
        u'https://warosu.org/{board_name}/?task=search2'
        u'&ghost=yes'# Include ghostposts in query
        u'&search_text='
        u'&search_subject='
        u'&search_username='
        u'&search_tripcode='
        u'&search_email='
        u'&search_filename='
        u'&search_datefrom={date_from}'# Specify start date
        u'&search_dateto={date_to}'# Specify end date
        u'&search_op=op'# Only look for OP posts
        u'&search_del=dontcare'
        u'&search_int=dontcare'
        u'&search_ord=new'
        u'&search_capcode=all'
        u'&search_res=post'
        u'&offset={offset}'# Specify results offset
        u'&search_res=op'# Only show thread OP in results
    )
    current_page_url = current_page_template.format(
        board_name=board_name, date_from=date_from,
        date_to=date_to, offset=offset)
    logging.debug(u'current_page_url={0!r}'.format(current_page_url))
    # Load page
    page_res = common.fetch(requests_session=req_ses, url=current_page_url)
##    # Save page for debug
##    current_page_filename = u'df{df}.dt{dt}.html'.format(df=date_from, dt=date_to)
##    # <base>/thread_listings/<board_name>/html/<offset>.html
##    current_page_filepath = os.path.join(
##        dl_dir, u'thread_listings', board_name, u'html', current_page_filename )
##    current_page_filepath = os.path.join(# TODO: Put normal dl path generration back in
##        dl_dir, u'temp', current_page_filename)
##    logging.debug(u'current_page_filename={0!r}'.format(current_page_filename))
##    logging.debug(u'current_page_filepath={0!r}'.format(current_page_filepath))
##    common.write_file(file_path=current_page_filepath, data=page_res.content)
    return page_res


def str_to_date(date_string):
    """'YYYY-MM-DD' -> datetime.date(YYYY, MM, DD)
    '2018-11-25' -> datetime.date(year=2018,month=11,day=25)"""
    logging.debug(u'date_string={0!r}'.format(date_string))
    date = datetime.datetime.strptime(date_string, u'%Y-%m-%d')
    return date


def date_to_warosu(date):
    """Convert datetime objects to YYYY-MM-DD strings"""
    return date.strftime('%Y-%m-%d')


def convert_list_str_to_int(values):
    out_list = []
    for value in values:
        out_list.append(int(value))
    return out_list


def insert_if_new(db_ses, RSThreads, thread_nums):
    # See if thread ID(s) in DB:
    new_threads = []
    for thread_num in thread_nums:
        # Lookup thread_num
        check_q = db_ses.query(RSThreads)\
            .filter(RSThreads.thread_num == thread_num,)
        check_result = check_q.first()
        if check_result:
            # UPDATE
            #logging.debug('Thread already in DB, not inserting: {0!r}'.format(thread_num))
            continue
        else:
            # INSERT
            #logging.debug('Staging thread for insert: {0!r}'.format(thread_num))
            new_thread = RSThreads( thread_num = thread_num )
            new_threads.append(new_thread)# Insert thread_num
    if len(new_threads) > 0:
        logging.debug('Inserting {0!r} new threads'.format(len(new_threads)))
        db_ses.add_all(new_threads)
        db_ses.commit()
    return


def insert_threads_to_db(db_ses, RSThreads, thread_nums):
    new_threads = []
    for thread_num in thread_nums:
        new_thread = RSThreads( thread_num = thread_num )
        new_threads.append(new_thread)
    db_ses.add_all(new_threads)
    db_ses.commit()
    return


def scan_board_range(db_ses, RSThreads, req_ses, board_name,
    dl_dir, date_from, date_to, tlist_out_template, step_days=1):
    logging.debug(u'save_board_range() args={0!r}'.format(locals()))# Record arguments.
    # Generate output filepath
    filename = (tlist_out_template.format(l=date_from, h=date_to))
    thread_nums_dump_path = os.path.join(dl_dir, 'found_threads', filename)
    logging.debug(u'thread_nums_dump_path={0!r}'.format(thread_nums_dump_path))
    # Iterate over range
    delta = datetime.timedelta(days=step_days)
    working_date = date_from# Initialise at low end
    prev_page_threads = [None]
    all_thread_nums = []
    total_pages = 0
    while (working_date < date_to):
        # Generate our current date range
        logging.debug(u'working_date={0!r}'.format(working_date))
##        fut_date = working_date + weekdelta
        fut_date = working_date + delta
        logging.debug(u'fut_date={0!r}'.format(fut_date))
        # Iterate over offsets in the current date range
        for page_counter in xrange(1, 1000):
            total_pages += 1
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
            thread_num_strings = re.findall('href="/\w+/thread/S?(\d+)">View', res.content)
            logging.debug(u'thread_num_strings={0!r}'.format(thread_num_strings))
            logging.debug(u'len(thread_num_strings)={0!r}'.format(len(thread_num_strings)))
            thread_nums = convert_list_str_to_int(thread_num_strings)
            logging.debug(u'thread_nums={0!r}'.format(thread_nums))
            logging.debug(u'len(thread_nums)={0!r}'.format(len(thread_nums)))
            unique_thread_nums = common.uniquify(thread_nums)
            logging.debug(u'unique_thread_nums={0!r}'.format(unique_thread_nums))
            # Store thread numbers to DB
##            insert_threads_to_db(db_ses=db_ses, RSThreads=RSThreads, thread_nums=unique_thread_nums)
            insert_if_new(db_ses=db_ses, RSThreads=RSThreads, thread_nums=unique_thread_nums)
            # Store thread numbers
            all_thread_nums += unique_thread_nums
            logging.debug(u'len(all_thread_nums)={0!r}'.format(len(all_thread_nums)))
            # Check if end of results reached
            if len(thread_nums) == 0:
                logging.info('No threads found on this page, moving on to next date range')
                break
            elif (thread_nums == prev_page_threads):
                logging.info('Threads on this page were the same as the previous page, moving on to next date range')
                break
            prev_page_threads = thread_nums
            continue
        # Go forward a week
        logging.debug('Incrementing working date')
        working_date = fut_date
        continue
    logging.debug(u'total_pages={0!r}'.format(total_pages))

    # Save threadIDs to file as a backup
    logging.debug(u'thread_nums_dump_path={0!r}'.format(thread_nums_dump_path))
    # Ensure dir exists
    dump_dir, dump_filename = os.path.split(thread_nums_dump_path)
    if len(dump_dir) != 0:
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)
    # Save file
    with open(thread_nums_dump_path, 'a') as df:
        for thread_num_out in all_thread_nums:
            df.write('t{0}\n'.format(thread_num_out))
    logging.info(u'Finished searching range: {0!r} to {1!r}'.format(date_from, date_to))
    return


##def scan_delta(low_date, end_date, delta):
##    logging.debug(u'scan_delta() args={0!r}'.format(locals()))# Record arguments.
##    logging.info('Scanning range: {0!r} to {1!r} in batches of {2!r}'.format(date_from, date_to, delta))
##    working_date = low_date
##    while (working_date < end_date):
##        date_from = working_date
##        date_to = working_date + delta
##        logging.debug('Now working on range: {0!r} to {1!r}'.format(date_from, date_to))
##        scan_board_range(
##            db_ses=db_ses,
##            RSThreads=RSThreads,
##            req_ses=req_ses,
##            board_name=board_name,
##            dl_dir=dl_dir,
##            date_from=date_from,
##            date_to=date_to
##            )
##        working_date += delta
##    logging.info('Finished scanning range: {0!r} to {1!r} in batches of {2!r}'.format(date_from, date_to, delta))
##    return
##
##
##def detect_fake_date(date_obj):
##    """Detect a predefined dummy value date"""
##    if (type(date_obj) not in [datetime.datetime, datetime.date, datetime.time]):
##        logging.error('Improper date object type!')
##        return True
##    predefined_fake_date = datetime.date(1970,1,1)# 1st Jan 1970, classic dummy date.
##    slop_delta = datetime.timedelta(days=7)# Some slop to tolerate whatever decrease in resolution if conversions occur.
##    l_date = predefined_fake_date - datetime.timedelta(days=7)
##    h_date = predefined_fake_date + datetime.timedelta(days=7)
##    if ( (l_date) <= date_obj <= (h_date) ):
##        logging.info('Predefined fake date detected!')
##        return True
##    else:
##        return False


##def dev():
##    logging.warning(u'running dev()')
##    # Set run parameters
##    board_name = u'tg'
##    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
##    connection_string = common.convert_filepath_to_connect_string(filepath=db_filepath)
##    logging.debug(u'connection_string={0!r}'.format(connection_string))
##    thread_num = 40312936 # https://warosu.org/tg/thread/40312936
##    dl_dir = os.path.join(u'dl', u'wtest', u'{0}'.format(board_name))
##    # Setup requests session
##    req_ses = requests.Session()
##    # Prepare board DB classes/table mappers
##    RSThreads = warosu_tables.table_factory_really_simple_threads(Base, board_name)
##    # Setup/start/connect to DB
##    logging.debug(u'Connecting to DB')
##    db_dir, db_filename = os.path.split(db_filepath)
##    if len(db_dir) != 0:# Ensure DB has a dir to be put in
##        if not os.path.exists(db_dir):
##            os.makedirs(db_dir)
##    # Start the DB engine
##    engine = sqlalchemy.create_engine(
##        connection_string,# Points SQLAlchemy at a DB
##        echo=True# Output DB commands to log
##    )
##    # Link table/class mapping to DB engine and make sure tables exist.
##    Base.metadata.bind = engine# Link 'declarative' system to our DB
##    Base.metadata.create_all(checkfirst=True)# Create tables based on classes
##    # Create a session to interact with the DB
##    SessionClass = sqlalchemy.orm.sessionmaker(bind=engine)
##    db_ses = SessionClass()
##
##    # Scan the range
##    scan_board_range(
##        db_ses=db_ses,
##        RSThreads=RSThreads,
##        req_ses=req_ses,
##        board_name=board_name,
##        dl_dir=dl_dir,
##        date_from = datetime.date(2018, 11, 1),# Year, month, day of month
##        date_to = datetime.date(2018, 11, 2),# Year, month, day of month
##    )
##
##    # Persist data now that thread has been grabbed
##    logging.info(u'Committing')
##    db_ses.commit()
##    # Gracefully disconnect from DB
##    logging.info(u'Ending DB session')
##    db_ses.close()# Release connection back to pool.
##    engine.dispose()# Close all connections.
##    logging.warning(u'exiting dev()')
##    return


def from_config():
    logging.info(u'Running from_config()')
    # Load config file
    config_path = os.path.join(u'config', 'scan_for_threads.yaml')
    config = YAMLConfigScanForThreads(config_path)
    # Set values from config file
    board_name = unicode(config.board_name)
    db_filepath = unicode(config.db_filepath)
    connection_string = unicode(config.connection_string)
    dl_dir = unicode(config.dl_dir)
    date_from = config.date_from
    date_to = config.date_to
    step_days = int(config.step_days)
    echo_sql = config.echo_sql
    tlist_out_template = 'l{l}.h{h}.txt'

    # Sanity checks
    assert(date_from > datetime.date(2000,1,1))
    assert(date_to > datetime.date(2000,1,1))

    # Setup requests session
    req_ses = requests.Session()
    # Prepare board DB classes/table mappers
    RSThreads = tables_reallysimple.really_simple_threads(Base, board_name)
    # Setup/start/connect to DB
    logging.debug(u'Connecting to DB')
    db_dir, db_filename = os.path.split(db_filepath)
    if len(db_dir) != 0:# Ensure DB has a dir to be put in
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    # Start the DB engine
    engine = sqlalchemy.create_engine(
        connection_string,# Points SQLAlchemy at a DB
        echo=echo_sql# Output DB commands to log
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
        RSThreads=RSThreads,
        req_ses=req_ses,
        board_name=board_name,
        dl_dir=dl_dir,
        date_from = date_from,
        date_to = date_to,
        tlist_out_template = tlist_out_template,
        step_days=step_days
    )

    # Persist data now that thread has been grabbed
    logging.info(u'Committing')
    db_ses.commit()

    # Gracefully disconnect from DB
    logging.info(u'Ending DB session')
    db_ses.close()# Release connection back to pool.
    engine.dispose()# Close all connections.

    logging.info(u'Exiting from_config()')
    return


def main():
##    dev()
    from_config()
    return


if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "scan_for_threads.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
