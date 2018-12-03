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


# ===== Really Simple =====
# Absolute minimum number of fields

def really_simple_threads(Base, board_name):# simple threads table
    """A DB schema with the absolute minimum number of columns.
    Make a simple, fast-to-code threads table for warosu.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug(u'table_factory_really_simple_threads() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [unicode])
    table_name = u'{0}_reallysimplethreads'.format(board_name)
    logging.debug(u'Naming the ReallySimpleThreads table {0!r}'.format(table_name))
    class ReallySimpleThreads(Base):
        __tablename__ = table_name
        # There can only be one thread per ID.
        # ThreadID will always be integer  where (n >= 0)
        # ThreadID will always be unique
##        thread_num = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        thread_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        is_new = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=True)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
    return ReallySimpleThreads



def main():
    pass

if __name__ == '__main__':
    main()
