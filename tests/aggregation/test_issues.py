#!/usr/bin/python
 
import unittest
import sys
import os
from pathlib import Path
import pandas as pd
from github2pandas.aggregation.utility import Utility
from github2pandas.aggregation.issues import AggIssues

class TestIssueAggregation(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    def test_generate_pandas_tables(self):
        """
        Test generating pandas table
        """
        repo = Utility.get_repo(self.git_repo_owner, self.git_repo_name, self.github_token)
        AggIssues.generate_issue_pandas_tables(repo, self.default_data_folder)
        self.assertTrue(True)
        
    def test_get_issues(self):
        """
        Test to get issue pandas Tables
        """
        data_folder = Path("data", self.git_repo_name)
        issues = AggIssues.get_issues(data_folder)
        self.assertFalse(issues.empty , "issues have no data")

if __name__ == "__main__":
    unittest.main()