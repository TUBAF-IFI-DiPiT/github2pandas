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
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    data_root_dir = Path("test_data")

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        shutil.rmtree("test_data", onerror=Core._file_error_handling)
        self.data_root_dir.mkdir(parents=True, exist_ok=True)

    def test_generate_pandas_tables(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)

        issues = Issues(github2pandas.github_connection, repo, self.data_root_dir)
        issues.print_calls("Start issues")
        issues.generate_pandas_tables()
        issues.print_calls("End issues")
        # check max request limit
        issues = Issues(github2pandas.github_connection, repo, self.data_root_dir, 20)
        issues.print_calls("Start rate limit issues")
        issues.generate_pandas_tables()
        issues.print_calls("End rate limit issues")

    def test_get_data_frames(self):
        data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name,Issues.DATA_DIR)
        issues = Core.get_pandas_data_frame(data_dir, Issues.ISSUES)
        comments = Core.get_pandas_data_frame(data_dir, Issues.COMMENTS)
        events = Core.get_pandas_data_frame(data_dir, Issues.EVENTS)
        reactions = Core.get_pandas_data_frame(data_dir, Issues.ISSUES_REACTIONS)
        pass

if __name__ == "__main__":
    unittest.main()