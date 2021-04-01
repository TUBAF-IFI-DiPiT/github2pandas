import unittest
import os
from pathlib import Path

from github2pandas.utility import Utility
from github2pandas.git_releases import GitReleases

class TestGitReleases(unittest.TestCase):
    """
    Test case for GitReleases class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)

    def test_generate_git_releases_pandas_tables(self):
        GitReleases.generate_git_releases_pandas_tables(self.repo, self.default_data_folder, check_for_updates=False)
        GitReleases.generate_git_releases_pandas_tables(self.repo, self.default_data_folder)

    def test_get_git_releases(self):
        git_releases = GitReleases.get_git_releases(self.default_data_folder)

    def test_extract_git_releases_data(self):
        git_releases = self.repo.get_releases()
        for git_release in git_releases:
            git_release_data = GitReleases.extract_git_releases_data(git_release, self.users_ids, self.default_data_folder)
            break

if __name__ == "__main__":
    unittest.main()
