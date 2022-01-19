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
    github_connection = Utility.get_github_connection(github_token)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)

    def test_generate_workflow_pandas_tables(self):
        repository = Repository(self.github_connection, self.repo, self.default_data_folder)
        repository.print_calls("Start repository")
        repository.generate_pandas_tables()
        repository.print_calls("End repository")
        repository.print_calls("Start repository")
        repository.generate_pandas_tables(contributor_companies_included=True)
        repository.print_calls("End repository")
        
    def test_get_workflows(self):
        pd_repository = Repository.get_repository_keyparameter(self.default_data_folder)

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")

if "__main__" == __name__:
    unittest.main()