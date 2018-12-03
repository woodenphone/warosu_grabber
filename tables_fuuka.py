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



# ===== Fuuka-style =====
def fuuka_posts(Base, board_name):
    table_name = u'{0}'.format(board_name)
    logging.debug(u'Naming the FuukaPosts table {0!r}'.format(table_name))
    class FuukaPosts(Base):
        __tablename__ = table_name
        # Fuuka columns:
##        # doc_id int unsigned not null auto_increment,# Cannot retrieve
##        # id decimal(39,0) unsigned not null default '0',# Cannot retrieve
        num = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)# num int unsigned not null,
        subnum = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)# subnum int unsigned not null,
        parent = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)# parent int unsigned not null default '0',
        timestamp = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)# timestamp int unsigned not null,
        preview = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# preview varchar(20),
        preview_w = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)# preview_w smallint unsigned not null default '0',
        preview_h = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)# preview_h smallint unsigned not null default '0',
        media = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# media text,
        media_w = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)# media_w smallint unsigned not null default '0',
        media_h = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)# media_h smallint unsigned not null default '0',
        media_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)# media_size int unsigned not null default '0',
        media_hash = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# media_hash varchar(25),
        media_filename = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# media_filename varchar(20),
        spoiler = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)# spoiler bool not null default '0',
        deleted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)# deleted bool not null default '0',
        capcode = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False, default=u'N')# capcode enum('N', 'M', 'A', 'G') not null default 'N',
        email = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# email varchar(100),
        name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# name varchar(100),
        trip = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# trip varchar(25),
        title = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# title varchar(100),
        comment = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# comment text,
        delpass = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# delpass tinytext,# Cannot retrieve
        sticky = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)# sticky bool not null default '0'
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
    return FuukaPosts



def main():
    pass

if __name__ == '__main__':
    main()
