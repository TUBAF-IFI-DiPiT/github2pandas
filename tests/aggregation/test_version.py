#!/usr/bin/python
 
import unittest
import os
from pathlib import Path

from github2pandas.aggregation.utility import Utility
from github2pandas.aggregation.version import AggVersion as AggVer

class Test_CommitExtraction(unittest.TestCase):

    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)

    def test_clone_public_repository(self):
        """
        Test cloning with small open source project
        """
        repo = Utility.get_repo(self.git_repo_owner, self.git_repo_name, self.github_token)
        result = AggVer.clone_repository(repo=repo, 
                                         data_root_dir=self.default_data_folder, 
                                         github_token=self.github_token)
        self.assertTrue( result, "Cloning throws exception")

    def test_generate_pandas_files(self):
        """
        Extract commit history for small open source project
        """
        result  = AggVer.generate_version_pandas_tables(data_root_dir=self.default_data_folder)
        self.assertTrue( result, "Pandas data frame empty")


    def test_get_commit_pandas_files(self):
        """
        Extract commit history for small open source project
        """
        pdCommits = AggVer.get_raw_commit(data_root_dir=self.default_data_folder)
        self.assertTrue( not pdCommits.empty, "Pandas commit data frame empty")


    def test_get_edit_pandas_files(self):
        """
        Extract commit history for small open source project
        """
        pdEdits = AggVer.get_raw_edit(data_root_dir=self.default_data_folder)
        self.assertTrue( not pdEdits.empty, "Pandas edits data frame empty")


if "__main__" == __name__:
    unittest.main()