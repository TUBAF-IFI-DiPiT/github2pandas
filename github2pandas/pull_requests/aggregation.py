import pandas as pd
from pathlib import Path
import pickle
import enum
import os
import shutil
from .. import utility
from ..issues.aggregation import extract_issue_event_data

PD_PULL_REQUESTS = "pdPullRequests.p"

# https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html
def extract_pull_request_data(pull_request):
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

# https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html
def extract_pull_request_comment_data(comment, comment_data):
    comment_data["comment_body"] = comment.body
    comment_data["comment_created_at"] = comment.created_at
    comment_data["comment_id"] = comment.id
    comment_data["comment_author"] = utility.extract_user_data(comment.user)
    comment_data["comment_reactions_count"] = comment.get_reactions().totalCount
    return comment_data

# https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html
def extract_pull_request_review_data(review, review_data):
    review_data["review_id"] = review.id
    review_data["review_author"] = utility.extract_user_data(review.user)
    review_data["review_body"] = review.body
    review_data["review_state"] = review.state
    review_data["review_submitted_at"] = review.submitted_at
    return review_data

def generate_pandas_tables(data_dir, git_repo_name, repo):
    pull_requests = repo.get_pulls(state='all') 
    pull_request_list = list()
    pull_request_comment_list = list()
    pull_request_reaction_list = list()
    pull_request_review_list = list()
    pull_request_event_list = list()
    # pull request data
    for pull_request in pull_requests:
        pull_request_data = extract_pull_request_data(pull_request)
        list_len = len(pull_request_list)
        # pull request comment data
        for comment in pull_request.get_comments():
            comment_data = extract_pull_request_comment_data(comment, pull_request_data.copy())
            # pull request reaction data
            for reaction in comment.get_reactions():
                reaction_data = utility.extract_reaction_data(reaction, comment_data.copy())
                pull_request_list.append(reaction_data)
            if comment.get_reactions().totalCount == 0:
                pull_request_list.append(comment_data)
        # pull request review data
        for review in pull_request.get_reviews():
            review_data = extract_pull_request_review_data(review, pull_request_data.copy())
            pull_request_list.append(review_data)
        # pull request issue comments data
        for comment in pull_request.get_issue_comments():
            comment_data = extract_pull_request_comment_data(comment, pull_request_data.copy())
            # pull request reaction data
            for reaction in comment.get_reactions():
                reaction_data = utility.extract_reaction_data(reaction, comment_data.copy())
                pull_request_list.append(reaction_data)
            if comment.get_reactions().totalCount == 0:
                pull_request_list.append(comment_data)
        # pull request issue events
        for event in pull_request.get_issue_events():
            event_data = extract_issue_event_data(event, pull_request_data.copy())
            pull_request_list.append(event_data)
        if list_len == len(pull_request_list):
            pull_request_list.append(pull_request_data)
    utility.save_list_to_pandas_table(data_dir, PD_PULL_REQUESTS, pull_request_list)
    return True

def get_raw_pull_requests(data_dir):
    pd_pull_requests_file = Path(data_dir_, PD_PULL_REQUESTS)
    if pd_pull_requests_file.is_file():
        return pd.read_pickle(pd_pull_requests_file)
    else:
        return pd.DataFrame()