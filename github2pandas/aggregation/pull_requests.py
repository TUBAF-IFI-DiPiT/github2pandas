import pandas as pd
from pathlib import Path
import pickle
import os
import shutil
from .utility import Utility

class AggPullRequest():
    """
    Class to aggregate Pull Requests

    Attributes
    ----------
    PULL_REQUESTS_DIR : str
        Pull request dir where all files are saved in.
    PULL_REQUESTS : str
        Pandas table file for raw pull request data.
    PULL_REQUESTS_COMMENTS : str
        Pandas table file for raw comments data in pull requests.
    PULL_REQUESTS_REACTIONS : str
        Pandas table file for raw reactions data in pull requests.
    PULL_REQUESTS_REVIEWS : str
        Pandas table file for raw reviews data in pull requests.
    PULL_REQUESTS_EVENTS : str
        Pandas table file for raw events data in pull requests.

    Methods
    -------
    extract_pull_request_data(pull_request, data_root_dir)
        Extracting general pull request data.
    extract_pull_request_review_data(review, pull_request_id, data_root_dir)
        Extracting general review data from a pull request.
    generate_pull_request_pandas_tables(repo, data_root_dir)
        Extracting the complete pull request data from a repository
    get_raw_pull_requests(data_root_dir, filename)
        Get the genearted pandas table.
    
    """
    PULL_REQUESTS_DIR = "PullRequests"
    PULL_REQUESTS = "pdPullRequests.p"
    PULL_REQUESTS_COMMENTS = "pdPullRequestsComments.p"
    PULL_REQUESTS_REACTIONS = "pdPullRequestsReactions.p"
    PULL_REQUESTS_REVIEWS = "pdPullRequestsReviews.p"
    PULL_REQUESTS_EVENTS = "pdPullRequestsEvents.p"
    
    @staticmethod
    def extract_pull_request_data(pull_request, data_root_dir):
        """
        extract_pull_request_data(pull_request, data_root_dir)

        Extracting general pull request data.

        Parameters
        ----------
        pull_request: PullRequest
            PullRequest object from pygithub.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        PullRequestData
            Dictionary with the extracted data.

        Notes
        -----
            PullRequest object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html

        """
        pull_request_data = AggPullRequest.PullRequestData()
        pull_request_data["id"] = pull_request.id
        pull_request_data["assignees"] = Utility.extract_assignees(pull_request.assignees, data_root_dir)
        pull_request_data["assignees_count"] = len(pull_request.assignees)  
        pull_request_data["body"] = pull_request.body
        pull_request_data["title"] = pull_request.title
        pull_request_data["changed_files"] = pull_request.changed_files
        pull_request_data["closed_at"] = pull_request.closed_at
        pull_request_data["created_at"] = pull_request.created_at
        pull_request_data["deletions"] = pull_request.deletions
        pull_request_data["additions"] = pull_request.additions
        pull_request_data["labels"] = Utility.extract_labels(pull_request.labels)
        pull_request_data["labels_count"] = len(pull_request.labels)
        pull_request_data["merged"] = pull_request.merged
        pull_request_data["merged_at"] = pull_request.merged_at
        pull_request_data["merged_by"] = Utility.extract_user_data(pull_request.merged_by, data_root_dir)
        if pull_request.milestone:
            pull_request_data["milestone_id"] = pull_request.milestone.id
        pull_request_data["state"] = pull_request.state
        pull_request_data["updated_at"] = pull_request.updated_at
        pull_request_data["author"] = Utility.extract_user_data(pull_request.user, data_root_dir)
        pull_request_data["comments_count"] = pull_request.get_comments().totalCount + pull_request.get_issue_comments().totalCount
        pull_request_data["issue_events_count"] = pull_request.get_issue_events().totalCount
        pull_request_data["reviews_count"] = pull_request.get_reviews().totalCount
        return pull_request_data
    
    @staticmethod
    def extract_pull_request_review_data(review, pull_request_id, data_root_dir):
        """
        extract_pull_request_review_data(review, pull_request_id)

        Extracting general review data from a pull request.

        Parameters
        ----------
        review: PullRequestReview
            PullRequestReview object from pygithub.
        pull_request_id: int
            Pull request id as foreign key.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            PullRequestReview object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html

        """
        review_data = AggPullRequest.PullRequestReviewData()
        review_data["pull_request_id"] = pull_request_id
        review_data["id"] = review.id
        review_data["author"] = Utility.extract_user_data(review.user, data_root_dir)
        review_data["body"] = review.body
        review_data["state"] = review.state
        review_data["submitted_at"] = review.submitted_at
        return review_data
    
    @staticmethod
    def generate_pull_request_pandas_tables(repo, data_root_dir):
        """
        generate_pull_request_pandas_tables(repo, data_root_dir)

        Extracting the complete pull request data from a repository

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        bool
            Code runs without errors 
        
        Notes
        -----
            Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        pull_request_dir = Path(data_root_dir, AggPullRequest.PULL_REQUESTS_DIR)
        pull_requests = repo.get_pulls(state='all') 
        pull_request_list = list()
        pull_request_comment_list = list()
        pull_request_reaction_list = list()
        pull_request_review_list = list()
        pull_request_event_list = list()
        # pull request data
        for pull_request in pull_requests:
            pull_request_data = AggPullRequest.extract_pull_request_data(pull_request, data_root_dir)
            pull_request_list.append(pull_request_data)
            # pull request comment data
            for comment in pull_request.get_comments():
                pull_request_comment_data = Utility.extract_comment_data(comment, pull_request.id, "pull_request", data_root_dir)
                pull_request_comment_list.append(pull_request_comment_data)
                # pull request reaction data
                for reaction in comment.get_reactions():
                    reaction_data = Utility.extract_reaction_data(reaction,comment.id, "comment", data_root_dir)
                    pull_request_reaction_list.append(reaction_data)
            # pull request review data
            for review in pull_request.get_reviews():
                pull_request_review_data = AggPullRequest.extract_pull_request_review_data(review, pull_request.id, data_root_dir)
                pull_request_review_list.append(pull_request_review_data)
            # pull request issue comments data
            for comment in pull_request.get_issue_comments():
                pull_request_comment_data = Utility.extract_comment_data(comment, pull_request.id, "pull_request", data_root_dir)
                pull_request_comment_list.append(pull_request_comment_data)
                # pull request reaction data
                for reaction in comment.get_reactions():
                    reaction_data = Utility.extract_reaction_data(reaction,comment.id, "comment", data_root_dir)
                    pull_request_reaction_list.append(reaction_data)
            # pull request issue events
            for event in pull_request.get_issue_events():
                pull_request_event_data = Utility.extract_event_data(event, pull_request.id, "pull_request", data_root_dir)
                pull_request_event_list.append(pull_request_event_data)
        # Save lists
        Utility.save_list_to_pandas_table(pull_request_dir, AggPullRequest.PULL_REQUESTS, pull_request_list)
        Utility.save_list_to_pandas_table(pull_request_dir, AggPullRequest.PULL_REQUESTS_COMMENTS, pull_request_comment_list)
        Utility.save_list_to_pandas_table(pull_request_dir, AggPullRequest.PULL_REQUESTS_REACTIONS, pull_request_reaction_list)
        Utility.save_list_to_pandas_table(pull_request_dir, AggPullRequest.PULL_REQUESTS_REVIEWS, pull_request_review_list)
        Utility.save_list_to_pandas_table(pull_request_dir, AggPullRequest.PULL_REQUESTS_EVENTS, pull_request_event_list)
        return True
    
    @staticmethod
    def get_raw_pull_requests(data_root_dir, filename = PULL_REQUESTS):
        """
        get_raw_pull_requests(data_root_dir, filename)

        Get the genearted pandas table.

        Parameters
        ----------
        data_root_dir: str
            Path to the data folder of the repository.
        filename: str, default: PULL_REQUESTS
            A filename of PullRequests

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the pull request data

        """
        pull_request_dir = Path(data_root_dir, AggPullRequest.PULL_REQUESTS_DIR)
        pd_pull_requests_file = Path(pull_request_dir, filename)
        if pd_pull_requests_file.is_file():
            return pd.read_pickle(pd_pull_requests_file)
        else:
            return pd.DataFrame()
    
    class PullRequestData(dict):
        """
        Class extends a dict in order to restrict the pull request data set to defined keys.

        Attributes
        ----------
        KEYS: list
            List of allowed keys.
            
        Methods
        -------
            __init__(self)
                Set all keys in KEYS to None.
            __setitem__(self, key, val)
                Set Value if Key is in KEYS.
        
        """

        KEYS = [
            "id",
            "assignees",
            "assignees_count",
            "body",
            "title",
            "changed_files",
            "closed_at",
            "created_at",
            "deletions",
            "additions",
            "labels",
            "labels_count",
            "merged",
            "merged_at",
            "merged_by",
            "milestone_id",
            "state",
            "updated_at",
            "author",
            "comments_count",
            "issue_events_count",
            "reviews_count"
        ]
        
        def __init__(self):
            """
            __init__(self)

            Set all keys in KEYS to None.

            """

            for key in AggPullRequest.PullRequestData.KEYS:
                self[key] = None
        
        def __setitem__(self, key, val):
            """
            __setitem__(self, key, val)

            Set Value if Key is in KEYS.

            Parameters
            ----------
            key: str
                Key for dict
            val
                Value for dict
            """

            if key not in AggPullRequest.PullRequestData.KEYS:
                raise KeyError
            dict.__setitem__(self, key, val)

    class PullRequestReviewData(dict):
        """
        Class extends a dict in order to restrict the pull request review data set to defined keys.

        Attributes
        ----------
        KEYS: list
            List of allowed keys.
            
        Methods
        -------
            __init__(self)
                Set all keys in KEYS to None.
            __setitem__(self, key, val)
                Set Value if Key is in KEYS.
        
        """

        KEYS = [
            "pull_request_id",
            "id",
            "author",
            "body",
            "state",
            "submitted_at"
        ]
        
        def __init__(self):
            """
            __init__(self)

            Set all keys in KEYS to None.

            """

            for key in AggPullRequest.PullRequestReviewData.KEYS:
                self[key] = None
        
        def __setitem__(self, key, val):
            """
            __setitem__(self, key, val)

            Set Value if Key is in KEYS.

            Parameters
            ----------
            key: str
                Key for dict
            val
                Value for dict
            """

            if key not in AggPullRequest.PullRequestReviewData.KEYS:
                raise KeyError
            dict.__setitem__(self, key, val)