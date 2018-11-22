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

    current_page_filename = u'df{df}.dt{dt}.html'.format(df=date_from, dt=date_to)
    # <base>/thread_listings/<board_name>/html/<offset>.html
##    current_page_filepath = os.path.join(
##        dl_dir,
##        u'thread_listings',
##        u'{0}'.format(board_name),
##        u'html',
##        current_page_filename
##    )
    current_page_filepath = os.path.join(# TODO: Put normal dl path generration back in
        dl_dir,
        u'temp',
        current_page_filename
    )
    logging.debug(u'current_page_url={0!r}'.format(current_page_url))
    logging.debug(u'current_page_filename={0!r}'.format(current_page_filename))
    logging.debug(u'current_page_filepath={0!r}'.format(current_page_filepath))
    # Load page
    page_res = common.fetch(requests_session=req_ses, url=current_page_url)
    # Save page for debug
    common.write_file(file_path=current_page_filepath, data=page_res.content)
    return page_res


def count_search_ranges(date_from, date_to):
    pass


def date_to_warosu(date):
    """Convert datetime objects to YYYY-MM-DD strings for Warosu's Fuuka searh"""
    return date.strftime('%Y-%m-%d')


def convert_list_str_to_int(values):
    out_list = []
    for value in values:
        out_list.append(int(value))
    return out_list


def scan_board_range(req_ses, board_name, dl_dir,
    date_from, date_to):
    logging.debug(u'save_board_range() args={0!r}'.format(locals()))# Record arguments.

    # Iterate over range
    weekdelta = datetime.timedelta(days=7)# One week's difference in time towards the future
    working_date = date_from# Initialise at low end
    all_thread_ids = []
    while working_date < date_to:
        logging.debug(u'working_date={0!r}'.format(working_date))
        fut_date = working_date + weekdelta
        logging.debug(u'fut_date={0!r}'.format(fut_date))
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
            logging.debug(u'len(all_thread_ids)={0!r}'.format(len(all_thread_ids)))
            # Check if end of results reached
            if len(thread_ids) == 0:
                logging.info('No threads found on this page, moving on to next date range')
                break
            continue
        # Go forward a week
        logging.debug('Incrementing working date')
        working_date += weekdelta
        continue
    logging.info(u'Finished searching')
    return


def remove_cf_email_garbage(html):
    # erase cloudflare email hiding junk
    clean_html = re.sub('<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="\w+">\[email&#160;protected\]</a>', '', html)
    return clean_html



##def parse_post(fragment, thread_num, ghost_only=False):
##    """Accepts a post's html fragment for a thread"""
##    # doc_id: Cannot retrive
##    # num, subnum:
##    num_search = re.search(u'<input name="delete" type="checkbox" value="(\d+),(\d+)', fragment)
##    num_string = num_search.group(1)
##    subnum_string = num_search.group(2)
##    num = int(num_string)
##    subnum = int(subnum_string)
##    if ghost_only:
##        if subnum == 0:
##            return None
##    # media_id:
##    # op:
##    # timestamp:
##    # timestamp_expired:
##    # preview_orig:
##    # preview_w:
##    # preview_h:
##    # media_filename:
##    # media_w
##    # media_h:
##    # media_size:
##    # media_hash:
##    # media_orig:
##    # spoiler:
##    # deleted:
##    # capcode:
##    # email: CLOUDFLARE FUCKS THIS UP
##    # name:
##    # trip:
##    # title:
##    # comment:
##    # delpass: Can't retrieve this
##    # sticky:
##    # locked:
##    # poster_hash:
##    # poster_country:
##    # exif:
##    # Assemble collected values
##    post_data = {
##        u'num':num,
##        u'subnum':subnum,
##        u'thread_num': thread_num,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##        u'TODO': TODO,
##
##    }
##    return post_data






def parse_post_include_file(html):
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
    ''
    ''
    ''
    ''
    ''
    )

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
    '(\w+)'# <var make_filesize_string($media_size)>
    ', '
    '(\d+)'# <var $media_w>
    'x'
    '(\d+)'# <var $media_h>
    ', '
    '([a-zA-Z0-9]+)'# <var $media>
    '<!-- '
    '([a-zA-Z0-9=]+)'# <var $media_hash>
    ' --></span>'
    )

    f_search_1 = re.search(file_regex_1, fragment)
    if f_search_1:
        # File present
        filesize_string = f_search_1.group(1)
        media_w = f_search_1.group(2)
        media_h = f_search_1.group(3)
        media = f_search_1.group(4)
        media_hash = f_search_1.group(5)
    else:
        # No file
        filesize_string = None
        media_w = None
        media_h = None
        media = None
        media_hash = None

    file_regex_2 = (
    ''
    ''
    ''
    ''
    )


    # media_id:


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
    # Split into post HTML fagments
    # Make sure OP is included
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




def dev3():
    logging.warning(u'running dev3()')
    # Load from file
    thread_num = 1
    thread_url = u''
    html = common.read_file(os.path.join())
    # Parse thread
    posts = parse_thread(html, thread_num, thread_url)
    logging.warning(u'exiting dev3()')
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
    return

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
    dev3()
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
