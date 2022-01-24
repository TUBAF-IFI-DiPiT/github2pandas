import logging
import unittest
import os
from pathlib import Path
import shutil
# github2pandas imports
from github2pandas.core import Core
from github2pandas.github2pandas import GitHub2Pandas
from github2pandas.pull_requests import PullRequests

class TestPullRequests(unittest.TestCase):
    """
    Test case for PullRequests class.
    """
    github_token = os.environ['TOKEN']
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    data_root_dir = Path("test_data")
    log_level = logging.DEBUG

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        shutil.rmtree("test_data", onerror=Core._file_error_handling)
        self.data_root_dir.mkdir(parents=True, exist_ok=True)

    def test_generate_pandas_tables(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir, log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)

        pull_requests = PullRequests(github2pandas.github_connection, repo, self.data_root_dir, log_level=self.log_level)
        pull_requests.print_calls("Start pr (No Issues)")
        pull_requests.generate_pandas_tables()
        pull_requests.print_calls("End pr (No Issues)")
        pull_requests.print_calls("Start pr")
        pull_requests.generate_pandas_tables()
        pull_requests.print_calls("End pr")
        pull_requests = PullRequests(github2pandas.github_connection, repo, self.data_root_dir,10, log_level=self.log_level)
        pull_requests.print_calls("Start rate limit pr")
        pull_requests.generate_pandas_tables()
        pull_requests.print_calls("End rate limit pr")

    def test_get_data_frames(self):
        data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name,PullRequests.DATA_DIR)
        pull_requests = Core.get_pandas_data_frame(data_dir, PullRequests.PULL_REQUESTS)
        reviews = Core.get_pandas_data_frame(data_dir, PullRequests.REVIEWS)
        reviews_comments = Core.get_pandas_data_frame(data_dir, PullRequests.REVIEWS_COMMENTS)
        reactions = Core.get_pandas_data_frame(data_dir, PullRequests.PULL_REQUESTS_REACTIONS)
        pass

if __name__ == "__main__":
    unittest.main()
