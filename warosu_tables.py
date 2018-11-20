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
import logging
import logging.handlers
import datetime
# Remote libraries
import sqlalchemy# For talking to DBs
from sqlalchemy.ext.declarative import declarative_base
# local


##def table_factory_threads(Base, board_name):# Threads table
##    """We're Java now!
##    Make the 'x_threads' table for a 4chan board.
##    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
##    TODO: Sane database design"""
##    logging.debug(u'table_factory_threads() args={0!r}'.format(locals()))# Record arguments.
##    assert(type(board_name) in [unicode])
##    table_name = u'{0}_threads'.format(board_name)
##    logging.debug(u'Naming the thread table {0!r}'.format(table_name))
##    class Threads(Base):
##        __tablename__ = table_name
##        # from asagi boards.sql
##        thread_num = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
##        time_op = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        time_last = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        time_bump = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        time_ghost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
##        time_ghost_bump = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
##        time_last_modified = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        nreplies = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        nimages = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        sticky = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
##        locked = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
##        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
##        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
##        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
##    return Threads
##
##
##
##def table_factory_posts(Base, board_name):# Posts table
##    """We're Java now!
##    Make the 'x_threads' table for an 4chan board.
##    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
##    TODO: Sane database design"""
##    logging.debug(u'table_factory_posts() args={0!r}'.format(locals()))# Record arguments.
##    assert(type(board_name) in [unicode])
##    table_name = u'{0}'.format(board_name)
##    logging.debug(u'Naming the post table {0!r}'.format(table_name))
##    class Posts(Base):
##        __tablename__ = table_name
##        # from asagi boards.sql
##        doc_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
##        media_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        poster_ip
##        num = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        subnum = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        thread_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
##        op = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
##        timestamp = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        timestamp_expired = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        preview_orig = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        preview_w = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        preview_h = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        media_filename = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        media_w = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        media_h = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        media_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        media_hash = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        media_orig = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        spoiler = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=0)
##        deleted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=0)
##        capcode = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False, default=u'N')
##        email = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        trip = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        title = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        comment = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        delpass = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        sticky = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=0)
##        locked = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=0)
##        poster_hash = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        poster_country = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        exif = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
##        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
##        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
##    return Posts
##
##
##
##def table_factory_images(Base, board_name):# images table
##    """We're Java now!
##    Make the 'x_files' table for an 8chan board.
##    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
##    TODO: Sane database design"""
##    logging.debug(u'table_factory_images() args={0!r}'.format(locals()))# Record arguments.
##    assert(type(board_name) in [unicode])
##    table_name = u'{0}_images'.format(board_name)
##    logging.debug(u'Naming the images table {0!r}'.format(table_name))
##    class Image(Base):
##        __tablename__ = table_name
##        media_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
##        media_hash = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
##        media = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        preview_op = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        preview_reply = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        total = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
##        banned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
##
##        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
##        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
##        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
##    return Image







##def table_factory_simple_boards(Base):# simple threads table
##    """We're Java now!
##    Make a simple, fast-to-code threads table for warosu.
##    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
##    TODO: Sane database design"""
##    logging.debug(u'table_factory_simple_boards() args={0!r}'.format(locals()))# Record arguments.
##    table_name = u'simpleboards'
##    logging.debug(u'Naming the images table {0!r}'.format(table_name))
##    class SimpleBoards(Base):
##        __tablename__ = table_name
##        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
##        board_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
##        shortname = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
##        title = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        description = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
##        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
##        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
##        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
##    return SimpleBoards
##
##
##
##def table_factory_simple_threads(Base, board_name):# simple threads table
##    """We're Java now!
##    Make a simple, fast-to-code threads table for warosu.
##    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
##    TODO: Sane database design"""
##    logging.debug(u'table_factory_simple_threads() args={0!r}'.format(locals()))# Record arguments.
##    assert(type(board_name) in [unicode])
##    table_name = u'{0}_simplethreads'.format(board_name)
##    logging.debug(u'Naming the images table {0!r}'.format(table_name))
##    class SimpleThreads(Base):
##        __tablename__ = table_name
##        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
##        thread_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
##        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
##        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
##        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
##    return SimpleThreads



def table_factory_simple_posts(Base, board_name):# simple threads table
    """We're Java now!
    Make a simple, fast-to-code posts table for warosu.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug(u'table_factory_simple_posts() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [unicode])
    table_name = u'{0}_simpleposts'.format(board_name)
    logging.debug(u'Naming the images table {0!r}'.format(table_name))
    class SimplePosts(Base):
        __tablename__ = table_name
        num = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
        subnum = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
        thread_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        post_html = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
    return SimplePosts


def main():
    pass

if __name__ == '__main__':
    main()
