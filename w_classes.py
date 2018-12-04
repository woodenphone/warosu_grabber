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
import yaml
# local
import common
import thread_parsers# Post parsing functions
import tables_fuuka# Table class factories for Fuuka-style DB




Base = declarative_base()# Setup system to keep track of tables and classes




class YAMLConfigWClasses():
    """Handle reading, writing, and creating YAML config files."""
    def __init__(self, config_path=None):
        # Set default values
        self.board_name = 'tg'# Shortname of board
        self.db_filepath = 'temp/tg.db'# Path to SQLite DBif appropriate
        self.connection_string = 'sqlite:///temp/tg.db'# SQLAlchemy connection string
        self.dl_dir = 'temp/dl/tg/'# Where to download to
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
        if config is None:
            logging.error('Could not load config from {0!r}'.format(config_path))
            return
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



class Board():
    """A board from Warosu"""
    def __init__(self, base_url, board_name, req_ses, dl_dir, board_images_path):
        # Store arguments
        self.base_url = unicode(base_url)# E.G. u'https://warosu.org'; No trailing slash.
        self.board_name = unicode(board_name)# Board shortname, E.G. u'tg'
        self.req_ses = req_ses# requests Session object
        self.dl_dir = unicode(dl_dir)# Dir to put files into
        self.board_images_path = board_images_path# Used for finding images. E.G. u'data/tg'
        # Initialise variables
        self.threads = {}
        pass

    def load_thread(self, thread_num):
        logging.debug('Loading thread: {0!r}'.format(thread_num))
        new_thread = Thread(
            base_url=self.base_url,
            board_name=self.board_name,
            thread_num=thread_num,
            req_ses=self.req_ses,
            dl_dir=self.dl_dir,
            load_immediately=True,
            board_images_path=self.board_images_path
        )
        self.threads[thread_num] = new_thread
        return new_thread




class Thread():
    """A thread from Warosu"""
    def __init__(self, base_url, board_name, thread_num,
        req_ses, dl_dir, board_images_path, load_immediately=True, ):
        # Store arguments
        self.base_url = base_url# E.G. u'https://warosu.org'; No trailing slash.
        self.board_name = board_name# Board shortname, E.G. u'tg'
        self.thread_num = int(thread_num)# Thread id number
        self.req_ses = req_ses# requests Session object
        self.dl_dir = dl_dir
        self.board_images_path = board_images_path
        # Initialise variables
        self.posts = {}
        self.url = u'{b_u}/{brd}/thread/{t_num}'.format(
            b_u=self.base_url,
            brd=self.board_name,
            t_num=self.thread_num)# ex. u'https://warosu.org/g/thread/68630359'
        self.html = None# Initialise as None; unicode later.
        self.time_grabbed = None# Initialise as None; datetime.datetime later.
        self.html_filepath = os.path.join(self.dl_dir, u'{0}.html'.format(self.thread_num))
        # Load thread and process into posts if requested
        if load_immediately:
            self.load_posts_to_self()
        return

    def load_posts_to_self(self):
        """Load a thread from warosu"""
        logging.debug(u'Loading posts for thread: {0!r}'.format(self.thread_num))
        # Load page
        thread_res = common.fetch(requests_session=self.req_ses, url=self.url)
        self.time_grabbed = datetime.datetime.utcnow()# Record when we got the thread
        # Decode page into unicode object
        # TODO: Ensure unicode everywhere
        logging.debug(u'type(thread_res.content)={0!r}'.format(type(thread_res.content)))
        self.html = thread_res.content.decode(u'utf8')
        logging.debug(u'type(html)={0!r}'.format(type(self.html)))
        # Store page
        common.write_unicode_file(file_path=self.html_filepath, data=self.html)# TODO: Ensure unicode works with this
        # Parse page
        self._split_posts(
            thread_num=self.thread_num,
            html=self.html,
            time_grabbed=self.time_grabbed,
            board_images_path=self.board_images_path
        )
        return

    def _split_posts(self, thread_num, html, time_grabbed, board_images_path):
        """Split page into post fragments and instantiate child Post objects for them"""
        # Split poage into posts
        fragments = thread_parsers.split_thread_into_posts(html)
        for fragment in fragments:
            # Parse post
            new_post = WarosuPost(thread_num=thread_num, board_images_path=board_images_path, html=fragment, time_grabbed=time_grabbed)
            if new_post.num:
                self.posts[new_post.num] = new_post
            else:
                logging.error(u'New post did not have "num", did not store it!')
        return

    def insert_posts_dict(self, posts_dict, db_ses, FuukaPosts):
        """Insert a dict of Post objects into the supplied FuukaPosts table using SQLAlchemy."""
        logging.debug(u'Attempting to insert all posts from thread {0!r} into the DB'.format(self.thread_num))
        for num in posts_dict.keys():
            logging.debug('Attempting to insert post {0!r}'.format(num))
            post = posts_dict[num]
            post.db_insert(db_ses, FuukaPosts)
        logging.debug('Inserted all posts from thread {0!r} into the DB'.format(self.thread_num))
        return

    def insert_posts_list(self, posts_list, db_ses, FuukaPosts):
        """Insert a list of Post objects into the supplied FuukaPosts table using SQLAlchemy."""
        logging.debug('Attempting to insert all posts from thread {0!r} into the DB'.format(self.thread_num))
        for post in posts_list:
            logging.debug('Attempting to insert post {0!r}'.format(post.num))
            post.db_insert(db_ses, FuukaPosts)
        logging.debug('Inserted all posts from thread {0!r} into the DB'.format(self.thread_num))
        return

    def lookup_posts(self, db_ses, FuukaPosts, thread_num):
        """Find all posts for this thread in the DB"""
        # Look for all posts for this thread in DB
        logging.debug('About to look for existing posts for this thread')
        existing_posts_q = db_ses.query(FuukaPosts)\
            .filter(FuukaPosts.parent == thread_num,)# TODO Confirm parent is always == thread_num
        existing_post_rows = existing_posts_q.all()
        logging.debug(u'existing_post_rows={0!r}'.format(existing_post_rows))
        logging.debug(u'len(existing_post_rows)={0!r}'.format(len(existing_post_rows)))
        # Keep only post nums
        db_post_nums = []
        for existing_post_row in existing_post_rows:
            post_num = existing_post_row.num
            db_post_nums.append(post_num)
        return db_post_nums

    def insert_new_ghost_posts(self, db_ses, FuukaPosts):
        """Check for existing posts for a thread, then insert any new ghost posts into the DB"""
        # Lookup existing posts for this thread
        db_post_nums = self.lookup_posts(
            db_ses=db_ses,
            FuukaPosts=FuukaPosts,
            thread_num=self.thread_num
        )
        # Find new posts
        new_posts = []
        logging.debug(u'self.posts={0!r}'.format(self.posts))
        for post_key in self.posts.keys():
            post = self.posts[post_key]
            if (post.num not in db_post_nums):
                logging.debug('Post t{0!r}.p{1!r} is not in DB'.format(post.parent, post.num))
                if post.is_ghost:
                    logging.debug('Inserting ghost post t{0!r}.p{1!r}'.format(post.parent, post.num))
                    new_posts.append(post)#TODO: FIXME: DOES NOT GET ALL GHOST POSTS!
        logging.debug('Inserting {0!r} new posts'.format(len(new_posts)))
        # Insert new posts for this thread
        self.insert_posts_list(posts_list=new_posts, db_ses=db_ses, FuukaPosts=FuukaPosts)
        logging.debug('Inserted {0!r} posts for thread t{1!r}'.format(len(new_posts), self.thread_num))
        return




class WarosuPost():
    """A post from Warosu"""
    def __init__(self, board_images_path, thread_num, html=None, time_grabbed=None):
        # Store arguments
        self.board_images_path = board_images_path
        self.thread_num = thread_num
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
        # Parse post HTML into thread vars if given
        if self.html:
            self.parse_to_self(
                html=self.html,
                board_images_path=self.board_images_path
            )
        return

    def parse_to_self(self, html, board_images_path):
        """Parse a post HTML fragment and set instance values to found values"""
##        # doc_id int unsigned not null auto_increment,# Cannot be retrieved
##        # id decimal(39,0) unsigned not null default '0',# Cannot be retrieved
        # num int unsigned not null,
        self.num, self.subnum = thread_parsers.num_subnum(html)
        # parent int unsigned not null default '0',
        self.parent = self.thread_num
        # timestamp int unsigned not null,
        self.timestamp = thread_parsers.timestamp(html)
        # preview varchar(20),
        # preview_w smallint unsigned not null default '0',
        # preview_h smallint unsigned not null default '0',
        self.preview, self.preview_w, self.preview_h = thread_parsers.preview_preview_w_preview_h(html)
        # media text,
        # media_w smallint unsigned not null default '0',
        # media_h smallint unsigned not null default '0',
        # media_size int unsigned not null default '0',
        self.media, self.media_w, self.media_h, self.media_size = thread_parsers.media_media_w_media_h_media_size(html)
        # media_hash varchar(25),
        self.media_hash = thread_parsers.media_hash(html)
        # media_filename varchar(20),
        self.media_filename = thread_parsers.media_filename(html, board_images_path)
        # spoiler bool not null default '0',
        self.spoiler = thread_parsers.spoiler(html)
        # deleted bool not null default '0',
        self.deleted = thread_parsers.deleted(html)
        # capcode enum('N', 'M', 'A', 'G') not null default 'N',
        self.capcode = thread_parsers.capcode(html)
        # email varchar(100),# Cannot be retrieved
    ##    email = thread_parsers.email(html)
        self.email = u'EMAIL FINDING NOT IMPLIMENTED!'
        # name varchar(100),
        self.name = thread_parsers.name(html)
        # trip varchar(25),
        self.trip = thread_parsers.trip(html)
        # title varchar(100),
        self.title = thread_parsers.title(html)
        # comment text,
        self.comment = thread_parsers.comment(html)
##        # delpass tinytext,# Cannot be retrieved
        # sticky bool not null default '0',
        self.sticky = thread_parsers.sticky(html)
        # Added-on values
        logging.debug(u'self.subnum={0!r}'.format(self.subnum))
        self.is_ghost = (self.subnum != 0)# Ghost posts have a subnum other than zero
        self.has_image = (self.media_filename != None)# Post has image if media_filename is not NULL. (media_filename is Fuuka's disk location of the image)
        return

    def db_insert(self, db_ses, FuukaPosts):
        new_row = FuukaPosts(
            num = self.num,
            subnum = self.subnum,
            parent = self.parent,
            timestamp = self.timestamp,
            preview = self.preview,
            preview_w = self.preview_w,
            preview_h = self.preview_h,
            media = self.media,
            media_w = self.media_w,
            media_h = self.media_h,
            media_size = self.media_size,
            media_hash = self.media_hash,
            media_filename = self.media_filename,
            spoiler = self.spoiler,
            deleted = self.deleted,
            capcode = self.capcode,
            email = self.email,
            name = self.name,
            trip = self.trip,
            title = self.title,
            comment = self.comment,
            delpass=None,# Can't be grabbed, server-side only value
            sticky = self.sticky,
            )
        db_ses.add(new_row)
        return



def dev():
    """Development test area"""
    logging.warning(u'running dev()')
    # Load config file
    config_path = os.path.join(u'config', 'w_classes.yaml')
    config = YAMLConfigWClasses(config_path)
    # Set values from config file
    board_name = unicode(config.board_name)
    db_filepath = unicode(config.db_filepath)
    connection_string = unicode(config.connection_string)
    dl_dir = unicode(config.dl_dir)
    echo_sql = config.echo_sql

    # Startup DB stuff
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
    Base.metadata.create_all(checkfirst=True)# Create tables based on classes. checkfirst
    # Create a session to interact with the DB
    SessionClass = sqlalchemy.orm.sessionmaker(bind=engine)
    db_ses = SessionClass()

    # Generate table classes
    FuukaPosts = tables_fuuka.fuuka_posts(Base, board_name)# Creates table class using factory function
    # Ensure tables exist
    Base.metadata.create_all(engine, checkfirst=True)

    # Setup requests session
    req_ses = requests.Session()

    # Test grabbing a thread
    # https://warosu.org/tg/thread/40312936
    board = Board(
        base_url = u'https://warosu.org',
        board_name = u'tg',
        req_ses = req_ses,
        dl_dir = dl_dir,
        board_images_path = u'data/tg',
    )
    thread = board.load_thread(40312936)
    thread.insert_new_ghost_posts(db_ses, FuukaPosts)

    # Persist data now that thread has been grabbed
    logging.info(u'Committing')
    db_ses.commit()

    # Gracefully disconnect from DB
    logging.info(u'Ending DB session')
    db_ses.close()# Release connection back to pool.
    engine.dispose()# Close all connections.

    logging.warning(u'exiting dev()')
    return


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

