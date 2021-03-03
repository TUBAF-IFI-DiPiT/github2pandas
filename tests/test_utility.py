#!/usr/bin/python
 
import unittest
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Test_Settings(unittest.TestCase):

    def test_github_token_availability(self):
        self.assertTrue( "TOKEN" in os.environ , "No Token available")

if "__main__" == __name__:
    unittest.main()