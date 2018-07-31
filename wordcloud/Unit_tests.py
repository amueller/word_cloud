import unittest, random, sys
import numpy as np
import array
import copy
import pyximport
pyximport.install()
from query_integral_image import test_c_search_for_space


class baseBlankCanvasSearchTester(unittest.TestCase):
    """
    abstract base class for other test cases
    """
    def setUp(self):
        self.integral_image = np.zeros((100, 100), dtype=np.uint32)
        
    def assert_hits_equal_expected(self):
        """
        generic test format to be run by runTest in each subclass
        """
        hits = test_c_search_for_space(self.integral_image, self.test_word_x, self.test_word_y)
        self.assertEqual(hits, self.expected_hits)

class SmallWordTester10_by_10(baseBlankCanvasSearchTester):
    def runTest(self):
        self.test_word_x= 10
        self.test_word_y = 10
        self.expected_hits = self.calculate_expected_hits(self.integral_image, (self.test_word_x, self.test_word_y))
        self.assert_hits_equal_expected()

    def calculate_expected_hits(self, canvas, word):
        usable_height = canvas.shape[1] - word[1]
        usable_width = canvas.shape[0] - word[0]
        expected_hits = usable_height * usable_width
        return expected_hits
    

class OversizedWordTester(baseBlankCanvasSearchTester):
    def runTest(self):
        self.length = max(self.integral_image.shape)*2
        self.test_word_x = self.length
        self.test_word_y = self.length
        self.expected_hits = 0
        self.assert_hits_equal_expected()


class OneHitTester(baseBlankCanvasSearchTester):
    "tests that the hittester can appropriately detect a word that fits exactly"
    def runTest(self):
        self.test_word_x = self.integral_image.shape[0] -1
        self.test_word_y = self.integral_image.shape[1]-1
        self.expected_hits = 1
        self.assert_hits_equal_expected()

