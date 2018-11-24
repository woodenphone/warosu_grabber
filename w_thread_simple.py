#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     24-11-2018
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


def simple_save_thread(db_ses, req_ses, Threads, SimplePosts, board_name, thread_num, dl_dir):
    """Save the ghost posts in a thread in a very simple manner"""
    logging.info(u'Fetching thread: {0!r}'.format(thread_num))
    # Calculate values
    thread_url = u'https://warosu.org/{bn}/thread/{tn}'.format(bn=board_name, tn=thread_num)
    thread_filename = 'warosu.{bn}.{tn}.html'.format(bn=board_name, tn=thread_num)
    thread_filepath = os.path.join(dl_dir, u'{0}'.format(board_name), thread_filename)
    logging.debug(u'thread_url={0!r}'.format(thread_url))

    # Look for all posts for this thread in DB
    logging.debug('About to look for existing posts for this thread')
    existing_posts_q = db_ses.query(SimplePosts)\
        .filter(SimplePosts.thread_num == thread_num,)
    existing_posts = existing_posts_q.all()
    logging.debug(u'existing_posts={0!r}'.format(existing_posts))
    logging.debug(u'len(existing_posts)={0!r}'.format(len(existing_posts)))
    # Load thread
    thread_res = common.fetch( requests_session=req_ses, url=thread_url, )
    thread_html = thread_res.content
    # Save for debugging/hoarding
    logging.debug(u'thread_filepath={0!r}'.format(thread_filepath))
    common.write_file(# Store page to disk
        file_path=thread_filepath,
        data=thread_res.content
    )
    # Parse thread (we only care about ghost posts)
    soup = bs4.BeautifulSoup(thread_html, u'html.parser')
    # Find posts
    posts = soup.find_all(name=u'table', attrs={u'itemtype':'http://schema.org/Comment',})# TODO WARNING This may miss op!
    logging.warning('The current method of post finding may miss OP!')
    logging.debug(u'len(posts)={0!r}'.format(len(posts)))
    for post in posts:# Process each post
##        logging.debug(u'post={0!r}'.format(post))
        # Get post num and subnum (Num is post ID, subnum is ghost ID thing)
        delete_element = post.find_all('input', {'name':'delete'})
        delete_element_string = unicode(delete_element)
        num_search = re.search(u'<input name="delete" type="checkbox" value="(\d+),(\d+)', delete_element_string)
        num_string = num_search.group(1)
        subnum_string = num_search.group(2)
        num = int(num_string)
        subnum = int(subnum_string)
        # Detect if ghost post
        is_ghost = (subnum != 0)# subnum is 0 for regular replies, positive for ghost replies
        if (not is_ghost):# Skip post if not ghost
            logging.debug(u'Skipping regular reply: num={0!r}, subnum={1!r}'.format(num, subnum))
            continue
        logging.debug(u'Found ghost reply: num={0!r}, subnum={1!r}'.format(num, subnum))
        post_html = unicode(post)# If we can't extract original values, maybe we can just store the whole post?
        # Check if post is already in DB
        post_is_in_db = is_post_in_results(results=existing_posts, thread_num=thread_num,
             num=num, subnum=subnum)
        if (post_is_in_db):
            logging.debug(u'Post {0}.{1} in thread {2} already saved'.format(num ,subnum, thread_num))
        else:
            logging.debug('About to insert ghost post')
            logging.debug(u'SimplePosts={0!r}'.format(SimplePosts))
            logging.debug(u'num={0!r}'.format(num))
            logging.debug(u'subnum={0!r}'.format(subnum))
            logging.debug(u'thread_num={0!r}'.format(thread_num))
            logging.debug(u'post_html={0!r}'.format(post_html))
            # Add post to DB
            new_simplepost = SimplePosts(
                num = num,
                subnum = subnum,
                thread_num = thread_num,
                post_html = post_html,
            )
            db_ses.add(new_simplepost)
            logging.info(u'Inserted a ghost post into SimplePosts')
    logging.info(u'Fetched thread: {0!r}'.format(thread_num))
    return




def thread_simple_dev():
    """Dev playground"""
    logging.warning(u'running thread_simple_dev()')

    # Set run parameters
    board_name = u'tg'
    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
    connection_string = common.convert_filepath_to_connect_string(filepath=db_filepath)
    logging.debug(u'connection_string={0!r}'.format(connection_string))
    thread_num = 40312936 # https://warosu.org/tg/thread/40312936 #Ghost post example
    thread_num = 40312392 # https://warosu.org/tg/thread/40312392 # Tripcode example
    dl_dir = os.path.join(u'dl', u'wtest', u'{0}'.format(board_name))
    # Setup requests session
    req_ses = requests.Session()
    # Prepare board DB classes/table mappers
    Boards = None# warosu_tables.table_factory_simple_boards(Base)
    Threads = None# warosu_tables.table_factory_simple_threads(Base, board_name)
    SimplePosts = warosu_tables.table_factory_simple_posts(Base, board_name)

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

    # Save a thread
    simple_save_thread(
        db_ses=session,
        req_ses=req_ses,
        Threads=Threads,
        SimplePosts=SimplePosts,
        board_name=board_name,
        thread_num=thread_num,
        dl_dir=dl_dir
    )

    # Persist data now that thread has been grabbed
    logging.info(u'Committing')
    session.commit()
    # Shutdown DB
    logging.info(u'Ending DB session')
    session.close()# Release connection back to pool.
    engine.dispose()# Close all connections.

    logging.warning(u'exiting thread_simple_dev()')
    return


def from_config():
    logging.info(u'Running from_config()')

    # Load config file

    # Set run parameters
    board_name = u'tg'
    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
    connection_string = common.convert_filepath_to_connect_string(filepath=db_filepath)
    logging.debug(u'connection_string={0!r}'.format(connection_string))
    thread_num = 40312936 # https://warosu.org/tg/thread/40312936 #Ghost post example
    thread_num = 40312392 # https://warosu.org/tg/thread/40312392 # Tripcode example
    dl_dir = os.path.join(u'dl', u'wtest', u'{0}'.format(board_name))
    # Setup requests session
    req_ses = requests.Session()
    # Prepare board DB classes/table mappers
    SimplePosts = warosu_tables.table_factory_simple_posts(Base, board_name)

    # Setup/start/connect to DB
    logging.debug(u'Connecting to DB')
    if db_filepath:
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

    # Save a thread
    simple_save_thread(
        db_ses=session,
        req_ses=req_ses,
        Threads=Threads,
        SimplePosts=SimplePosts,
        board_name=board_name,
        thread_num=thread_num,
        dl_dir=dl_dir
    )

    # Persist data now that thread has been grabbed
    logging.info(u'Committing')
    session.commit()
    # Shutdown DB
    logging.info(u'Ending DB session')
    session.close()# Release connection back to pool.
    engine.dispose()# Close all connections.

    logging.info(u'Exiting from_config()')
    return



def main():
##    thread_simple_dev()
    from_config()
    return


if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "w_thread_simple.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
