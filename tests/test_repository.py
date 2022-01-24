import unittest
import os
from pathlib import Path
import datetime
import shutil
from github import Github
from github2pandas.github2pandas import GitHub2Pandas
from github2pandas.repository import Repository

class TestRepositories(unittest.TestCase):
    """
    Test case for Repository class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("test_data")

    github2pandas = GitHub2Pandas(github_token,default_data_folder)
    repo = github2pandas.get_repo(git_repo_owner, git_repo_name)
    params = {
        "git_releases": False,
        "issues": False,
        "pull_requests": False,
        "repository": True,
        "version": False,
        "workflows": False
    }

    def test_generate_pandas_tables_repository(self):
        repository = Repository(Github(self.github_token), self.repo, self.default_data_folder)
        repository.print_calls("Start repository")
        repository.generate_pandas_tables()
        repository.print_calls("End repository")
        repository.print_calls("Start repository")
        repository.generate_pandas_tables(contributor_companies_included=True)
        repository.print_calls("End repository")
    
    def test_repository_on_large_repo(self):
        repo = self.github2pandas.get_repo("microsoft","vscode")
        repository = Repository(Github(self.github_token), repo, self.default_data_folder)
        repository.print_calls("Start large repository")
        repository.generate_pandas_tables(contributor_companies_included=True)
        repository.print_calls("End large repository")

    def test_generate_pandas_tables_github2pandas(self):
        self.github2pandas.generate_pandas_tables(self.repo,self.params)
        
    def test_get_workflows(self):
        pd_repository = Repository.get_repository_keyparameter(self.default_data_folder)

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")

if "__main__" == __name__:
    unittest.main()