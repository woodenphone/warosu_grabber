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
import w_post_extractors

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
        u'<span>File: ([a-zA-Z0-9 ]+), (\d+)x(\d+), ([a-zA-Z0-9\.]+)</span>'
        u''
        u''
        u''
        u''
    )
    logging.debug(u'f_regex={0!r}'.format(f_regex))

    file_regex_1 = (
        u'<span>File: '
        u'(\w+ )'# <var make_filesize_string($media_size)>
        u', '
        u'(\d+)'# <var $media_w>
        u'x'
        u'(\d+)'# <var $media_h>
        u', '
        u'([a-zA-Z0-9]+)'# <var $media>
        u'([a-zA-Z0-9=]+)'# <var $media_hash>
        u'</span>'
        u'\n'
        u'\[<a href="'
        +board_shortname+#<var $self>
        u'/image/'
        u'([a-zA-Z0-9=]+)'# <var urlsafe_b64encode(urlsafe_b64decode($media_hash))>
        u'>">View same</a>\]'
    )
    # Extract f
    f_regex_2 = (
        ''
    )
    logging.debug(u'file_regex_1={0!r}'.format(file_regex_1))

    file_values = {}
    return file_values






def fuuka_post(fragment, thread_num, thread_url, board_images_path):
    """Extract fuuka values."""
    post_data = {}
##    # doc_id int unsigned not null auto_increment,
##    # id decimal(39,0) unsigned not null default '0',
    # num int unsigned not null,
    num, subnum = w_post_extractors.num_subnum(fragment)
    post_data['num'] = num
    post_data['subnum'] = subnum

    # parent int unsigned not null default '0',
    post_data['parent'] = thread_num# TODO Verify this is correct

    # timestamp int unsigned not null,
    timestamp = w_post_extractors.timestamp(fragment)
    logging.debug(u'timestamp={0!r}'.format(timestamp))
    post_data['timestamp'] = timestamp

    # preview varchar(20),
    # preview_w smallint unsigned not null default '0',
    # preview_h smallint unsigned not null default '0',
    preview, preview_w, preview_h = w_post_extractors.preview_preview_w_preview_h(fragment)
    post_data['preview'] = preview# Thumbnail filename on disk
    post_data['preview_w'] = preview_w
    post_data['preview_h'] = preview_h

    # media text,
    # media_w smallint unsigned not null default '0',
    # media_h smallint unsigned not null default '0',
    # media_size int unsigned not null default '0',
    media, media_w, media_h, media_size = w_post_extractors.media_media_w_media_h_media_size(fragment)
    post_data['media'] = media# Original filename
    post_data['media_w'] = media_w# media_w
    post_data['media_h'] = media_h# media_h
    post_data['media_size'] = media_size# media_size (lowered resolution?)TODO Investigate accuracy of given values

    # media_hash varchar(25),
    media_hash = w_post_extractors.media_hash(fragment)
    post_data['media_hash'] = media_hash# Image MD5 hash encoded in base64
    logging.debug(u'media_hash={0!r}'.format(media_hash))

    # media_filename varchar(20),
    media_filename = w_post_extractors.media_filename(fragment)
    post_data['media_filename'] = media_filename# Filename on disk
    logging.debug(u'media_filename={0!r}'.format(media_filename))

    # spoiler bool not null default '0',
    spoiler = w_post_extractors.spoiler(fragment)
    post_data['spoiler'] = spoiler# Post was spoilered on 4chan
    logging.debug(u'spoiler={0!r}'.format(spoiler))

    # deleted bool not null default '0',
    deleted = w_post_extractors.deleted(fragment)
    post_data['deleted'] = deleted# Post was deleted on 4chan
    logging.debug(u'deleted={0!r}'.format(deleted))

    # capcode enum('N', 'M', 'A', 'G') not null default 'N',
    capcode = w_post_Extractors.capcode(fragment)

    # email varchar(100),
##    email = w_post_Extractors.email(fragment)

    # name varchar(100),
    name = name(fragment)
    name = w_post_extractors.name(fragment)
    post_data['name'] = name
    logging.debug(u'name={0!r}'.format(name))

    # trip varchar(25),
    trip = w_post_extractors.trip(fragment)
    post_data['trip'] = trip
    logging.debug(u'trip={0!r}'.format(trip))

    # title varchar(100),
    # <if $title><span class="filetitle"><var $title></span>&nbsp;</if>
    title_search = re.search('<span class="filetitle">([^<]+)</span>&nbsp;', fragment)
    title = title_search.group(1)
    post_data['title'] = title
    logging.debug(u'title={0!r}'.format(title))

    # comment text,
    post_data['comment'] = comment
    logging.debug(u'comment={0!r}'.format(comment))

##    # delpass tinytext,

    # sticky bool not null default '0',
    sticky = w_post_extractors.sticky(fragment)
    post_data['sticky'] = sticky
    logging.debug(u'sticky={0!r}'.format(sticky))

    logging.debug(u'post_data={0!r}'.format(post_data))
    return post_data


def parse_ghost_post(fragment, thread_num, thread_url):# TODO: Write tests
    """Accepts a post's html fragment for a thread.
    Asafu/Foolfuuka values"""
    # doc_id: Cannot retrive
    # num, subnum:
    #num_search = re.search(u'<input name="delete" type="checkbox" value="(\d+),(\d+)', fragment)
    num_search_regex = (
    u'<input '
    u'(?:name="delete"|type="checkbox"| )+'# These can be in either order, and are seperated by spaces
    u'value="(\d+),(\d+)'
    )
    num_search = re.search(num_search_regex, fragment)
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
        u'<span>File: '
        u'(\w+ )'# <var make_filesize_string($media_size)>
        u', '
        u'(\d+)'# <var $media_w>
        u'x'
        u'(\d+)'# <var $media_h>
        u', '
        u'([a-zA-Z0-9]+)'# <var $media>
        u'</span>'
        u'\n'
    )
##    logging.debug(u'file_regex_1={0!r}'.format(file_regex_1))
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
        u'</span>'# Match end of file size display line to avoid mismatches
        u'\n'
        u'\[<a href="'
        u'[a-zA-Z0-9]+?'#<var $self> board shortname
        u'/image/'
        u'([a-zA-Z0-9=]+)'# <var urlsafe_b64encode(urlsafe_b64decode($media_hash))>
        u'>">View same</a>\]'
    )
    f_hash_search = re.search(file_hash_regex, fragment)
    if f_hash_search:
        media_hash =  f_hash_search.group(0)# media_hash
    else:
        media_hash = None# media_hash
    # media_id: Can we obtain this?

    # op:
    # OP has same post num as thread num
    op = (int(thread_num) == int(num))


    # timestamp:
    # Find timestamp string
    # <span class="posttime" title="<var deyotsutime($date) * 1000>"><var scalar gmtime($date)></span></label>
    # '<span class="posttime" title="1474172041000">Sun Sep 18 12:14:01 2016</span></label>'
    timestamp_search = re.search(u'<span class="posttime" title="(\d+)">', fragment)
    timestamp_string = timestamp_search.group(1)
    # Convert timestamp string to correct unixtime
    timestamp = int(timestamp_string)# TODO Ensure we're not off by a factor of a thousand or so (check actual DB values)
    logging.debug(u'timestamp={0!r}'.format(timestamp))

    # timestamp_expired:
    # (Can we retrieve this?)

    # Image preview values
    # <if $file><img class="thumb" src="<var $file>" alt="<var $num>" <if $preview_w>width="<var $preview_w>" height="<var $preview_h>"</if> /></if>
    # ...
    # <if not $file><img src="<const MEDIA_LOCATION_HTTP>/error.png" alt="ERROR" class="nothumb" title="No thumbnail" /></if>
    preview_search = re.search('<img class="thumb" src="([^"]+)" alt="([^"]+)" (?:width="([^"]+)" height="([^"]+)")?', fragment)
    if preview_search:
        logging.debug('Found thumbnail')
        thumb_src = preview_search.group(1)
        thumb_alt = preview_search.group(2)
        if preview_search.group(3):
            logging.debug('Found thumbnail dimensions')
            preview_w = preview_search.group(3)
            preview_h = preview_search.group(4)
        else:
            preview_w = None
            preview_h = None
    else:
        thumb_src = None
        thumb_alt = None
        preview_w = None
        preview_h = None
    # preview_orig:

    # preview_w:

    # preview_h:

    # media_filename: 'media_filename varchar(20)'



    # media_w
    # Done previously in funtion

    # media_h:
    # Done previously in funtion

    # media_size:

    # media_hash:
    # Done previously in funtion

    # media_orig:


    # spoiler:

    # deleted:

    # capcode:

    # email: CLOUDFLARE FUCKS THIS UP

    # name:
    # <span itemprop="name">jubels</span>
    name_search = re.search(u'<span itemprop="name">([^<]+)</span>', fragment)
    name = name_search.group(1)
    logging.debug(u'name={0!r}'.format(name))

    # trip:
    # <span class="postertrip<if $capcode eq 'M'> mod</if><if $capcode eq 'A'> admin</if><if $capcode eq 'D'> dev</if>">&nbsp;<var $trip></span><if $email></a></if></if>
    # TODO: Handle capcode presence
    trip_search = re.search(u'<span class="postertrip">&nbsp;([a-zA-Z0-9!/]+)</span>', fragment)
    if trip_search:
        trip = trip_search.group(1)
    else:
        trip = None
    logging.debug(u'trip={0!r}'.format(trip))

    # title:
    title_search = re.search(u'', fragment)

    # comment:
    # Extract HTML segment
    # <blockquote><p><var $comment></p></blockquote>
    # or:
    # <blockquote><p>
	# <var $comment>
	# </p></blockquote>
	# </td>
	# </tr></table>
    soup = bs4.BeautifulSoup(fragment, u'html.parser')# TODO Maybe find more efficient way to grab this value than bs4?
    comment_element = soup.find(name=u'p', attrs={u'itemprop':'text',})
    comment = str(comment_element)
    logging.debug(u'comment={0!r}'.format(comment))
##    comment_search = re.search(u'<blockquote><p>([^(?:</p>)])</p></blockquote>', fragment)
    # Reverse formatting
    # TODO
    # Cloudfire email hiding
    # BBCode

    # delpass: Can't retrieve this
    # sticky: (Is this OP-only?)
    # locked: (Is this OP-only?)
    # poster_hash:
    # poster_country:
    # exif:

    TODO = 'w_thread_full.py 2018-11 NOT IMPLIMENTED YET dummy string'# Dummy string instead of None because we want to pass NULL for absent values
    # Assemble collected values
    post_data = {
        #u'doc_id': doc_id,
        #u'media_id': media_id,
        #u'poster_ip': poster_ip,
        u'num':num,# Post ID number
        u'subnum':subnum,# Ghost post number, 0 if not ghost post
        u'thread_num': thread_num,# Thread ID number
        u'op': op,# TODO
        u'timestamp': timestamp,# Timestamp, secons-since-epoch?
        u'timestamp_expired': TODO,# TODO
        u'preview_orig': TODO,# ?thumbnail image filename on server?
        u'preview_w': TODO,# TODO
        u'preview_h': TODO,# TODO
        u'media_filename': TODO,# ?full image filename on server?
        u'media_w': media_w,# Full image height in pixels
        u'media_h': media_h,# Full image width in pixels
        u'media_size': TODO,# TODO # Full image size (WHAT UNITS?)
        u'media_hash': media_hash,# Image MD5 hash encoded in base64
        u'media_orig': TODO,# TODO ?Original image filename?
        u'spoiler': TODO,# TODO
        u'deleted': TODO,# TODO
        u'capcode': TODO,# Poster capcode
        u'email': TODO,# Poster email
        u'name': TODO,# Poster name
        u'trip': trip,# TODO
        u'title': TODO,# Post comment
        u'comment': comment,# Post text
        u'delpass': TODO,# TODO
        u'sticky': TODO,# TODO
        u'locked': TODO,# TODO
        u'poster_hash': TODO,# TODO
        u'poster_country': TODO,# TODO
        u'exif': TODO,# TODO
        u'TODO': TODO,# TODO
        u'TODO': TODO,# TODO

    }
    logging.debug(u'post_data={0!r}'.format(post_data))
    return post_data


def split_thread_into_posts(html):# TODO: Write tests
    """Split thread into post HTML fragments.
    Start of OP:           <div id="p40312936" itemscope="" itemtype="http://schema.org/DiscussionForumPosting">
    1st line of next post: <table itemscope="" itemtype="http://schema.org/Comment"><tbody><tr>
    2nd line of next post: <td class="doubledash">&gt;&gt;</td>
    3rd line of next post: <td class="reply" id="p40313137">"""
    # Select only the OP
    op_fragment_search = re.search('(<div id="p\d+" itemscope itemtype="http://schema.org/DiscussionForumPosting">(?:.|\n|\t)+?)<table itemscope itemtype="http://schema.org/Comment"><tr>', html)
    op_fragment = op_fragment_search.group(1)
    # (?:.|\n|\t) is to match any character, because some regex engines do not do DOTALL functionality
    reply_fragments = re.findall('(<table itemscope itemtype="http://schema.org/Comment">(?:.|\n|\t)+?</table>)', html)
    post_fragments = [op_fragment] + reply_fragments
##    logging.debug(u'post_fragments={0!r}'.format(post_fragments))
    logging.debug(u'len(post_fragments)={0!r}'.format(len(post_fragments)))
    return post_fragments


def detect_ghost_post(fragment):# TODO: Write tests
    """Given a post HTML fragment, determine if it is a ghost post."""
    if ('<img class="inline" src="/media/internal.png" width="19" height="17" alt="[INTERNAL]" title="This is not an archived reply" />&nbsp;' in fragment):
        return True
    else:
        return False


def parse_thread(html, thread_num, thread_url, board_images_path):
    """Split into post HTML fagments
    Make sure OP is included"""
    ghost_posts = []
    # Split thread into post HTML fragments
    fragments = split_thread_into_posts(html)
    # Process each fragment of the page
    for fragment in fragments:
        # Decide if post needs recording
        if ( detect_ghost_post(fragment) ):
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




def dev_thread_complex():
    """Dev playground"""
    logging.warning(u'running dev_thread_complex()')
    # Ghost post example: https://warosu.org/tg/thread/40312936
    thread_num = 40312936
    thread_url = u'https://warosu.org/tg/thread/40312936'
    thread_filepath = os.path.join('example_threads', 'warosu.tg.40312936.html')
    board_images_path = ''

##    # Tripcode example: https://warosu.org/tg/thread/40312392
##    thread_num = 40312392
##    thread_url = u'https://warosu.org/tg/thread/40312392'
##    thread_filepath = os.path.join('example_threads', 'warosu.tg.40312392.html')
    board_images_path = ''

    # Load from file
    html = common.read_file(thread_filepath)
    # Parse thread
    thread = parse_thread(html, thread_num, thread_url, board_images_path)
    logging.debug(u'thread={0!r}'.format(thread))
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
