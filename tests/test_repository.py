import unittest
import os
from pathlib import Path
import datetime
import shutil

from github2pandas.repository import Repository
from github2pandas.utility import Utility

class TestRepositories(unittest.TestCase):
    """
    Test case for Repository class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("test_data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)

    def test_generate_workflow_pandas_tables(self):
        Repository.generate_repository_pandas_table(self.repo, self.default_data_folder, contributor_companies_included = True)
        Repository.generate_repository_pandas_table(self.repo, self.default_data_folder, contributor_companies_included = False)
        
    def test_get_workflows(self):
        pd_repository = Repository.get_repository_keyparameter(self.default_data_folder)

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")

if "__main__" == __name__:
    unittest.main()