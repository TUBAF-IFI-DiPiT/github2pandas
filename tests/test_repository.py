import logging
import unittest
import os
from pathlib import Path
import shutil
# github2pandas imports
from github import Github
from github2pandas.core import Core
from github2pandas.github2pandas import GitHub2Pandas
from github2pandas.repository import Repository

class TestRepositories(unittest.TestCase):
    """
    Test case for Repository class.
    """
    github_token = os.environ['TOKEN']
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    data_root_dir = Path("test_data")
    log_level = logging.DEBUG

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        if self.data_root_dir.exists() and self.data_root_dir.is_dir():
            shutil.rmtree(self.data_root_dir, onerror=Core.file_error_handling)
        self.data_root_dir.mkdir(parents=True, exist_ok=True)

    def test_generate_pandas_tables(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir, log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)

        repository = Repository(github2pandas.github_connection, repo, self.data_root_dir, log_level=self.log_level)
        repository.print_calls("Start repository")
        repository.generate_pandas_tables()
        repository.print_calls("End repository")
        repository.print_calls("Start repository with companies")
        repository.generate_pandas_tables(contributor_companies_included=True)
        repository.print_calls("End repository with companies")
    
    def test_generate_pandas_tables_on_large_repo(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir, log_level=self.log_level)
        repo = github2pandas.get_repo("microsoft","vscode")

        repository = Repository(github2pandas.github_connection, repo, self.data_root_dir, log_level=self.log_level)
        repository.print_calls("Start large repository with companies")
        repository.generate_pandas_tables(contributor_companies_included=True)
        repository.print_calls("End large repository with companies")
        
    def test_get_workflows(self):
        data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name,Repository.Files.DATA_DIR)
        repository = Core.get_pandas_data_frame(data_dir, Repository.Files.REPOSITORY)
        pass

if "__main__" == __name__:
    unittest.main()