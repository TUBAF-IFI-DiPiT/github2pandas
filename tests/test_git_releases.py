import unittest
import os
from pathlib import Path
import github
import datetime
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
        class User:
             node_id = "test_extract_git_releases_data"
             name = "test_extract_git_releases_data"
             email = "test_extract_git_releases_data@test.de"
             login = "test_extract_git_releases_data"
        class GitRelease:
            id = 0
            body = "test_extract_git_releases_data"
            title = "test_extract_git_releases_data"
            tag_name = "test_extract_git_releases_data"
            target_commitish = "test_extract_git_releases_data"
            draft = "test_extract_git_releases_data"
            prerelease = "test_extract_git_releases_data"
            _author = User()
            author = User()
            created_at = datetime.datetime.now()
            published_at = datetime.datetime.now()
        
        git_release_data = GitReleases.extract_git_releases_data(GitRelease(), self.users_ids, self.default_data_folder)
        self.assertIsNotNone(git_release_data)
        git_release = GitRelease()
        git_release._author = github.GithubObject.NotSet
        git_release_data = GitReleases.extract_git_releases_data(git_release, self.users_ids, self.default_data_folder)
        self.assertIsNotNone(git_release_data)
        self.assertFalse("author" in git_release_data.keys())
    
    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")
        self.users_ids = {}
        
if __name__ == "__main__":
    unittest.main()
