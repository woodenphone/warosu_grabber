#-------------------------------------------------------------------------------
# Name:        w_post_extractors
# Purpose:  Extract values from a post's HTML snippet
#
# Author:      User
#
# Created:     24-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import logging
import logging.handlers
import re
import unittest
# Remote libraries
import bs4
# local






def convert_filesize_string(fs_string):
    """Inverse of:
    sub size_string($){
        my($val)=@_;

        return sprintf "%d B",$val if $val<1024;
        return sprintf "%d KB",$val if ($val/=1024)<1024;
        return sprintf "%.2f MB",$val if ($val/=1024)<1024;
        return sprintf "%.2f GB",$val if ($val/=1024)<1024;

        "very large"
    }
    """
    val, mult = fs_string.split(' ')
    if (mult == 'B'):
        return int(val)
    elif (mult == 'KB'):
        return int(val) * 1024
    elif (mult == 'MB'):
        return int(val) * 1024*1024
    elif (mult == 'GB'):
        return int(val) * 1024*1024*1024
    elif (mult == 'large'):
        return None# NULL
    # Unexpected value
    logging.error('Unexpected filesize value!  fs_string={0!r}'.format(fs_string))
    raise ValueError()


# ===== Fuuka-style =====
def timestamp(fragment):
    """"Find timestamp.
    timestamp: unix time post was made.
    """
    # timestamp int unsigned not null,
    # Find timestamp string
    # <span class="posttime" title="<var deyotsutime($date) * 1000>"><var scalar gmtime($date)></span></label>
    # '<span class="posttime" title="1474172041000">Sun Sep 18 12:14:01 2016</span></label>'
    timestamp_search = re.search(u'<span class="posttime" title="(\d+)">', fragment)
    timestamp_string = timestamp_search.group(1)
    # Convert timestamp string to correct unixtime
    timestamp = int(timestamp_string)# TODO Ensure we're not off by a factor of a thousand or so (check actual DB values)
    return timestamp


def num_subnum(fragment):
    """"Find num, subnum
    num:post number
    subnum: ghost post number, 0 for regular posts
    """
    # num int unsigned not null,
    # subnum int unsigned not null,
    num_search_regex = (
    u'<input '
    u'(?:name="delete"|type="checkbox"| )+'# These can be in either order, and are seperated by spaces
    u'value="(\d+),(\d+)')
    num_search = re.search(num_search_regex, fragment)
    num_string = num_search.group(1)
    subnum_string = num_search.group(2)
    num = int(num_string)
    subnum = int(subnum_string)
    return (num, subnum)


def preview_preview_w_preview_h(fragment):
    """"Find preview, preview_w, preview_h
    preview: thumbnail filename on server
    preview_w: thumbnail width
    preview_h: thumbnail height
    """
    # preview varchar(20),
    # preview_w smallint unsigned not null default '0',
    # preview_h smallint unsigned not null default '0',
    # Image preview values
    # <if $file><img class="thumb" src="<var $file>" alt="<var $num>" <if $preview_w>width="<var $preview_w>" height="<var $preview_h>"</if> /></if>
    # ...
    # <if not $file><img src="<const MEDIA_LOCATION_HTTP>/error.png" alt="ERROR" class="nothumb" title="No thumbnail" /></if>
    preview_search = re.search('<img class="thumb" src="([^"]+)" alt="([^"]+)" (?:width="([^"]+)" height="([^"]+)")?', fragment)
    if preview_search:
        logging.debug('Found thumbnail')
        preview = preview_search.group(1)
        #thumb_alt = preview_search.group(2)# num
        if preview_search.group(3):
            logging.debug('Found thumbnail dimensions')
            preview_w = preview_search.group(3)
            preview_h = preview_search.group(4)
        else:
            preview_w = None# NULL
            preview_h = None# NULL
    else:
        preview = None# NULL
##        thumb_alt = None# NULL
        preview_w = None# NULL
        preview_h = None# NULL
    return (preview, preview_w, preview_h)


def media_media_w_media_h_media_size(fragment):
    """"Find media, media_w, media_h, media_size
    media: original media filename.
    media_w: width of full media.
    media_h: horiz of full media.
    media_size: size of media file (will be an estimate).
    """
    # media text,
    # media_w smallint unsigned not null default '0',
    # media_h smallint unsigned not null default '0',
    # media_size int unsigned not null default '0',
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
        u'\n')
##    logging.debug(u'file_regex_1={0!r}'.format(file_regex_1))
    f_search_1 = re.search(file_regex_1, fragment)
    if f_search_1:
        # File present
        filesize_string = f_search_1.group(1)# media_size (lowered resolution?)TODO Investigate accuracy of given values
        media_w = f_search_1.group(2)# media_w
        media_h = f_search_1.group(3)# media_h
        media = f_search_1.group(4)# Original filename
    else:
        # No file
        filesize_string = None# NULL# media_size (lowered resolution?)TODO Investigate accuracy of given values
        media_w = None# NULL# media_w
        media_h = None# NULL# media_h
        media = None# NULL# Original filename
    if filesize_string:
        media_size = convert_filesize_string(filesize_string)
    else:
        media_size = None# NULL
    return (media, media_w, media_h, media_size)


def media_hash(fragment):
    """Find media_hash
    (MD5 hash of full media, encoded into base64)"""
    # media_hash varchar(25),
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
        media_hash = None# NULL
    return media_hash


def media_filename(fragment, board_images_path):
    """Find media_filename
    media_filename: server's disk filename of full image."""
    # media_filename varchar(20),
    # <elsif $media_filename><a rel="noreferrer" href="<var "$images_link/$media_filename">">
    # </if>
    media_filename_regex = (
        u'<a rel="noreferrer" href="<var "'
        +board_images_path+
        u'/([^"]+)">">')
    media_filename_search = re.search(media_filename_regex, fragment)
    if media_filename_search:
        media_filename = media_filename_search.group(1)
    else:
        media_filename = None# NULL
    return media_filename


def spoiler(fragment):
    """Determine if spoiler true/false.
    spoiler: Was post spoilered on 4chan."""
    # <if $spoiler><img class="inline" src="<const MEDIA_LOCATION_HTTP>/spoilers.png" alt="[SPOILER]" title="Picture in this post is marked as spoiler" />&nbsp;</if>
    spoiler_indicator = u'/spoilers.png" alt="[SPOILER]" title="Picture in this post is marked as spoiler" />&nbsp;'
    logging.debug(u'spoiler() type(spoiler_indicator)={0!r}'.format(type(spoiler_indicator)))
    logging.debug(u'spoiler() spoiler_indicator={0!r}'.format(spoiler_indicator))
    logging.debug(u'spoiler() type(fragment)={0!r}'.format(type(fragment)))
    logging.debug(u'spoiler() fragment={0!r}'.format(fragment))
    spoiler = (spoiler_indicator in fragment)
    return spoiler


def deleted(fragment):
    """Determine if deleted true/false
    deleted: Was post prematurely deleted from 4chan."""
    # deleted bool not null default '0',
    # <if $deleted><img class="inline" src="<const MEDIA_LOCATION_HTTP>/deleted.png" alt="[DELETED]" title="This post was deleted before its lifetime has expired" />&nbsp;</if>
    deleted = (u'/deleted.png" alt="[DELETED]" title="This post was deleted before its lifetime has expired" />' in fragment)
    return deleted


def sticky(fragment):
    """Determine if stick true/false.
    sticky: Was post a sticky on 4chan."""
    # sticky bool not null default '0',
    # <if $sticky><img class="inline" src="<const MEDIA_LOCATION_HTTP>/sticky.png" alt="[STICKY]" title="This post was stickied on 4chan." />&nbsp;</if>
    sticky = (u'sticky.png" alt="[STICKY]" title="This post was stickied on 4chan." />&nbsp;' in fragment)
    return sticky


def capcode(fragment):
    """Find capcode.
    capcode: capcode of poster."""
    # capcode enum('N', 'M', 'A', 'G') not null default 'N',
    if (u'<span class="trip">## God</span>' in fragment):
        return u'G'# God capcode
    elif (u'<span class="postername mod"> ##Mod</span><' in fragment):
        return u'M'# Mod capcode
    elif (u'<span class="postername admin"> ##Admin</span>' in fragment):
        return u'A'# Admin capcode
    elif (u'<span class="postername dev"> ##Developer</span>' in fragment):
        return u'D'# Developer capcode
    else:
        return u'N'# No capcode
    logging.error('Unexpected value')
    raise ValueError()# Unexpected value


def name(fragment):
    """Find name.
    name: name of poster."""
    # name varchar(100),
    # <span itemprop="name">jubels</span>
    name_search = re.search(u'<span itemprop="name">([^<]+)</span>', fragment)
    name = name_search.group(1)
    return name


def trip(fragment):
    """Find trip.
    trip: tripcode of poster."""
    # trip varchar(25),
    # <span class="postertrip<if $capcode eq 'M'> mod</if><if $capcode eq 'A'> admin</if><if $capcode eq 'D'> dev</if>">&nbsp;<var $trip></span><if $email></a></if></if>
    # TODO: Handle capcode presence
    trip_search = re.search(u'<span class="postertrip">&nbsp;([a-zA-Z0-9!/]+)</span>', fragment)
    if trip_search:
        trip = trip_search.group(1)
    else:
        trip = None# NULL
    return trip


def comment(fragment):
    """Find comment.
    comment: Post text"""
    soup = bs4.BeautifulSoup(fragment, u'html.parser')# TODO Maybe find more efficient way to grab this value than bs4?
    comment_element = soup.find(name=u'p', attrs={u'itemprop':'text',})
    comment = str(comment_element)
    return comment


def title(fragment):
    """Find title.
    title: file title"""
    # title varchar(100),
    # <if $title><span class="filetitle"><var $title></span>&nbsp;</if>
    title_search = re.search('<span class="filetitle">([^<]+)</span>&nbsp;', fragment)
    if title_search:
        title = title_search.group(1)
        return title
    else:
        return None# NULL





def main():
    pass

if __name__ == '__main__':
    main()
