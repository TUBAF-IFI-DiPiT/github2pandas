import unittest
import os
from pathlib import Path
import shutil
from github2pandas.github2pandas import GitHub2Pandas

class TestPullRequests(unittest.TestCase):
    """
    Test case for GitHub2Pandas class.
    """
    github_token = os.environ['TOKEN']
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    default_data_folder = Path("test_data")

    def test_generate__pandas_tables(self):
        github2pandas = GitHub2Pandas(self.github_token,self.default_data_folder)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)
        github2pandas.generate_pandas_tables(repo)

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        #shutil.rmtree("test_data")
        pass

if __name__ == "__main__":
    unittest.main()