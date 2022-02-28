import logging
import unittest
import os
from pathlib import Path
import pygit2 as git2
import shutil
# github2pandas imports
from github2pandas.core import Core
from github2pandas.github2pandas import GitHub2Pandas
from github2pandas.version import Version

class TestVersion(unittest.TestCase):
    """
    Test case for Version class.
    """
    github_token = os.environ['TOKEN']
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    data_root_dir = Path("test_data")
    log_level = logging.DEBUG

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        if self.data_root_dir.exists() and self.data_root_dir.is_dir():
            shutil.rmtree(self.data_root_dir, onerror=Core._file_error_handling)
        self.data_root_dir.mkdir(parents=True, exist_ok=True)

    def test_generate_pandas_tables_serial(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir, log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)

        #self.skipTest("Skip Test because it fails to delete the folder on windows")
        # clone_public_repository
        version = Version(github2pandas.github_connection, repo, self.data_root_dir, log_level=self.log_level)
        try:
            version.print_calls("Start clone repo")
            version.clone_repository()
            version.print_calls("End clone repo")
        except git2.GitError:
            self.skipTest("Skip Test because repo is not public")
        version.print_calls("Start version")
        version.generate_pandas_tables()
        version.print_calls("End version")

    def test_generate_pandas_tables_parallel(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir, log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)

        #self.skipTest("Skip Test because it fails to delete the folder on windows")
        # clone_public_repository
        version = Version(github2pandas.github_connection, repo, self.data_root_dir, 
                          log_level=self.log_level, number_of_proceses = 2)
        try:
            version.print_calls("Start clone repo")
            version.clone_repository()
            version.print_calls("End clone repo")
        except git2.GitError:
            self.skipTest("Skip Test because repo is not public")
        version.print_calls("Start version")
        version.generate_pandas_tables()
        version.print_calls("End version")
        
    def test_get_data_frames(self):
        data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name,Version.Files.DATA_DIR)
        commits = Core.get_pandas_data_frame(data_dir, Version.Files.COMMITS)
        edits = Core.get_pandas_data_frame(data_dir, Version.Files.EDITS)
        branches = Core.get_pandas_data_frame(data_dir, Version.Files.BRANCHES)
        pass
    

if "__main__" == __name__:
    unittest.main()
