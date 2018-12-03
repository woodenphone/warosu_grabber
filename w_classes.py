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
import w_post_extractors# Post parsing functions
import tables_fuuka# Table class factories for Fuuka-style DB



class YAMLConfigWClasses():
    """Handle reading, writing, and creating YAML config files."""
    def __init__(self, config_path=None):
        # Set default values
        self.board_name = u'tg'# Shortname of board
        self.db_filepath = u'temp/tg.db'# Path to SQLite DBif appropriate
        self.connection_string = u'sqlite:///temp/tg.db'# SQLAlchemy connection string
        self.dl_dir = u'temp/dl/tg/'# Where to download to
        self.echo_sql = True# Will SQLAlchemy print its DB commands?
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
        logging.debug('Loaded config values: {0!r}'.format(config))
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


##class DBThread():
##    """The board as the DB sees it"""
##    def __init__(self, db_ses, thread_num, FuukaPosts):
##        self.db_ses=db_ses
##        self.thread_num = thread_num
##        self.post_rows = None
##        self.post_nums = {}
##        return
##
##    def lookup_posts(self, db_ses):
##        # Look for all posts for this thread in DB
##        logging.debug('About to look for existing posts for this thread')
##        existing_posts_q = db_ses.query(FuukaPosts)\
##            .filter(FuukaPosts.parent == thread_num,)# TODO Confirm parent is always == thread_num
##        existing_post_rows = existing_posts_q.all()
##        logging.debug(u'existing_post_rows={0!r}'.format(existing_post_rows))
##        logging.debug(u'len(existing_post_rows)={0!r}'.format(len(existing_post_rows)))
##        for existing_post_row in existing_post_rows:
##            post_num = existing_post_row.num
##            self.post_nums[post_num] = 'has'
##        return len(existing_posts)
##
##    def insert_post(self, post, FuukaPosts):
##        db_insert(self, db_ses, FuukaPosts)
##        return
##
##    def insert_new_ghost_posts(self):
##        for
##        return


class Board():
    """A board from Warosu"""
    def __init__(self, base_url, board_name, req_ses, dl_dir):
        # Store arguments
        self.base_url = unicode(base_url)# E.G. u'https://warosu.org'; No trailing slash.
        self.board_name = unicode(board_name)# Board shortname, E.G. u'tg'
        self.req_ses = req_ses# requests Session object
        self.dl_dir = unicode(dl_dir)
        # Initialise variables
        threads = {}
        pass

    def load_thread(self, thread_num):
        logging.debug('Loading thread: {0!r}'.format(thread_num))
        new_thread = Thread(board=self, thread_num=thread_num, req_ses=self.req_ses, load_immediately=True)
        self.threads[thread_num] = new_thread
        return




class Thread():
    """A thread from Warosu"""
    def __init__(self, board, thread_num, req_ses, load_immediately=True):
        # Store arguments
        self.board = self.board
        self.base_url = self.board.base_url# E.G. u'https://warosu.org'; No trailing slash.
        self.board_name = self.board.board_name# Board shortname, E.G. u'tg'
        self.thread_num = int(thread_num)# Thread id number
        self.req_ses = req_ses# requests Session object
        # Initialise variables
        self.posts = {}
        self.url = u'{b_u}/{brd}/thread/'.format(b_u=base_url, brd=board)# ex. u'https://warosu.org/g/thread/68630359'
        self.html = None# Initialise as None; unicode later.
        self.time_grabbed = None# Initialise as None; datetime.datetime later.
        self.html_filepath = os.path.join(dl_dir, '{0}.html'.format(self.thread_num))
        # Load thread and process into posts if requested
        if load_immediately:
            self.load_posts()

    def load_posts(self):
        """Load a thread from warosu"""
        logging.debug('Loading posts for thread: {0!r}'.format(thread_num))
        self._thread_res = common.fetch(requests_session=self.req_ses, url=self.url)
        self.time_grabbed = datetime.datetime.utcnow()# Record when we got the thread
        # TODO: Ensure unicode everywhere
        self.html = self._thread_res.content
        common.write_file(file_path=self.html_filepath, data=html)# TODO: Ensure unicode works with this
        self.posts = self._split_posts(self.html)

    def _split_posts(self, thread_num, html):
        """Split page into post fragments and instantiate child Post objects for them"""
        fragments = w_post_extractors.split_thread_into_posts(html)
        for fragment in fragments:
            new_post = WarosuPost(thread_num=thread_num, html=html, time_grabbed=time_grabbed)
            if new_post.num:
                self.posts[new_post.num] = new_post
            else:
                logging.error('New post did not have "num", did not store it!')
        return

    def insert_posts_dict(self, posts_dict, FuukaPosts):
        """Insert a dict of Post objects into the supplied FuukaPosts table using SQLAlchemy."""
        logging.debug('Attempting to insert all posts from thread {0!r} into the DB'.format(self.thread_num))
        for num in posts_dict.keys():
            logging.debug('Attempting to insert post {0!r}'.format(num))
            post = posts_dict[num]
            post.db_insert(db_ses, FuukaPosts)
        logging.debug('Inserted all posts from thread {0!r} into the DB'.format(self.thread_num))
        return

    def insert_posts_list(self, posts_list, FuukaPosts):
        """Insert a list of Post objects into the supplied FuukaPosts table using SQLAlchemy."""
        logging.debug('Attempting to insert all posts from thread {0!r} into the DB'.format(self.thread_num))
        for post in posts_list:
            logging.debug('Attempting to insert post {0!r}'.format(post.num))
            post.db_insert(db_ses, FuukaPosts)
        logging.debug('Inserted all posts from thread {0!r} into the DB'.format(self.thread_num))
        return

    def lookup_posts(self, db_ses, FuukaPosts, thread_num):
        # Look for all posts for this thread in DB
        logging.debug('About to look for existing posts for this thread')
        existing_posts_q = db_ses.query(FuukaPosts)\
            .filter(FuukaPosts.parent == thread_num,)# TODO Confirm parent is always == thread_num
        existing_post_rows = existing_posts_q.all()
        logging.debug(u'existing_post_rows={0!r}'.format(existing_post_rows))
        logging.debug(u'len(existing_post_rows)={0!r}'.format(len(existing_post_rows)))
        db_post_nums = []
        for existing_post_row in existing_post_rows:
            post_num = existing_post_row.num
            db_post_nums.append(post_num)
        return db_post_nums

    def insert_new_ghost_posts(self, db_ses, FuukaPosts, thread_num):
        # Lookup existing posts for this thread
        db_post_nums = self.lookup_posts(db_ses=db_ses, FuukaPosts=FuukaPosts, thread_num=thread_num)
        # Find new posts
        new_posts = []
        for post_key in self.posts.keys():
            post = self.posts[post_key]
            if (post.num in db_post_nums):
                logging.debug('Post t{0!r}.p{1!r} is not in DB'.format(post.parent, post.num))
                if post.is_ghost:
                    logging.debug('Post t{0!r}.p{1!r} is ghost'.format(post.parent, post.num))
                    logging.debug('Inserting post t{0!r}.p{1!r}'.format(post.parent, post.num))
                    new_posts.append(post)
        logging.debug('Inserting {0!r} new posts'.format(len(new_posts)))
        # Insert new posts for this thread
        self.insert_posts_list(posts_list=new_posts, FuukaPosts=FuukaPosts)
        logging.debug('Inserted {0!r} posts for thread t{1!r}'.format(len(new_posts), thread_num))
        return




class WarosuPost():
    """A post from Warosu"""
    def __init__(self, thread_num, html=None, time_grabbed=None):
        # Store arguments
        self.html = html
        self.time_grabbed = time_grabbed
        # Init future vars as None:
        # Fuuka DB values
        self.thread = None
        self.num = None
        self.subnum = None
        self.parent = None
        self.timestamp = None
        self.preview = None
        self.preview_w = None
        self.preview_h = None
        self.media = None
        self.media_w = None
        self.media_h = None
        self.media_size = None
        self.media_hash = None
        self.media_filename = None
        self.spoiler = None
        self.deleted = None
        self.capcode = None
        self.email = None# Cannot be retrieved
        self.name = None
        self.trip = None
        self.title = None
        self.comment = None
        self.delpass = None# Cannot be retrieved
        self.sticky = None
        # Custom values
        self.is_ghost = None# Is this post a ghost post?
        self.has_image = None# Does this post have an image?
        if self.html:
            self._parse(html)
        return

    def _parse(self, html):
        """Parse a post HTML fragment and set instance values to found values"""
##        # doc_id int unsigned not null auto_increment,# Cannot be retrieved
##        # id decimal(39,0) unsigned not null default '0',# Cannot be retrieved
        # num int unsigned not null,
        self.num, self.subnum = w_post_extractors.num_subnum(fragment)
        # parent int unsigned not null default '0',
        self.parent = self.thread_num
        # timestamp int unsigned not null,
        self.timestamp = w_post_extractors.timestamp(fragment)
        # preview varchar(20),
        # preview_w smallint unsigned not null default '0',
        # preview_h smallint unsigned not null default '0',
        self.preview, self.preview_w, self.preview_h = w_post_extractors.preview_preview_w_preview_h(fragment)
        # media text,
        # media_w smallint unsigned not null default '0',
        # media_h smallint unsigned not null default '0',
        # media_size int unsigned not null default '0',
        self.media, self.media_w, self.media_h, self.media_size = w_post_extractors.media_media_w_media_h_media_size(fragment)
        # media_hash varchar(25),
        self.media_hash = w_post_extractors.media_hash(fragment)
        # media_filename varchar(20),
        self.media_filename = w_post_extractors.media_filename(fragment, board_images_path)
        # spoiler bool not null default '0',
        self.spoiler = w_post_extractors.spoiler(fragment)
        # deleted bool not null default '0',
        self.deleted = w_post_extractors.deleted(fragment)
        # capcode enum('N', 'M', 'A', 'G') not null default 'N',
        self.capcode = w_post_extractors.capcode(fragment)
        # email varchar(100),# Cannot be retrieved
    ##    email = w_post_Extractors.email(fragment)
        self.email = u'EMAIL FINDING NOT IMPLIMENTED!'
        # name varchar(100),
        self.name = w_post_extractors.name(fragment)
        # trip varchar(25),
        self.trip = w_post_extractors.trip(fragment)
        # title varchar(100),
        self.title = w_post_extractors.title(fragment)
        # comment text,
        self.comment = w_post_extractors.comment(fragment)
##        # delpass tinytext,# Cannot be retrieved
        # sticky bool not null default '0',
        self.sticky = w_post_extractors.sticky(fragment)

        # Added-on values
        self.is_ghost = (self.subnum != 0)# Ghost posts have a subnum other than zero
        self.has_image = (self.media_filename != None)# Post has image if media_filename is not NULL. (media_filename is Fuuka's disk location of the image)
        return

    def db_insert(self, db_ses, FuukaPosts):
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
        db_ses.add(new_row)




### Fuuka does not use a seperate images table
##class Image():
##    """An image from Warosu"""
##    def __init__(self):
##        self.thread = None
##        self.num = None





def dev():
    """Development test area"""
    logging.warning(u'running dev()')

    # Startup DB stuff
    # Load config file
    config_path = os.path.join(u'config', 'w_classes.yaml')
    config = YAMLConfigWClasses(config_path)
    # Set values from config file
    board_name = unicode(config.board_name)
    db_filepath = unicode(config.db_filepath)
    connection_string = unicode(config.connection_string)
    dl_dir = unicode(config.dl_dir)
    echo_sql = config.echo_sql

    FuukaPosts = tables_fuuka.fuuka_posts(Base, board_name)# Creates table class using factory function

    # Setup requests session
    req_ses = requests.Session()

    # Test grabbing a thread
    board = Board(
        base_url = u'https://warosu.org',
        board_name = u'tg',
        req_ses = req_ses
    )
    thread = board.load_thread(68630359)
    thread.insert_new_ghost_posts()
    logging.warning(u'exiting dev()')



def main():
    dev()
    return



if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "w_classes.log.txt"), console_level=logging.DEBUG)# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical("Unhandled exception!")
        logging.exception(e)
    logging.info("Program finished.")

