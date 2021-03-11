#!/usr/bin/python
 
import unittest
import sys
import os
from pathlib import Path
from github2pandas.utility import Utility
from github2pandas.pull_requests.aggregation import AggPullRequest as AggPR

class TestPullRequestAggregation(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    def test_generate_pandas_tables(self):
        """
        Test generating pandas table
        """
        repo = Utility.get_repo(repo_name=self.git_repo_name, token=self.github_token)
        result = AggPR.generate_pandas_tables(data_dir=self.default_data_folder, repo=repo)
        self.assertTrue( result, "generate_pandas_tables throws exception")
        
    def test_get_raw_pull_requests(self):
        """
        Test to get raw pull request pandas Tables
        """
        data_folder = Path("data", self.git_repo_name)
        pull_requests = AggPR.get_raw_pull_requests(data_folder)
        self.assertTrue( pull_requests.count()[0] > 0 , "pull requests have no data")

if __name__ == "__main__":
    unittest.main()