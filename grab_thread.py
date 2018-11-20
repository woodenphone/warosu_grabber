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




def simple_save_thread(db_ses, req_ses, Threads, Posts, board_name, thread_num, dl_dir):
    logging.info(u'Fetching thread: {0!r}'.format(thread_num))
    # Calculate values
    thread_url = u'https://warosu.org/{bn}/thread/{tn}'.format(bn=board_name, tn=thread_num)
    thread_filename = 'warosu.{bn}.{tn}.html'.format(bn=board_name, tn=thread_num)
    thread_filepath = os.path.join(dl_dir, u'{0}'.format(board_name), thread_filename)
    logging.debug(u'thread_url={0!r}'.format(thread_url))

    # Look for all posts for this thread in DB
    logging.debug('About to look for existing posts for this thread')
    existing_posts_q = db_ses.query(Posts)\
        .filter(Posts.thread_num == thread_num,)
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
    posts = soup.find_all(name=u'table', attrs={u'itemtype':'http://schema.org/Comment',})
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
            logging.debug(u'Posts={0!r}'.format(Posts))
            logging.debug(u'num={0!r}'.format(num))
            logging.debug(u'subnum={0!r}'.format(subnum))
            logging.debug(u'thread_num={0!r}'.format(thread_num))
            logging.debug(u'post_html={0!r}'.format(post_html))
            # Add post to DB
            new_post = Posts(
                num = num,
                subnum = subnum,
                thread_num = thread_num,
                post_html = post_html,
            )
            db_ses.add(new_post)
            logging.info(u'Inserted a ghost post into Posts')
    logging.info(u'Fetched thread: {0!r}'.format(thread_num))
    return


def scan_board_range(req_ses, board_name, dl_dir,
    low_post_num, high_post_num):
    logging.debug(u'save_board_range() args={0!r}'.format(locals()))# Record arguments.
    # Iterate over range
    for page_num in xrange(low, high):
        current_page_url = u'https://warosu.org/tg/?task=page&page={pn}&ghost=View+in+Ghost+mode'.format()
        current_page_filename = u''.format()
        # <base>/thread_listings/<board_name>/html/<offset>.html
        current_page_filepath = os.path.join(
            dl_dir,
            u'thread_listings',
            u'{0}'.format(board_name),
            u'html',
            current_page_filename
        )
        logging.debug(u'current_page_url={0!r}'.format(current_page_url))
        logging.debug(u'current_page_filename={0!r}'.format(current_page_filename))
        logging.debug(u'current_page_filepath={0!r}'.format(current_page_filepath))
        # Load page
        page_res = common.fetch(requests_session=req_ses, url=thread_url)
        # Save page for debug
        write_file(file_path=current_page_filepath, data=page_res.content)
        # Extract thread numbers
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


##    sqlalchemy.insert(Posts)\
##    .values(
##        num = 1,
##        subnum = 2,
##        thread_num = 3,
##        post_html = u'FAKE POST',
##    )
##    sqlalchemy.insert(Posts)\
##        .values(
##            num = 1,
##            subnum = 2,
##            thread_num = 3,
##            post_html = u'FAKE POST',
##            primary_key=12
##        )
##    new_post = Posts(
##        num = 1,
##        subnum = 2,
##        thread_num = 3,
##        post_html = u'FAKE POST',
##    )
##    session.add(new_post)

    # Save a thread
    simple_save_thread(
        db_ses=session,
        req_ses=req_ses,
        Threads=Threads,
        Posts=Posts,
        board_name=board_name,
        thread_num=thread_num,
        dl_dir=dl_dir
    )

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
