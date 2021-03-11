#!/usr/bin/python
 
import unittest
import sys
import os
from pathlib import Path
from github2pandas import utility
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
        repo = utility.get_repo(repo_name=self.git_repo_name, token=self.github_token)
        result = AggPR.generate_pandas_tables(data_dir=self.default_data_folder, repo=repo)
        self.assertTrue( result, "generate_pandas_tables throws exception")
        
if __name__ == "__main__":
    unittest.main()
