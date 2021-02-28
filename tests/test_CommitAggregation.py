#!/usr/bin/python
 
import unittest
import os
import yaml
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Commits_aggregation import cloneRepository,\
                                    generateDataBase,\
                                    generatePandasTables

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

    def test_generate_commit_pandas_files(self):
        """
        Extract commit history for small open source project
        """
        pdCommits, pdEdits = generatePandasTables(data_dir=self.default_data_folder,
                                                  git_repo_name=self.git_repo_name)

        self.assertTrue( not pdCommits.empty, "Pandas data frame empty")


class Test_CommitExtractionPrivate(unittest.TestCase):

    git_repo_name = "xAPI_for_GitHubData"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    secret_path = Path("secret.yml")
    with open(secret_path, "r") as ymlfile:
        sct = yaml.load(ymlfile, Loader=yaml.FullLoader)

    github_token = sct["github"]["token"]

    def test_clone_private_repository(self):
        """
        Test cloning with private open source project
        """

        result = cloneRepository(git_repo_owner=self.git_repo_owner,
                                git_repo_name=self.git_repo_name,
                                git_repo_dir=self.default_repo_folder,
                                GitHubToken=self.github_token)

        self.assertTrue( result, "Cloning throws exception")

if "__main__" == __name__:
    unittest.main()