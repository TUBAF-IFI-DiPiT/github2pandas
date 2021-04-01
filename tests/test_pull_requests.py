#!/usr/bin/python
 
import unittest
import os
from pathlib import Path
import datetime
import github

from github2pandas.utility import Utility
from github2pandas.pull_requests import PullRequests

class TestPullRequests(unittest.TestCase):
    """
    Test case for PullRequests class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)

    def test_generate_pull_request_pandas_tables(self):
        PullRequests.generate_pull_request_pandas_tables(self.repo, self.default_data_folder, check_for_updates=False)
        PullRequests.generate_pull_request_pandas_tables(self.repo, self.default_data_folder)
        PullRequests.generate_pull_request_pandas_tables(self.repo, self.default_data_folder, reactions=True, check_for_updates=False)

    def test_get_pull_requests(self):
        pull_requests = PullRequests.get_pull_requests(self.default_data_folder)
        pull_requests_comments = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_COMMENTS)
        pull_requests_reactions = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_REACTIONS)
        pull_requests_reviews = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_REVIEWS)
        pull_requests_events = PullRequests.get_pull_requests(self.default_data_folder, filename=PullRequests.PULL_REQUESTS_EVENTS)

    def test_extract_pull_request_data(self):
        pull_requests = self.repo.get_pulls(state='all') 
        for pull_request in pull_requests:
            pull_request_data = PullRequests.extract_pull_request_data(pull_request, self.users_ids, self.default_data_folder)
            break
        class User:
             node_id = "test_extract_pull_request_data"
             name = "test_extract_pull_request_data"
             email = "test_extract_pull_request_data@test.de"
             login = "test_extract_pull_request_data"
        class PullRequest:
            assignees = []
            body = "test_extract_pull_request_data"
            closed_at = datetime.datetime.now()
            _merged_by = User()
            merged_by = User()
            created_at = datetime.datetime.now()
            merged_at = datetime.datetime.now()
            id = 0
            labels = []
            state = "test_extract_pull_request_data"
            title = "test_extract_pull_request_data"
            updated_at = datetime.datetime.now()
            _user = User()
            user = User()
        
        pull_request_data = PullRequests.extract_pull_request_data(PullRequest(), self.users_ids, self.default_data_folder)
        self.assertIsNotNone(pull_request_data)
        pull_request = PullRequest()
        pull_request._user = github.GithubObject.NotSet
        pull_request._merged_by = github.GithubObject.NotSet
        pull_request_data = PullRequests.extract_pull_request_data(pull_request, self.users_ids, self.default_data_folder)
        self.assertIsNotNone(pull_request_data)
        self.assertFalse("author" in pull_request_data.keys())
        self.assertFalse("merged_by" in pull_request_data.keys())
        # remove users data
        os.remove(Path(self.default_data_folder, Utility.USERS))
        self.users_ids = {}
    
    def test_extract_pull_request_review_data(self):
        pull_requests = self.repo.get_pulls(state='all') 
        for pull_request in pull_requests:
            for review in pull_request.get_reviews():
                pull_request_review_data = PullRequests.extract_pull_request_review_data(review, pull_request.id, self.users_ids, self.default_data_folder)
                break
            break
        class User:
             node_id = "test_extract_pull_request_review_data"
             name = "test_extract_pull_request_review_data"
             email = "test_extract_pull_request_review_data@test.de"
             login = "test_extract_pull_request_review_data"
        class PullRequestReview:
            body = "test_extract_pull_request_review_data"
            submitted_at = datetime.datetime.now()
            id = 0
            state = "test_extract_pull_request_review_data"
            _user = User()
            user = User()
        
        pull_request_review_data = PullRequests.extract_pull_request_review_data(PullRequestReview(), 0, self.users_ids, self.default_data_folder)
        self.assertIsNotNone(pull_request_review_data)
        pull_request_review = PullRequestReview()
        pull_request_review._user = github.GithubObject.NotSet
        pull_request_review_data = PullRequests.extract_pull_request_review_data(pull_request_review, 0, self.users_ids, self.default_data_folder)
        self.assertIsNotNone(pull_request_review_data)
        self.assertFalse("author" in pull_request_review_data.keys())
        # remove users data
        os.remove(Path(self.default_data_folder, Utility.USERS))
        self.users_ids = {}

if __name__ == "__main__":
    unittest.main()
