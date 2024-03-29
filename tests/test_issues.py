import logging
import unittest
import os
from pathlib import Path
import shutil
# github2pandas imports
from github2pandas.core import Core
from github2pandas.github2pandas import GitHub2Pandas
from github2pandas.issues import Issues

class TestIssues(unittest.TestCase):
    """
    Test case for Issues class.
    """
    github_token = os.environ['TOKEN']
    if "NAME" in os.environ:
        git_repo_name = os.environ['NAME']
        git_repo_owner = os.environ['OWNER']
    else:
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
        params = Issues.Params(reactions=True)
        issues = github2pandas.generate_issues_pandas_tables(repo, params)

    def test_get_data_frames(self):
        data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name,Issues.Files.DATA_DIR)
        issues = Core.get_pandas_data_frame(data_dir, Issues.Files.ISSUES)
        comments = Core.get_pandas_data_frame(data_dir, Issues.Files.COMMENTS)
        events = Core.get_pandas_data_frame(data_dir, Issues.Files.EVENTS)
        reactions = Core.get_pandas_data_frame(data_dir, Issues.Files.ISSUES_REACTIONS)
        pass

if __name__ == "__main__":
    unittest.main()