#!/usr/bin/python
 
import unittest
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utility import get_repo

class TestUtility(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    def test_get_repo(self):
        """
        Test generating pandas table
        """
        repo = get_repo(repo_name=self.git_repo_name, token=self.github_token)
        self.assertIsNotNone(repo)


if __name__ == "__main__":
    unittest.main()
