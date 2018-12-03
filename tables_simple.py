#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     25-11-2018
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


# ===== Simple =====
# Few fields

def simple_boards(Base):# simple threads table
    """A DB schema with few columns.
    Make a simple, fast-to-code threads table for warosu.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug(u'table_factory_simple_boards() args={0!r}'.format(locals()))# Record arguments.
    table_name = u'simpleboards'
    logging.debug(u'Naming the images table {0!r}'.format(table_name))
    class SimpleBoards(Base):
        __tablename__ = table_name
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        board_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
        shortname = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
    return SimpleBoards



def simple_threads(Base, board_name):# simple threads table
    """A DB schema with few columns.
    Make a simple, fast-to-code threads table for warosu.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug(u'table_factory_simple_threads() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [unicode])
    table_name = u'{0}_simplethreads'.format(board_name)
    logging.debug(u'Naming the SimpleThreads table {0!r}'.format(table_name))
    class SimpleThreads(Base):
        __tablename__ = table_name
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        thread_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
    return SimpleThreads



def simple_posts(Base, board_name):# simple threads table
    """A DB schema with few columns.
    Make a simple, fast-to-code posts table for warosu.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug(u'table_factory_simple_posts() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [unicode])
    table_name = u'{0}_simpleposts'.format(board_name)
    logging.debug(u'Naming the SimplePosts table {0!r}'.format(table_name))
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
