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










def parse_post_include_file(html, board_shortname):
    """
    use constant POSTS_INCLUDE_FILE => <<'HERE';
    <if $file>
    	<span>File: <var make_filesize_string($media_size)>, <var $media_w>x<var $media_h>, <var $media><!-- <var $media_hash> --></span>

    	[<a href="<var $self>/image/<var urlsafe_b64encode(urlsafe_b64decode($media_hash))>">View same</a>] [<a href="http://iqdb.org/?url=<var $absolute_path><var $file>">iqdb</a>]

    	<br />

    	<if $fullfile><a href="<var $fullfile>">
    	<elsif $media_filename><a rel="noreferrer" href="<var "$images_link/$media_filename">">
    	</if>

    	<if $file><img class="thumb" src="<var $file>" alt="<var $num>" <if $preview_w>width="<var $preview_w>" height="<var $preview_h>"</if> /></if>

    	<if $fillfile or $media_filename></a></if>

    	<if not $file><img src="<const MEDIA_LOCATION_HTTP>/error.png" alt="ERROR" class="nothumb" title="No thumbnail" /></if>
    </if>
    HERE
    """
    f_regex = (
        '<span>File: ([a-zA-Z0-9 ]+), (\d+)x(\d+), ([a-zA-Z0-9\.]+)</span>'
        ''
        ''
        ''
        ''
    )
    logging.debug(u'f_regex={0!r}'.format(f_regex))

    file_regex_1 = (
        '<span>File: '
        '(\w+ )'# <var make_filesize_string($media_size)>
        ', '
        '(\d+)'# <var $media_w>
        'x'
        '(\d+)'# <var $media_h>
        ', '
        '([a-zA-Z0-9]+)'# <var $media>
        '([a-zA-Z0-9=]+)'# <var $media_hash>
        '</span>'
        '\n'
        '\[<a href="'
        +board_shortname+#<var $self>
        '/image/'
        '([a-zA-Z0-9=]+)'# <var urlsafe_b64encode(urlsafe_b64decode($media_hash))>
        '>">View same</a>\]'
    )
    # Extract f
    f_regex_2 = (
        ''
    )
    logging.debug(u'file_regex_1={0!r}'.format(file_regex_1))



    file_values = {}
    return file_values



def parse_ghost_post(fragment, thread_num):
    """Accepts a post's html fragment for a thread"""
    # doc_id: Cannot retrive
    # num, subnum:
    num_search = re.search(u'<input name="delete" type="checkbox" value="(\d+),(\d+)', fragment)
    num_string = num_search.group(1)
    subnum_string = num_search.group(2)
    num = int(num_string)
    subnum = int(subnum_string)
    if subnum == 0:
        return None

    #
    """
    from templates.pl POSTS_INCLUDE_FILE
    to match:
    <span>File: <var make_filesize_string($media_size)>, <var $media_w>x<var $media_h>, <var $media><!-- <var $media_hash> --></span>
    """
    file_regex_1 = (
        '<span>File: '
        '(\w+ )'# <var make_filesize_string($media_size)>
        ', '
        '(\d+)'# <var $media_w>
        'x'
        '(\d+)'# <var $media_h>
        ', '
        '([a-zA-Z0-9]+)'# <var $media>
        '</span>'
        '\n'
    )
    logging.debug(u'file_regex_1={0!r}'.format(file_regex_1))
    f_search_1 = re.search(file_regex_1, fragment)
    if f_search_1:
        # File present
        filesize_string = f_search_1.group(1)# media_size (lowered resolution?)TODO Investigate accuracy of given values
        media_w = f_search_1.group(2)# media_w
        media_h = f_search_1.group(3)# media_h
        media = f_search_1.group(4)# media_filename?
    else:
        # No file
        filesize_string = None# media_size (lowered resolution?)TODO Investigate accuracy of given values
        media_w = None# media_w
        media_h = None# media_h
        media = None# media_filename?

    file_hash_regex = (
        '</span>'# Match end of file size display line to avoid mismatches
        '\n'
        '\[<a href="'
        '[a-zA-Z0-9]+?'#<var $self> board shortname
        '/image/'
        '([a-zA-Z0-9=]+)'# <var urlsafe_b64encode(urlsafe_b64decode($media_hash))>
        '>">View same</a>\]'
    )
    f_hash_search = re.search(file_hash_regex, fragment)
    if f_hash_search:
        media_hash =  f_hash_search.group(0)# media_hash
    else:
        media_hash = None# media_hash
    # media_id: Can we obtain this?
    # op:
    # timestamp:
    # timestamp_expired:
    # preview_orig:
    # preview_w:
    # preview_h:
    # media_filename:
    # media_w
    # media_h:
    # media_size:
    # media_hash:
    # media_orig:
    # spoiler:
    # deleted:
    # capcode:
    # email: CLOUDFLARE FUCKS THIS UP
    # name:
    # trip:
    # title:
    # comment:
    # delpass: Can't retrieve this
    # sticky:
    # locked:
    # poster_hash:
    # poster_country:
    # exif:

    # Assemble collected values
    post_data = {
        u'num':num,
        u'subnum':subnum,
        u'thread_num': thread_num,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,
        u'TODO': TODO,

    }
    return post_data



def parse_thread(html, thread_num, thread_url):
    """Split into post HTML fagments
    Make sure OP is included"""
    posts = []
    for fragment in fragments:
        # Decide if post needs recording
        if (u'' in fragment):
            # Extract data from post
            post = parse_ghost_post(fragment)
            posts.append(post)
    thread = {
        u'thread_num':thread_num,
        u'thread_url':thread_url,
        u'posts': posts,
    }
    return posts_data




def dev_thread_complex():
    """Dev playground"""
    logging.warning(u'running dev_thread_complex()')
    # Load from file
    thread_num = 1
    thread_url = u''
    html = common.read_file(os.path.join())
    # Parse thread
    posts = parse_thread(html, thread_num, thread_url)
    logging.warning(u'exiting dev_thread_complex()')
    return


def main():
    dev_thread_complex()
    return


if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "w_thread_full.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
