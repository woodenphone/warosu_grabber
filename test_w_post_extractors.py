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
import os
import logging
import logging.handlers
import unittest
# Remote libraries
import bs4
# local
import w_post_extractors
import w_thread_Full













class TestTitle(unittest.TestCase):# TODO
    def test_empty_string(self):
        test_value = u''
        expected_result = u''
        result = w_post_extractors.title(test_value)
        self.assertEqual(result, expected_result)



class TestWholeThread_40312936(unittest.TestCase):# TODO
    """Ghost post example: https://warosu.org/tg/thread/40312936"""
    def __init__(self):
        self.thread_num = 40312936
        self.thread_url = u'https://warosu.org/tg/thread/40312936'
        self.thread_filepath = os.path.join('example_threads', 'warosu.tg.40312936.html')
        self.board_images_path = ''
        return
    def setup(self):
        with open(self.thread_filepath, 'r') as f:
            self.file_data = f.read()
        self.thread_html = self.file_data.decode('utf8')
        self.post_fragments = w_thread_full.split_thread_into_posts(html=self.thread_html)
        return
    def test_post0(self):
        expected_result = {
            u'': u'',
        }
        result = w_thread_full.fuuka_post(
            fragment=self.post_fragments[0],
            thread_num=self.thread_num,
            thread_url=self.thread_url,
            board_images_path=self.board_images_path,
        )





def main():
    pass

if __name__ == '__main__':
    main()
