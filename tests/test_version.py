import unittest
import os
from pathlib import Path
import pygit2 as git2
import shutil

from github2pandas.utility import Utility
from github2pandas.version import Version

class TestVersion(unittest.TestCase):
    """
    Test case for Version class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    test_data_folder = Path("test_data")
    default_data_folder = Path(test_data_folder, git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)

    def test_version(self):
        self.skipTest("Skip Test because it fails to delete the folder on windows")
        # clone_public_repository
        try:
            result = Version.clone_repository(self.repo, self.default_data_folder, self.github_token)
        except git2.GitError:
            self.skipTest("Skip Test because repo is not public")
        

        # generate_version_pandas_tables
        result  = Version.generate_version_pandas_tables(data_root_dir=self.default_data_folder)
        
        # get_version
        pd_commits = Version.get_version(data_root_dir=self.default_data_folder)
        self.assertTrue( not pd_commits.empty)
        pd_edits = Version.get_version(self.default_data_folder, Version.VERSION_EDITS)
        self.assertTrue( not pd_edits.empty)
    
    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_data_folder.resolve(), onerror=Version.handleError)

if "__main__" == __name__:
    unittest.main()