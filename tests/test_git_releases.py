import unittest
import os
from pathlib import Path
import shutil

from github2pandas.utility import Utility
from github2pandas.git_releases import GitReleases

class TestGitReleases(unittest.TestCase):
    """
    Test case for GitReleases class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("test_data", git_repo_name)
    github_connection = Utility.get_github_connection(github_token)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)

    def test_generate_git_releases_pandas_tables(self):
        git_releases = GitReleases(self.github_connection, self.repo, self.default_data_folder)
        git_releases.print_calls("Start git releases")
        git_releases.generate_pandas_tables()
        git_releases.print_calls("End git releases")

    def test_get_git_releases(self):
        git_releases = GitReleases.get_git_releases(self.default_data_folder)

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")
        
if __name__ == "__main__":
    unittest.main()
