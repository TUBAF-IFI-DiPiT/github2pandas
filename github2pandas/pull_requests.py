import pandas as pd
from pathlib import Path
import os
from .utility import Utility
import github

class PullRequests():
    """
    Class to aggregate Pull Requests

    Attributes
    ----------
    PULL_REQUESTS_DIR : str
        Pull request dir where all files are saved in.
    PULL_REQUESTS : str
        Pandas table file for pull request data.
    PULL_REQUESTS_COMMENTS : str
        Pandas table file for comments data in pull requests.
    PULL_REQUESTS_REACTIONS : str
        Pandas table file for reactions data in pull requests.
    PULL_REQUESTS_REVIEWS : str
        Pandas table file for reviews data in pull requests.
    PULL_REQUESTS_EVENTS : str
        Pandas table file for events data in pull requests.

    Methods
    -------
    extract_pull_request_data(pull_request, users_ids, data_root_dir)
        Extracting general pull request data.
    extract_pull_request_review_data(review, pull_request_id, users_ids, data_root_dir)
        Extracting general review data from a pull request.
    generate_pull_request_pandas_tables(repo, data_root_dir, reactions=False, check_for_updates=True)
        Extracting the complete pull request data from a repository.
    generate_pull_request_pandas_tables_with_reactions(repo, data_root_dir)
        Extracting the complete pull request data from a repository including all reactions.
    generate_pull_request_pandas_tables_without_reactions(repo, data_root_dir)
        Extracting the complete pull request data from a repository excluding all reactions.
    get_pull_requests(data_root_dir, filename=PULL_REQUESTS))
        Get a genearted pandas table.
    
    """
    PULL_REQUESTS_DIR = "PullRequests"
    PULL_REQUESTS = "pdPullRequests.p"
    PULL_REQUESTS_COMMENTS = "pdPullRequestsComments.p"
    PULL_REQUESTS_REACTIONS = "pdPullRequestsReactions.p"
    PULL_REQUESTS_REVIEWS = "pdPullRequestsReviews.p"
    PULL_REQUESTS_EVENTS = "pdPullRequestsEvents.p"
    
    @staticmethod
    def extract_pull_request_data(pull_request, users_ids, data_root_dir):
        """
        extract_pull_request_data(pull_request, users_ids, data_root_dir)

        Extracting general pull request data.

        Parameters
        ----------
        pull_request: PullRequest
            PullRequest object from pygithub.
        users_ids: dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir: str
            Data root directory for the repository.

        Returns
        -------
        dict
            Dictionary with the extracted general pull request data.

        Notes
        -----
            PyGithub PullRequest object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html

        """
        
        pull_request_data = {}
        pull_request_data["id"] = pull_request.id
        pull_request_data["body"] = pull_request.body
        pull_request_data["title"] = pull_request.title
        pull_request_data["closed_at"] = pull_request.closed_at
        pull_request_data["created_at"] = pull_request.created_at
        pull_request_data["merged_at"] = pull_request.merged_at
        pull_request_data["state"] = pull_request.state
        pull_request_data["updated_at"] = pull_request.updated_at
        pull_request_data["assignees"] = Utility.extract_assignees(pull_request.assignees, users_ids, data_root_dir)
        pull_request_data["labels"] = Utility.extract_labels(pull_request.labels)
        if not pull_request._merged_by == github.GithubObject.NotSet:
            pull_request_data["merged_by"] = Utility.extract_user_data(pull_request.merged_by, users_ids, data_root_dir)
        if not pull_request._user == github.GithubObject.NotSet:
            pull_request_data["author"] = Utility.extract_user_data(pull_request.user, users_ids, data_root_dir)
        # slow calls
        #pull_request_data["deletions"] = pull_request.deletions
        #pull_request_data["additions"] = pull_request.additions
        #pull_request_data["merged"] = pull_request.merged
        return pull_request_data
    
    @staticmethod
    def extract_pull_request_review_data(review, pull_request_id, users_ids, data_root_dir):
        """
        extract_pull_request_review_data(review, users_ids, pull_request_id)

        Extracting review data from a pull request.

        Parameters
        ----------
        review: PullRequestReview
            PullRequestReview object from pygithub.
        pull_request_id: int
            Pull request id as foreign key.
        users_ids: dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir: str
            Data root directory for the repository.

        Returns
        -------
        dict
            Dictionary with the extracted review data.

        Notes
        -----
            PyGithub PullRequestReview object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html

        """
        review_data = {}
        review_data["pull_request_id"] = pull_request_id
        review_data["id"] = review.id
        if not review._user == github.GithubObject.NotSet:
            review_data["author"] = Utility.extract_user_data(review.user, users_ids, data_root_dir)
        review_data["body"] = review.body
        review_data["state"] = review.state
        review_data["submitted_at"] = review.submitted_at
        return review_data
    
    @staticmethod
    def generate_pull_request_pandas_tables(repo, data_root_dir, reactions=False, check_for_updates=True):
        """
        generate_pull_request_pandas_tables(repo, data_root_dir, reactions=False, check_for_updates=True)

        Extracting the complete pull request data from a repository.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        data_root_dir: str
            Data root directory for the repository.
        reactions: bool, default=False
            If reactions should also be exracted. The extraction of all reactions increases significantly the aggregation speed.
        check_for_updates: bool, default=True
            Check first if there are any new pull requests.
        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        
        if check_for_updates:
            pull_requests = repo.get_pulls(state='all') 
            old_pull_requests = PullRequests.get_pull_requests(data_root_dir)
            if not Utility.check_for_updates_paginated(pull_requests, old_pull_requests):
                return
        if reactions:
            PullRequests.generate_pull_request_pandas_tables_with_reactions(repo, data_root_dir)
        else:
            PullRequests.generate_pull_request_pandas_tables_without_reactions(repo, data_root_dir)
        
    @staticmethod
    def generate_pull_request_pandas_tables_with_reactions(repo, data_root_dir):
        """
        generate_pull_request_pandas_tables_with_reactions(repo, data_root_dir)

        Extracting the complete pull request data from a repository including all reactions.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        data_root_dir: str
            Data root directory for the repository.
        
        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        pull_request_dir = Path(data_root_dir, PullRequests.PULL_REQUESTS_DIR)
        pull_requests = repo.get_pulls(state='all') 
        users_ids = Utility.get_users_ids(data_root_dir)
        pull_request_list = []
        pull_request_comment_list = []
        pull_request_reaction_list = []
        pull_request_review_list = []
        pull_request_event_list = []
        # pull request data
        for pull_request in pull_requests:
            pull_request_data = PullRequests.extract_pull_request_data(pull_request, users_ids, data_root_dir)
            pull_request_list.append(pull_request_data)
            # pull request comment data
            for comment in pull_request.get_comments():
                pull_request_comment_data = Utility.extract_comment_data(comment, pull_request.id, "pull_request", users_ids, data_root_dir)
                pull_request_comment_list.append(pull_request_comment_data)
                # pull request reaction data
                for reaction in comment.get_reactions():
                    reaction_data = Utility.extract_reaction_data(reaction,comment.id, "comment", users_ids, data_root_dir)
                    pull_request_reaction_list.append(reaction_data)
            pull_request_list.append(pull_request_data)
            # pull request review data
            for review in pull_request.get_reviews():
                pull_request_review_data = PullRequests.extract_pull_request_review_data(review, pull_request.id, users_ids, data_root_dir)
                pull_request_review_list.append(pull_request_review_data)
            pull_request_list.append(pull_request_data)
            # pull request issue comments data
            for comment in pull_request.get_issue_comments():
                pull_request_comment_data = Utility.extract_comment_data(comment, pull_request.id, "pull_request", users_ids, data_root_dir)
                pull_request_comment_list.append(pull_request_comment_data)
                # pull request reaction data
                for reaction in comment.get_reactions():
                    reaction_data = Utility.extract_reaction_data(reaction,comment.id, "comment", users_ids, data_root_dir)
                    pull_request_reaction_list.append(reaction_data)
            pull_request_list.append(pull_request_data)
            # pull request issue events
            for event in pull_request.get_issue_events():
                pull_request_event_data = Utility.extract_event_data(event, pull_request.id, "pull_request", users_ids, data_root_dir)
                pull_request_event_list.append(pull_request_event_data)
            pull_request_list.append(pull_request_data)
        # Save lists
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS, pull_request_list)
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS_COMMENTS, pull_request_comment_list)
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS_REACTIONS, pull_request_reaction_list)
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS_REVIEWS, pull_request_review_list)
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS_EVENTS, pull_request_event_list)
        return True
    
    @staticmethod
    def generate_pull_request_pandas_tables_without_reactions(repo, data_root_dir):
        """
        generate_pull_request_pandas_tables_without_reactions(repo, data_root_dir)

        Extracting the complete pull request data from a repository excluding all reactions.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        data_root_dir: str
            Data root directory for the repository.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        pull_request_dir = Path(data_root_dir, PullRequests.PULL_REQUESTS_DIR)
        pull_requests = repo.get_pulls(state='all') 
        users_ids = Utility.get_users_ids(data_root_dir)
        pull_request_list = []
        pull_request_comment_list = []
        pull_request_review_list = []
        pull_request_event_list = []
        # pull request data
        for pull_request in pull_requests:
            pull_request_data = PullRequests.extract_pull_request_data(pull_request, users_ids, data_root_dir)
            pull_request_list.append(pull_request_data)
            # pull request comment data
            for comment in pull_request.get_comments():
                pull_request_comment_data = Utility.extract_comment_data(comment, pull_request.id, "pull_request", users_ids, data_root_dir)
                pull_request_comment_list.append(pull_request_comment_data)
            # pull request review data
            for review in pull_request.get_reviews():
                pull_request_review_data = PullRequests.extract_pull_request_review_data(review, pull_request.id, users_ids, data_root_dir)
                pull_request_review_list.append(pull_request_review_data)
            # pull request issue comments data
            for comment in pull_request.get_issue_comments():
                pull_request_comment_data = Utility.extract_comment_data(comment, pull_request.id, "pull_request", users_ids, data_root_dir)
                pull_request_comment_list.append(pull_request_comment_data)
            # pull request issue events
            for event in pull_request.get_issue_events():
                pull_request_event_data = Utility.extract_event_data(event, pull_request.id, "pull_request", users_ids, data_root_dir)
                pull_request_event_list.append(pull_request_event_data)
        # Save lists
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS, pull_request_list)
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS_COMMENTS, pull_request_comment_list)
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS_REVIEWS, pull_request_review_list)
        Utility.save_list_to_pandas_table(pull_request_dir, PullRequests.PULL_REQUESTS_EVENTS, pull_request_event_list)
        return True
    
    @staticmethod
    def get_pull_requests(data_root_dir, filename=PULL_REQUESTS):
        """
        get_pull_requests(data_root_dir, filename=PULL_REQUESTS))

        Get a genearted pandas table.

        Parameters
        ----------
        data_root_dir: str
            Data root directory for the repository.
        filename: str, default=PULL_REQUESTS
            Pandas table file for pull requests or comments or reactions or reviews or events data.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can includes the desired data

        """
        pull_request_dir = Path(data_root_dir, PullRequests.PULL_REQUESTS_DIR)
        pd_pull_requests_file = Path(pull_request_dir, filename)
        if pd_pull_requests_file.is_file():
            return pd.read_pickle(pd_pull_requests_file)
        else:
            return pd.DataFrame()
