#!/usr/bin/python
 
import unittest
import os
from pathlib import Path

from github2pandas.utility import Utility
from github2pandas.pull_requests import PullRequests

class TestPullRequests(unittest.TestCase):
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)

    def test_generate_pull_request_pandas_tables(self):
        """
        Test generate pull request pandas tables without reactions and check for updates.
        """

        PullRequests.generate_pull_request_pandas_tables(self.repo, self.default_data_folder, check_for_updates=False)

    def test_generate_pull_request_pandas_tables_check(self):
        """
        Test generate pull request pandas tables with reactions check for updates.
        """

        PullRequests.generate_pull_request_pandas_tables(self.repo, self.default_data_folder)

    def test_generate_pull_request_pandas_tables_reactions(self):
        """
        Test generate pull request pandas tables with reactions and without check for updates.
        """

        PullRequests.generate_pull_request_pandas_tables(self.repo, self.default_data_folder, reactions=True, check_for_updates=False)

    def test_get_pull_requests(self):
        """
        Test get pull requests.
        """

        pull_requests = PullRequests.get_pull_requests(self.default_data_folder)
        pull_requests_comments = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_COMMENTS)
        pull_requests_reactions = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_REACTIONS)
        pull_requests_reviews = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_REVIEWS)
        pull_requests_events = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_EVENTS)

    def test_extract_pull_request_data(self):
        """
        Test extract pull request data.
        """

        pull_requests = self.repo.get_pulls(state='all') 
        for pull_request in pull_requests:
            pull_request_data = PullRequests.extract_pull_request_data(pull_request, self.users_ids, self.default_data_folder)
            break
    
    def test_extract_pull_request_review_data(self):
        """
        Test extract pull request review data.
        """

        pull_requests = self.repo.get_pulls(state='all') 
        for pull_request in pull_requests:
            for review in pull_request.get_reviews():
                pull_request_review_data = PullRequests.extract_pull_request_review_data(review, pull_request.id, self.users_ids, self.default_data_folder)
                break
            break

if __name__ == "__main__":
    unittest.main()
