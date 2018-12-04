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
import thread_parsers

Base = declarative_base()# Setup system to keep track of tables and classes






def fuuka_post(fragment, thread_num, thread_url, board_images_path):
    """Extract fuuka values."""
    post_data = {}
##    # doc_id int unsigned not null auto_increment,
##    # id decimal(39,0) unsigned not null default '0',
    # num int unsigned not null,
    num, subnum = thread_parsers.num_subnum(fragment)
    post_data[u'num'] = num
    post_data[u'subnum'] = subnum

    # parent int unsigned not null default '0',
    post_data[u'parent'] = thread_num# TODO Verify this is correct

    # timestamp int unsigned not null,
    timestamp = thread_parsers.timestamp(fragment)
    post_data[u'timestamp'] = timestamp

    # preview varchar(20),
    # preview_w smallint unsigned not null default '0',
    # preview_h smallint unsigned not null default '0',
    preview, preview_w, preview_h = thread_parsers.preview_preview_w_preview_h(fragment)
    post_data[u'preview'] = preview# Thumbnail filename on disk
    post_data[u'preview_w'] = preview_w
    post_data[u'preview_h'] = preview_h

    # media text,
    # media_w smallint unsigned not null default '0',
    # media_h smallint unsigned not null default '0',
    # media_size int unsigned not null default '0',
    media, media_w, media_h, media_size = thread_parsers.media_media_w_media_h_media_size(fragment)
    post_data[u'media'] = media# Original filename
    post_data[u'media_w'] = media_w# media_w
    post_data[u'media_h'] = media_h# media_h
    post_data[u'media_size'] = media_size# media_size (lowered resolution?)TODO Investigate accuracy of given values

    # media_hash varchar(25),
    media_hash = thread_parsers.media_hash(fragment)
    post_data[u'media_hash'] = media_hash# Image MD5 hash encoded in base64

    # media_filename varchar(20),
    media_filename = thread_parsers.media_filename(fragment, board_images_path)
    post_data[u'media_filename'] = media_filename# Filename on disk

    # spoiler bool not null default '0',
    spoiler = thread_parsers.spoiler(fragment)
    post_data[u'spoiler'] = spoiler# Post was spoilered on 4chan

    # deleted bool not null default '0',
    deleted = thread_parsers.deleted(fragment)
    post_data[u'deleted'] = deleted# Post was deleted on 4chan

    # capcode enum('N', 'M', 'A', 'G') not null default 'N',
    capcode = thread_parsers.capcode(fragment)
    post_data[u'capcode'] = capcode

    # email varchar(100),
##    email = thread_parsers.email(fragment)
    post_data[u'email'] = u'EMAIL FINDING NOT IMPLIMENTED!'

    # name varchar(100),
    name = thread_parsers.name(fragment)
    post_data[u'name'] = name

    # trip varchar(25),
    trip = thread_parsers.trip(fragment)
    post_data[u'trip'] = trip

    # title varchar(100),
    title = thread_parsers.title(fragment)
    post_data[u'title'] = title

    # comment text,
    comment = thread_parsers.comment(fragment)
    post_data[u'comment'] = comment
##    # delpass tinytext,
    # sticky bool not null default '0',
    sticky = thread_parsers.sticky(fragment)
    post_data[u'sticky'] = sticky
    logging.debug(u'post_data={0!r}'.format(post_data))
    return post_data



def split_thread_to_file(html, thread_num, filepath_template):
    # Split thread into post HTML fragments
    fragments = thread_parsers.split_thread_into_posts(html)
    # Process each fragment of the page
    offset = 0
    for fragment in fragments:
        filepath = filepath_template.format(tnum=thread_num, offset=offset)
        common.write_file(filepath, fragment)
        offset += 1
    return


def parse_thread(html, thread_num, thread_url, board_images_path):
    """Split into post HTML fagments
    Make sure OP is included"""
    ghost_posts = []
    # Split thread into post HTML fragments
    fragments = thread_parsers.split_thread_into_posts(html)
    # Process each fragment of the page
    for fragment in fragments:
        # Decide if post needs recording
        if ( thread_parsers.detect_ghost_post(fragment) ):
            # This is a ghost post
            # Extract data from post
            post = fuuka_post(fragment, thread_num, thread_url, board_images_path)# Fuuka-style values
##            post = parse_ghost_post(fragment, thread_num, thread_url)# Asagi-style values
            logging.debug(u'post={0!r}'.format(post))
            ghost_posts.append(post)
    thread = {
        u'thread_num':thread_num,
        u'thread_url':thread_url,
        u'ghost_posts': ghost_posts,
    }
    logging.debug(u'thread={0!r}'.format(thread))
    return thread


def split_file():
    # Ghost post example: https://warosu.org/tg/thread/40312936
    thread_num = 40312936
    thread_url = u'https://warosu.org/tg/thread/40312936'
    thread_filepath = os.path.join(u'example_threads', u'warosu.tg.40312936.html')
    board_images_path = u'data/tg'# No trailing slash

    # Tripcode example: https://warosu.org/tg/thread/40312392
    thread_num = 40312392
    thread_url = u'https://warosu.org/tg/thread/40312392'
    thread_filepath = os.path.join(u'example_threads', u'warosu.tg.40312392.html')
    board_images_path = u'data/tg'# No trailing slash

    # Load from file
    file_data = common.read_file(thread_filepath)

    # Dump thread into one file per post
    file_data = common.read_file(thread_filepath)
    split_thread_to_file(
        html=file_data,
        thread_num=thread_num,
        filepath_template=os.path.join(u'tests', str(thread_num), u't{tnum}.o{offset}.html')
    )
    return


def dev():
    """Dev playground"""
    logging.warning(u'running dev()')
    # Ghost post example: https://warosu.org/tg/thread/40312936
    thread_num = 40312936
    thread_url = u'https://warosu.org/tg/thread/40312936'
    thread_filepath = os.path.join(u'example_threads', u'warosu.tg.40312936.html')
    board_images_path = u'data/tg'

##    # Tripcode example: https://warosu.org/tg/thread/40312392
##    thread_num = 40312392
##    thread_url = u'https://warosu.org/tg/thread/40312392'
##    thread_filepath = os.path.join('example_threads', 'warosu.tg.40312392.html')
##    board_images_path = 'data/tg'

    # Load from file
    file_data = common.read_file(thread_filepath)
    html = file_data.decode('utf8')

    # Parse thread
    thread = parse_thread(html, thread_num, thread_url, board_images_path)
    logging.debug(u'thread={0!r}'.format(thread))
    logging.warning(u'exiting dev()')
    return


def main():
    dev()
    return


if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "parse_thread_fuuka.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
