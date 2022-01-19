import unittest
import os
from pathlib import Path
import shutil

from github2pandas.utility import Utility
from github2pandas.pull_requests import PullRequests

class TestPullRequests(unittest.TestCase):
    """
    Test case for PullRequests class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("test_data", git_repo_name)
    github_connection = Utility.get_github_connection(github_token)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)

    def test_generate_pull_request_pandas_tables(self):
        pull_requests = PullRequests(self.github_connection, self.repo, self.default_data_folder)
        pull_requests.print_calls("Start pr")
        params = {
            "deep_pull_requests": False,
            "reactions": False,
            "reviews": False,
            "review_comment": True,
            "review_requested": False,
            "commits": False,
        }
        pull_requests.generate_pandas_tables(extraction_params=params)
        pull_requests.print_calls("End pr")
        pull_requests = PullRequests(self.github_connection, self.repo, self.default_data_folder,10)
        pull_requests.print_calls("Start pr")
        pull_requests.generate_pandas_tables(extraction_params=params)
        pull_requests.print_calls("End pr")

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")

if __name__ == "__main__":
    unittest.main()
