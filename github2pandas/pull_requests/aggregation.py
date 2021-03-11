import pandas as pd
from pathlib import Path
import pickle
import enum
import os
import shutil
from .. import utility
from ..issues.aggregation import extract_issue_event_data

class RawPullRequests(enum.Enum):
    """
    Includes nessesarry folders and filenames

    Attributes
    ----------
    PULL_REQUESTS_DIR : str
        Pull request dir where all files are saved in.
    PD_PULL_REQUESTS : str
        Pandas table for raw pull request data.
    PD_PULL_REQUESTS_COMMENTS : str
        Pandas table for raw comments data in pull requests.
    PD_PULL_REQUESTS_REACTIONS : str
        Pandas table for raw reactions on comments data in pull requests.
    PD_PULL_REQUESTS_REVIEWS : str
        Pandas table for raw reviews data in pull requests.
    PD_PULL_REQUESTS_EVENTS : str
        Pandas table for raw events data in pull requests.

    """
    PULL_REQUESTS_DIR = "PullRequests"
    PD_PULL_REQUESTS = "pdPullRequests.p"
    PD_PULL_REQUESTS_COMMENTS = "pdPullRequestsComments.p"
    PD_PULL_REQUESTS_REACTIONS = "pdPullRequestsReactions.p"
    PD_PULL_REQUESTS_REVIEWS = "pdPullRequestsReviews.p"
    PD_PULL_REQUESTS_EVENTS = "pdPullRequestsEvents.p"

def extract_pull_request_data(pull_request):
    """
    extract_pull_request_data(pull_request)

    Extracting general pull request data.

    Parameters
    ----------
    pull_request: PullRequest
        PullRequest object from pygithub.

    Returns
    -------
    dict
        Dictionary with the extracted data.

    Notes
    -----
        PullRequest object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html

    """
    pull_request_data = dict()
    pull_request_data["id"] = pull_request.id
    pull_request_data["assignees"] = utility.extract_assignees(pull_request.assignees)
    pull_request_data["assignees_count"] = len(pull_request.assignees)  
    pull_request_data["body"] = pull_request.body
    pull_request_data["title"] = pull_request.title
    pull_request_data["changed_files"] = pull_request.changed_files
    pull_request_data["closed_at"] = pull_request.closed_at
    pull_request_data["created_at"] = pull_request.created_at
    pull_request_data["deletions"] = pull_request.deletions
    pull_request_data["additions"] = pull_request.additions
    pull_request_data["deletions"] = pull_request.deletions
    pull_request_data["labels"] = utility.extract_labels(pull_request.labels)
    pull_request_data["labels_count"] = len(pull_request.labels)
    pull_request_data["merged"] = pull_request.merged
    pull_request_data["merged_at"] = pull_request.merged_at
    pull_request_data["merged_by"] = utility.extract_user_data(pull_request.merged_by)
    if pull_request.milestone:
        issue_data["milestone_id"] = pull_request.milestone.id
    pull_request_data["state"] = pull_request.state
    pull_request_data["updated_at"] = pull_request.updated_at
    pull_request_data["author"] = utility.extract_user_data(pull_request.user)
    pull_request_data["comments_count"] = pull_request.get_comments().totalCount + pull_request.get_issue_comments().totalCount
    pull_request_data["issue_events_count"] = pull_request.get_issue_events().totalCount
    pull_request_data["reviews_count"] = pull_request.get_reviews().totalCount
    return pull_request_data

def extract_pull_request_comment_data(comment, pull_request_id):
    """
    extract_pull_request_comment_data(comment, pull_request_id)

    Extracting general comment data from a pull request.

    Parameters
    ----------
    comment: PullRequestComment
        PullRequestComment object from pygithub.
    pull_request_id: int
        Pull request id as foreign key.

    Returns
    -------
    dict
        Dictionary with the extracted data.

    Notes
    -----
        PullRequestComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html

    """
    comment_data = dict()
    comment_data["pull_request_id"] = pull_request_id
    comment_data["body"] = comment.body
    comment_data["created_at"] = comment.created_at
    comment_data["id"] = comment.id
    comment_data["author"] = utility.extract_user_data(comment.user)
    comment_data["reactions_count"] = comment.get_reactions().totalCount
    return comment_data

def extract_pull_request_review_data(review, pull_request_id):
    """
    extract_pull_request_review_data(review, pull_request_id)

    Extracting general review data from a pull request.

    Parameters
    ----------
    review: PullRequestReview
        PullRequestReview object from pygithub.
    pull_request_id: int
        Pull request id as foreign key.

    Returns
    -------
    dict
        Dictionary with the extracted data.

    Notes
    -----
        PullRequestReview object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html

    """
    review_data = dict()
    review_data["pull_request_id"] = pull_request_id
    review_data["id"] = review.id
    review_data["author"] = utility.extract_user_data(review.user)
    review_data["body"] = review.body
    review_data["state"] = review.state
    review_data["submitted_at"] = review.submitted_at
    return review_data

def generate_pandas_tables(data_dir, repo):
    """
    generate_pandas_tables(data_dir, repo)

    Extracting the complete pull request data from a repository

    Parameters
    ----------
    data_dir: str
        Path to the data folder of the repository
    repo: Repository
        Repository object from pygithub.

    Returns
    -------
    bool
        Code runs without errors 
        
    Notes
    -----
        Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

    """
    data_dir_ = Path(data_dir, RawPullRequests.PULL_REQUESTS_DIR)
    pull_requests = repo.get_pulls(state='all') 
    pull_request_list = list()
    pull_request_comment_list = list()
    pull_request_reaction_list = list()
    pull_request_review_list = list()
    pull_request_event_list = list()
    # pull request data
    for pull_request in pull_requests:
        pull_request_data = extract_pull_request_data(pull_request)
        pull_request_list.append(pull_request_data)
        # pull request comment data
        for comment in pull_request.get_comments():
            pull_request_comment_data = extract_pull_request_comment_data(comment, pull_request.id)
            pull_request_comment_list.append(pull_request_comment_data)
            # pull request reaction data
            for reaction in comment.get_reactions():
                reaction_data = utility.extract_reaction_data(reaction,comment.id, "comment")
                pull_request_reaction_list.append(reaction_data)
        # pull request review data
        for review in pull_request.get_reviews():
            pull_request_review_data = extract_pull_request_review_data(review, pull_request.id)
            pull_request_review_list.append(pull_request_review_data)
        # pull request issue comments data
        for comment in pull_request.get_issue_comments():
            pull_request_comment_data = extract_pull_request_comment_data(comment, pull_request.id)
            pull_request_comment_list.append(pull_request_comment_data)
            # pull request reaction data
            for reaction in comment.get_reactions():
                reaction_data = utility.extract_reaction_data(reaction,comment.id, "comment")
                pull_request_reaction_list.append(reaction_data)
        # pull request issue events
        for event in pull_request.get_issue_events():
            pull_request_event_data = extract_issue_event_data(event, pull_request.id)
            pull_request_event_list.append(pull_request_event_data)
    # Save lists
    if os.path.isdir(data_dir_):
        shutil.rmtree(data_dir_)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequests.PD_PULL_REQUESTS.value, pull_request_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequests.PD_PULL_REQUESTS_COMMENTS.value, pull_request_comment_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequests.PD_PULL_REQUESTS_REACTIONS.value, pull_request_reaction_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequests.PD_PULL_REQUESTS_REVIEWS.value, pull_request_review_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequests.PD_PULL_REQUESTS_EVENTS.value, pull_request_event_list)
    return True

def get_raw_pull_requests(data_dir, raw_pull_request_filename = RawPullRequests.PD_PULL_REQUESTS):
    """
    get_raw_pull_requests(data_dir, raw_pull_request_filename)

    Get the genearted pandas table.

    Parameters
    ----------
    data_dir: str
        Path to the data folder of the repository.
    raw_pull_request_filename: RawPullRequests, default: RawPullRequests.PD_PULL_REQUESTS
        A filename of RawPullRequests.

    Returns
    -------
    DataFrame
        Pandas DataFrame which includes the data

    """
    data_dir_ = Path(data_dir, RawPullRequests.PULL_REQUESTS_DIR)
    pd_pull_requests_file = Path(data_dir_, raw_pull_request_filename.value)
    if pd_pull_requests_file.is_file():
        return pd.read_pickle(pd_pull_requests_file)
    else:
        return pd.DataFrame()