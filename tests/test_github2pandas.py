import logging
import unittest
import os
from pathlib import Path
import shutil
# github2pandas imports
from github2pandas.core import Core
from github2pandas.github2pandas import GitHub2Pandas

class TestPullRequests(unittest.TestCase):
    """
    Test case for GitHub2Pandas class.
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
        print(Core.UserFiles.to_list())
        print(Core.UserFiles.to_dict())
        pass

    def test_get_repository_information(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir,log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)
        repo = github2pandas.get_repo("microsoft","vscode")
        repo_fullnames = GitHub2Pandas.get_full_names_of_repositories(self.data_root_dir)
        pass
    
    def test_generate_pandas_tables(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir,log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)
        github2pandas.generate_pandas_tables(repo)
        GitHub2Pandas.save_tables_to_excel(Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name))

    def test_files_to_list(self):
        files = GitHub2Pandas.Files.to_list()
        pass
    
    def test_files_to_dict(self):
        files = GitHub2Pandas.Files.to_dict()
        pass

    def test_get_all_data_frames(self):
        repo_data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name)
        for files in GitHub2Pandas.Files.to_list():
            for file in files.to_list():
                if isinstance(file, str):
                    df = GitHub2Pandas.get_pandas_data_frame(repo_data_dir, files.DATA_DIR, file)

if __name__ == "__main__":
    unittest.main()