#!/usr/bin/python
 
import unittest
import os
from pathlib import Path
import warnings

from github2pandas.utility import Utility
from github2pandas.git_releases import GitReleases

class TestGitReleases(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)

    def test_git_releases_aggregation(self):
        """
        Test pull requests aggregation
        """
        warnings.simplefilter ("ignore", ResourceWarning)
        repo = Utility.get_repo(self.git_repo_owner, self.git_repo_name, self.github_token, self.default_data_folder)
        result = GitReleases.generate_git_releases_pandas_tables(repo, self.default_data_folder)
        git_releases = GitReleases.get_git_releases(self.default_data_folder)
        self.assertTrue( True , "No Error")

if __name__ == "__main__":
    unittest.main()
