#!/usr/bin/python
 
import unittest
import sys
import os
from pathlib import Path
from github2pandas.utility import Utility

class TestUtility(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    def test_get_repo(self):
        """
        Evaluate accessibility of repository 
        """
        repo = Utility.get_repo(self.git_repo_owner, repo_name=self.git_repo_name, token=self.github_token)
        self.assertIsNotNone(repo)

    def test_github_token_availability(self):
        self.assertTrue( "TOKEN" in os.environ , "No Token available")


if __name__ == "__main__":
    unittest.main()
