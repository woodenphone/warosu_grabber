#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     02-12-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import time
import os
import logging
import datetime
import re
# Remote libraries
import requests# For talking to websites
import requests.exceptions
import sqlite3# Because spinning up a new DB is easier this way
import sqlalchemy# For talking to DBs
from sqlalchemy.ext.declarative import declarative_base
import yaml
# local
import common# Utility & common functions
import w_thread_full# Thread parsing
import tables_asagi# Asagi/Foolfuuka-style tables







def save_thread_asagi(req_ses, db_ses, board_name, thread_num, FFThreads, FFPosts, FFImage):# TODO
    """Save a thread into a asagi-style table.
    Only cares about ghost posts."""
    # Generate thread URL
    # e.g. https://warosu.org/tg/thread/40312936
    thread_url = u'https://warosu.org/{bn}/thread/{tn}'.format(bn=board_name, tn=thread_num)
    # Load thread HTML
    logging.debug(u'Loading HTML for thread: {0!r}'.format(thread_url))
    thread_res = common.fetch(requests_session=req_ses, url=thread_url)
    html = thread_res.content.decode('utf8')
    board_images_path = u'data/{bn}'.format(bn=board_name)# Used for HTML parsing. No trailing slash.
    # Parse thread HTML
    logging.debug(u'Parsing posts for thread: {0!r}'.format(thread_url))
    thread = w_thread_full.parse_thread(
        html=html,
        thread_num=thread_num,
        thread_url=thread_url,
        board_images_path=board_images_path,
    )
    # Look for all posts for this thread in DB
    logging.debug('About to look for existing posts for this thread')
    existing_posts_q = db_ses.query(FuukaPosts)\
        .filter(FuukaPosts.parent == thread_num,)# TODO Confirm parent is always == thread_num
    existing_posts = existing_posts_q.all()
    logging.debug(u'existing_posts={0!r}'.format(existing_posts))
    logging.debug(u'len(existing_posts)={0!r}'.format(len(existing_posts)))
    # Insert posts that have not already been saved
    logging.debug(u'Inserting posts {0!r} for thread: {1!r}'.format(len(thread[u'ghost_posts']), thread_url))
    post_rows = []
    for gp in thread[u'ghost_posts']:
        # Skip existing posts
        if (
            is_post_in_results(
                results=existing_posts,
                thread_num=thread_num,
                num=gp[u'num'],
                subnum=gp[u'subnum']
            )):
            continue# Post already in DB
        # Stage post
        logging.info(u'gp={0!r}'.format(gp))
        new_row = FuukaPosts(
            num = gp[u'num'],
            subnum = gp[u'subnum'],
            parent = gp[u'parent'],
            timestamp = gp[u'timestamp'],
            preview = gp[u'preview'],
            preview_w = gp[u'preview_w'],
            preview_h = gp[u'preview_h'],
            media = gp[u'media'],
            media_w = gp[u'media_w'],
            media_h = gp[u'media_h'],
            media_size = gp[u'media_size'],
            media_hash = gp[u'media_hash'],
            media_filename = gp[u'media_filename'],
            spoiler = gp[u'spoiler'],
            deleted = gp[u'deleted'],
            capcode = gp[u'capcode'],
            email = gp[u'email'],
            name = gp[u'name'],
            trip = gp[u'trip'],
            title = gp[u'title'],
            comment = gp[u'comment'],
            delpass=None,# Can't be grabbed, server-side only value
            sticky = gp[u'sticky'],
            )
        post_rows.append(new_row)
    if post_rows:
        db_ses.add_all(post_rows)
        # Commit changes
        db_ses.commit()
        logging.info(u'Saved thread: {0!r}'.format(thread_url))
    return










def save_threads_asagi(db_ses, req_ses, board_name, thread_list_path, FFThreads, FFPosts, FFImage):
    """Save using asagi DB schema"""
    logging.debug(u'save_threads_asagi() locals()={0!r}'.format(locals()))# Record arguments
    logging.info('Saving threads from list file:{0!r}'.format(thread_list_path))
    lc = 0# List counter
    with open(thread_list_path, 'r') as list_f:
        for line in list_f:
            lc += 1
            logging.debug(u'lc={0!r}, line={1!r}'.format(lc, line))
            # Decode line
            if line[0] != 't':# Only accept lines marked as threads
                continue
            wrk_num = line[1:]# Discard initial 't'
            thread_num = wrk_num.strip()# Discard trailing whitespace
            logging.debug(u'thread_num={0!r}'.format(thread_num))
            # Save a thread
            save_thread_asagi(
                req_ses=req_ses,
                db_ses=db_ses,
                board_name=board_name,
                thread_num=thread_num,
                FuukaPosts=FuukaPosts
            )
            continue
        logging.info('Processed all lines in file:{0!r}'.format(thread_list_path))
    logging.info('Finished saving threads')
    return



def from_config():# TODO
    logging.info(u'Running from_config()')
    # Load config file
    config_path = os.path.join(u'config', 'save_threads.yaml')
    config = YAMLConfigSaveThreads(config_path)
    # Set values from config file
    board_name = unicode(config.board_name)
    db_filepath = unicode(config.db_filepath)
    connection_string = unicode(config.connection_string)
    dl_dir = unicode(config.dl_dir)
    echo_sql = config.echo_sql

    # Manually-set values # TODO REMOVE THIS
    thread_list_path = os.path.join('temp', 'tg.threadslist.txt')

    # Setup requests session
    req_ses = requests.Session()
    # Prepare board DB classes/table mappers

    # Asagi/Foolfuuka-style DB
    FFThreads = foolfuuka_threads(Base, board_name)
    FFPosts = foolfuuka_posts(Base, board_name)
    FFImage = foolfuuka_images(Base, board_name)

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

    # Asagi/Foolfuuka-style DB
    save_threads_asagi(
        db_ses=db_ses,
        req_ses=req_ses,
        board_name=board_name,
        thread_list_path=thread_list_path,
        FFThreads=FFThreads,
        FFPosts=FFPosts,
        FFImage=FFImage,
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
    pass

if __name__ == '__main__':
    main()
