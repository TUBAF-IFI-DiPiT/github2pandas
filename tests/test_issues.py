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

    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("test_data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)

    def test_generate_issue_pandas_tables(self):
        Issues.generate_issue_pandas_tables(self.repo, self.default_data_folder, check_for_updates=False)
        Issues.generate_issue_pandas_tables(self.repo, self.default_data_folder)
        Issues.generate_issue_pandas_tables(self.repo, self.default_data_folder, reactions=True, check_for_updates=False)

    def test_get_issues(self):
        issues = Issues.get_issues(self.default_data_folder)
        issues_comments = Issues.get_issues(self.default_data_folder, filename=Issues.ISSUES_COMMENTS)
        issues_reactions = Issues.get_issues(self.default_data_folder, filename=Issues.ISSUES_REACTIONS)
        issues_events = Issues.get_issues(self.default_data_folder, filename=Issues.ISSUES_EVENTS)

    def test_extract_issue_data(self):
        issues = self.repo.get_issues(state='all') 
        for issue in issues:
            # remove pull_requests from issues
            if issue._pull_request == github.GithubObject.NotSet:
                issue_data = Issues.extract_issue_data(issue, self.users_ids, self.default_data_folder)
                break
        class User:
             node_id = "test_extract_issue_data"
             name = "test_extract_issue_data"
             email = "test_extract_issue_data@test.de"
             login = "test_extract_issue_data"
        class Issue:
            assignees = []
            body = "test_extract_issue_data"
            closed_at = datetime.datetime.now()
            _closed_by = User()
            closed_by = User()
            created_at = datetime.datetime.now()
            id = 0
            labels = []
            state = "test_extract_issue_data"
            title = "test_extract_issue_data"
            updated_at = datetime.datetime.now()
            _user = User()
            user = User()
        
        issue_data = Issues.extract_issue_data(Issue(), self.users_ids, self.default_data_folder)
        self.assertIsNotNone(issue_data)
        issue = Issue()
        issue._user = github.GithubObject.NotSet
        issue._closed_by = github.GithubObject.NotSet
        issue_data = Issues.extract_issue_data(issue, self.users_ids, self.default_data_folder)
        self.assertIsNotNone(issue_data)
        self.assertFalse("author" in issue_data.keys())
        self.assertFalse("closed_by" in issue_data.keys())

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")
        self.users_ids = {}

if __name__ == "__main__":
    unittest.main()