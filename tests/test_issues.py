#!/usr/bin/python
 
import unittest
import sys
import os
from pathlib import Path
import pandas as pd
import warnings

from github2pandas.utility import Utility
from github2pandas.issues import Issues

class TestIssues(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)

    def test_issues_aggregation(self):
        """
        Test issues aggregation
        """
        warnings.simplefilter ("ignore", ResourceWarning)
        repo = Utility.get_repo(self.git_repo_owner, self.git_repo_name, self.github_token, self.default_data_folder)
        Issues.generate_issue_pandas_tables(repo, self.default_data_folder)
        issues = Issues.get_issues(self.default_data_folder)
        self.assertFalse(issues.empty , "issues have no data")

if __name__ == "__main__":
    unittest.main()