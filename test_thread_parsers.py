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
import thread_parsers





##class TestTitle(unittest.TestCase):# TODO
##    def test_empty_string(self):
##        test_value = u''
##        expected_result = u''
##        result = thread_parsers.title(test_value)
##        self.assertEqual(result, expected_result)



class TestWholeThread_40312936(unittest.TestCase):# TODO
    """Ghost post example: https://warosu.org/tg/thread/40312936"""
    def setUp(self):
        self.thread_num=40312936
        self.thread_filepath = os.path.join('example_threads', 'warosu.tg.40312936.html')
        self.thread_url=u'https://warosu.org/tg/thread/40312936'

        with open(self.thread_filepath, 'r') as f:
            file_data = f.read()
        self.thread_html = file_data.decode('utf8')
        self.post_fragments = thread_parsers.split_thread_into_posts(html=self.thread_html)
        return

    def test_ghost_post_40319937_1(self):
        fragment = self.post_fragments[22]
        num, subnum = thread_parsers.num_subnum(fragment)
        self.assertEqual(num, 40319937)
        self.assertEqual(subnum, 1)





def main():
    unittest.main()

if __name__ == '__main__':
    main()
