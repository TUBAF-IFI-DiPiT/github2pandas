import logging
import unittest
import os
from pathlib import Path
import shutil
# github2pandas imports
from github2pandas.core import Core
from github2pandas.github2pandas import GitHub2Pandas

class TestPullRequests(unittest.TestCase):
    """
    Test case for GitHub2Pandas class.
    """
    github_token = os.environ['TOKEN']
    #git_repo_name = "fluentui"
    #git_repo_owner = "microsoft"
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    data_root_dir = Path("test_data")
    log_level = logging.DEBUG

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        if self.data_root_dir.exists() and self.data_root_dir.is_dir():
            shutil.rmtree(self.data_root_dir, onerror=Core._file_error_handling)
        self.data_root_dir.mkdir(parents=True, exist_ok=True)

    def test_generate_pandas_tables(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir,log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)
        github2pandas.generate_pandas_tables(repo)
    
    def test_get_all_data_frames(self):
        repo_data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name)
        for key, value in GitHub2Pandas.FILES.items():
            for file in value:
                df = GitHub2Pandas.get_pandas_data_frame(repo_data_dir, key, file)

if __name__ == "__main__":
    unittest.main()