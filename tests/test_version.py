import unittest
import os
from pathlib import Path
import pygit2 as git2

from github2pandas.utility import Utility
from github2pandas.version import Version

skip = False
class Test_Version(unittest.TestCase):
    """
    Test case for Version class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)

    def test_clone_public_repository(self):
        try:
            result = Version.clone_repository(self.repo, self.default_data_folder, self.github_token)
        except git2.GitError:
            global skip
            skip = True
            self.skipTest("Skip Test because repo is not public")

    def test_generate_pandas_files(self):
        if skip:
            self.skipTest("Skip Test due to GitError")
        result  = Version.generate_version_pandas_tables(data_root_dir=self.default_data_folder)


    def test_get_commit_pandas_files(self):
        if skip:
            self.skipTest("Skip Test due to GitError")
        pd_commits = Version.get_version(data_root_dir=self.default_data_folder)
        self.assertTrue( not pd_commits.empty)


    def test_get_edit_pandas_files(self):
        if skip:
            self.skipTest("Skip Test due to GitError")
        pd_edits = Version.get_version(self.default_data_folder, Version.VERSION_EDITS)
        self.assertTrue( not pd_edits.empty)
        
if "__main__" == __name__:
    unittest.main()