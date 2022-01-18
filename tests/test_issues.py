import unittest
import os
from pathlib import Path
import github
import datetime
import shutil

from github2pandas.utility import Utility
from github2pandas.issues import Issues

class TestIssues(unittest.TestCase):
    """
    Test case for Issues class.
    """
    
    github_token = os.environ['TOKEN']

    #git_repo_name = "fluentui"
    #git_repo_owner = "microsoft"
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("test_data", git_repo_name)
    github_connection = Utility.get_github_connection(github_token)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)

    def test_generate_issue_pandas_tables(self):
        issues = Issues(self.github_connection, self.repo, self.default_data_folder)
        issues.print_calls("Start pr")
        params = {
            "reactions": False,
            "events": True,
            "comments": True
        }
        issues.generate_pandas_tables(extraction_params=params)
        issues.print_calls("End pr")
        #issues.generate_pandas_tables(True, False)
        #issues.generate_pandas_tables(False, True)
        #issues.generate_pandas_tables(True, True)
        # check max request limit
        #issues = Issues(self.github_connection, self.repo, self.default_data_folder, 20)
        #issues.generate_pandas_tables()

    def test_get_issues(self):
        issues = Issues.get_pandas_table(self.default_data_folder)
        issues_comments = Issues.get_pandas_table(self.default_data_folder, filename=Issues.ISSUES_COMMENTS)
        issues_reactions = Issues.get_pandas_table(self.default_data_folder, filename=Issues.ISSUES_REACTIONS)
        issues_events = Issues.get_pandas_table(self.default_data_folder, filename=Issues.ISSUES_EVENTS)

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")
        self.users_ids = {}

if __name__ == "__main__":
    unittest.main()