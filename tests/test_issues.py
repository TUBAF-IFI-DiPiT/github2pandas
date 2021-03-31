import unittest
import os
from pathlib import Path
import github

from github2pandas.utility import Utility
from github2pandas.issues import Issues

class TestIssues(unittest.TestCase):
    """
    Test case for Issues class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)

    def test_generate_issue_pandas_tables(self):
        """
        Test generate issues pandas tables without reactions and check for updates.
        """

        Issues.generate_issue_pandas_tables(self.repo, self.default_data_folder, check_for_updates=False)

    def test_generate_issue_pandas_tables_check(self):
        """
        Test generate issues pandas tables with reactions check for updates.
        """

        Issues.generate_issue_pandas_tables(self.repo, self.default_data_folder)

    def test_generate_issue_pandas_tables_reactions(self):
        """
        Test generate issues pandas tables with reactions and without check for updates.
        """

        Issues.generate_issue_pandas_tables(self.repo, self.default_data_folder, reactions=True, check_for_updates=False)

    def test_get_issues(self):
        """
        Test get issues.
        """

        issues = Issues.get_issues(self.default_data_folder)
        issues_comments = Issues.get_issues(self.default_data_folder, filename=Issues.ISSUES_COMMENTS)
        issues_reactions = Issues.get_issues(self.default_data_folder, filename=Issues.ISSUES_REACTIONS)
        issues_events = Issues.get_issues(self.default_data_folder, filename=Issues.ISSUES_EVENTS)

    def test_extract_issue_data(self):
        """
        Test extract issue data.
        """

        issues = self.repo.get_issues(state='all') 
        for issue in issues:
            # remove pull_requests from issues
            if issue._pull_request == github.GithubObject.NotSet:
                issue_data = Issues.extract_issue_data(issue, self.users_ids, self.default_data_folder)
                break

if __name__ == "__main__":
    unittest.main()