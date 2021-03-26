#!/usr/bin/python
 
import unittest
import sys
import os
from pathlib import Path
import warnings

from github2pandas.utility import Utility
from github2pandas.pull_requests import PullRequests

class TestPullRequests(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)

    def test_pull_requests_aggregation(self):
        """
        Test pull requests aggregation
        """
        warnings.simplefilter ("ignore", ResourceWarning)
        repo = Utility.get_repo(self.git_repo_owner, self.git_repo_name, self.github_token)
        result = PullRequests.generate_pull_request_pandas_tables(repo, self.default_data_folder)
        pull_requests = PullRequests.get_pull_requests(self.default_data_folder)
        self.assertFalse( pull_requests.empty , "pull requests have no data")

if __name__ == "__main__":
    unittest.main()
