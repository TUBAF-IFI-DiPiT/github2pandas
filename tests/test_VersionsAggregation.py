#!/usr/bin/python
 
import unittest
import os
import yaml
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.commits_edits.aggregation import cloneRepository,\
                                    generateDataBase,\
                                    generatePandasTables,\
                                    getCommitRawPandasTable,\
                                    getEditRawPandasTable

class Test_CommitExtractionPublic(unittest.TestCase):

    git_repo_name = "WillkommenAufLiaScript"
    git_repo_owner = "SebastianZug"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    def test_clone_public_repository(self):
        """
        Test cloning with small open source project
        """

        result = cloneRepository(git_repo_owner=self.git_repo_owner,
                                 git_repo_name=self.git_repo_name,
                                 git_repo_dir=self.default_repo_folder)
        self.assertTrue( result, "Cloning throws exception")


    def test_generate_commit_database(self):
        """
        Extract commit history for small open source project
        """
        result = generateDataBase(git_repo_dir=self.default_repo_folder,
                                  data_dir=self.default_data_folder,
                                  git_repo_name=self.git_repo_name)
        self.assertTrue( result, "Git2Net throws exception")


    def test_generate_pandas_files(self):
        """
        Extract commit history for small open source project
        """
        result  = generatePandasTables(data_dir=self.default_data_folder,
                                       git_repo_name=self.git_repo_name)
        self.assertTrue( result, "Pandas data frame empty")


    def test_get_commit_pandas_files(self):
        """
        Extract commit history for small open source project
        """
        pdCommits = getCommitRawPandasTable(data_dir=self.default_data_folder)
        self.assertTrue( not pdCommits.empty, "Pandas commit data frame empty")


    def test_get_edit_pandas_files(self):
        """
        Extract commit history for small open source project
        """
        pdEdits = getEditRawPandasTable(data_dir=self.default_data_folder)
        self.assertTrue( not pdEdits.empty, "Pandas edits data frame empty")


class Test_CommitExtractionPrivate(unittest.TestCase):

    git_repo_name = "xAPI_for_GitHubData"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    @unittest.skip("Skiped for GitHub-Actions")
    def test_clone_private_repository(self):
        """
        Test cloning with private open source project
        """

        github_token = os.environ['TOKEN']

        result = cloneRepository(git_repo_owner=self.git_repo_owner,
                                git_repo_name=self.git_repo_name,
                                git_repo_dir=self.default_repo_folder,
                                GitHubToken=github_token)
        self.assertTrue( result, "Cloning throws exception")


if "__main__" == __name__:
    unittest.main()