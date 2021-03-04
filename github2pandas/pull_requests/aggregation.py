import pandas as pd
from pathlib import Path
import pickle
import enum

from .. import utility

PULL_REQUESTS_DIR = "PullRequests"
class RawPullRequestsFilenames(enum.Enum):
    PD_PULL_REQUESTS = "pdPullRequests.p"
    PD_PULL_REQUESTS_COMMENTS = "pdPullRequestsComments.p"
    PD_PULL_REQUESTS_REACTIONS = "pdPullRequestsReactions.p"
    PD_PULL_REQUESTS_COMMITS = "pdPullRequestsCommits.p"
    PD_PULL_REQUESTS_FILES = "pdPullRequestsFiles.p"
    PD_PULL_REQUESTS_REVIEWS = "pdPullRequestsReviews.p"
    PD_PULL_REQUESTS_REVIEWS_REQUESTS = "pdPullRequestsReviewsRequests.p"

# https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html
def extract_pull_request_data(pull_request):
    pull_request_data = dict()
    pull_request_data["additions"] = pull_request.additions
    pull_request_data["assignees"], pull_request_data["assignees_count"] = utility.extract_assignees(pull_request)
    if pull_request.base:
        pull_request_data["base_label"] = pull_request.base.label
        pull_request_data["base_ref"] = pull_request.base.ref
        pull_request_data["base_sha"] = pull_request.base.label
        if pull_request.base.user:
            pull_request_data["base_author"] = utility.extract_user_data(pull_request.base.user)    
    pull_request_data["body"] = pull_request.body
    pull_request_data["changed_files"] = pull_request.changed_files
    pull_request_data["closed_at"] = pull_request.closed_at
    pull_request_data["created_at"] = pull_request.created_at
    pull_request_data["deletions"] = pull_request.deletions
    pull_request_data["draft"] = pull_request.draft
    pull_request_data["id"] = pull_request.id
    pull_request_data["deletions"] = pull_request.deletions
    pull_request_data["labels"], pull_request_data["labels_count"] = utility.extract_labels(pull_request)
    pull_request_data["mergeable"] = pull_request.mergeable
    pull_request_data["mergeable_state"] = pull_request.mergeable_state
    pull_request_data["merged"] = pull_request.merged
    pull_request_data["merged_at"] = pull_request.merged_at
    if pull_request.base.merged_by:
        pull_request_data["merged_by"] = utility.extract_user_data(pull_request.merged_by)
    if pull_request.milestone:
        issue_data["milestone_id"] = pull_request.milestone.id
    pull_request_data["number"] = pull_request.number
    pull_request_data["rebaseable"] = pull_request.rebaseable
    pull_request_data["review_comments"] = pull_request.review_comments
    pull_request_data["state"] = pull_request.state
    pull_request_data["title"] = pull_request.title
    pull_request_data["updated_at"] = pull_request.updated_at
    if pull_request.base.user:
        pull_request_data["author"] = utility.extract_user_data(pull_request.user)

    pull_request_data["comments_count"] = pull_request.get_comments().totalCount
    pull_request_data["review_comments_count"] = pull_request.get_review_comments().totalCount
    pull_request_data["commits_count"] = pull_request.get_commits().totalCount
    pull_request_data["files_count"] = pull_request.get_files().totalCount
    pull_request_data["issue_comments_count"] = pull_request.get_issue_comments().totalCount
    pull_request_data["issue_events_count"] = pull_request.get_issue_events().totalCount
    pull_request_data["reviews_count"] = pull_request.get_reviews().totalCount
    pull_request_data["review_requests_count"] = pull_request.get_review_requests().totalCount

    return pull_request_data

# https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html
def extract_pull_request_comment_data(comment, pull_request_id, review):
    comment_data = dict()
    comment_data["pull_request_id"] = pull_request_id
    comment_data["review"] = review
    comment_data["body"] = comment.body
    comment_data["commit_id"] = comment.commit_id
    comment_data["created_at"] = comment.created_at
    comment_data["diff_hunk"] = comment.diff_hunk
    comment_data["id"] = comment.id
    comment_data["in_reply_to_id"] = comment.in_reply_to_id
    comment_data["original_commit_id"] = comment.original_commit_id
    comment_data["original_position"] = comment.original_position
    comment_data["path"] = comment.path
    comment_data["position"] = comment.position
    comment_data["updated_at"] = comment.updated_at
    if comment.user:
        comment_data["author"] = utility.extract_user_data(comment.user)
    return comment_data

# https://pygithub.readthedocs.io/en/latest/github_objects/Commit.html
def extract_commit_data(commit, pull_request_id):
    commit_data = dict()
    commit_data["pull_request_id"] = pull_request_id
    commit_data["sha"] = commit.sha
    return commit_data

# https://pygithub.readthedocs.io/en/latest/github_objects/File.html
def extract_file_data(file, pull_request_id):
    file_data = dict()
    file_data["pull_request_id"] = pull_request_id
    file_data["additions"] = file.additions
    file_data["changes"] = file.changes
    file_data["deletions"] = file.deletions
    file_data["filename"] = file.filename
    file_data["patch"] = file.patch
    file_data["previous_filename"] = file.previous_filename
    file_data["sha"] = file.sha
    file_data["status"] = file.status
    return file_data
# https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html#github.PullRequestReview.PullRequestReview
def extract_pull_request_review_data(review, pull_request_id):
    review_data = dict()
    review_data["pull_request_id"] = pull_request_id
    review_data["id"] = review.additions
    if review.user:
        review_data["author"] = utility.extract_user_data(review.user)
    review_data["body"] = review.body
    review_data["commit_id"] = review.commit_id
    review_data["state"] = review.state
    review_data["submitted_at"] = review.submitted_at
    return review_data
def generate_pandas_tables(data_dir, git_repo_name, repo):
    data_dir_ = Path(data_dir, PULL_REQUESTS_DIR)
    pull_requests = repo.get_pulls() 
    pull_request_list = list()
    pull_request_comment_list = list()
    pull_request_reaction_list = list()
    pull_request_commit_list = list()
    pull_request_file_list = list()
    pull_request_review_list = list()
    pull_request_review_request_list = list()
    for pull_request in pull_requests:
        pull_request_data = extract_pull_request_data(pull_request)
        pull_request_list.append(pull_request_data)
        # pull request comment data
        for comment in pull_request.get_comments():
            pull_request_comment_data = extract_pull_request_comment_data(comment, pull_request.id, False)
            pull_request_comments_list.append(pull_request_comment_data)
            # pull request reaction data
            for reaction in comment.get_reactions():
                reaction_data = utility.extract_reaction_data(reaction,comment.id, "comment")
                pull_request_reaction_list.append(reaction_data)
        # pull request review comment data
        for review_comment in pull_request.get_review_comments():
            pull_request_review_comment_data = extract_pull_request_comment_data(review_comment, pull_request.id, True)
            pull_request_comments_list.append(pull_request_review_comment_data)
            # pull request reaction data
            for reaction in review_comment.get_reactions():
                reaction_data = utility.extract_reaction_data(reaction,review_comment.id, "review_comment")
                pull_request_reaction_list.append(reaction_data)
        # pull request commit data
        for commit in pull_request.get_commits():
            commit_data = extract_commit_data(commit, pull_request.id)
            pull_request_commit_list.append(commit_data)
        # pull request file data
        for file in pull_request.get_files():
            file_data = extract_file_data(file, pull_request.id)
            pull_request_file_list.append(file_data)
        # pull request review data
        for review in pull_request.get_reviews():
            pull_request_review_data = extract_pull_request_review_data(review, pull_request.id)
            pull_request_review_list.append(pull_request_review_data)
        # pull review request review data (all requested reviewer)
        for review_request_user, review_request_team in pull_request.get_review_requests():
            review_request_user_data = dict()
            review_request_user_data["author"] = utility.extract_user_data(review_request_user)
            review_request_user_data["pull_request_id"] = pull_request_id
            pull_request_review_request_list.append(review_request_user_data)
        # left out for now. 
        # issue_comments
        # issue_events

    # Save lists
    utility.save_list_to_pandas_table(data_dir_, RawPullRequestsFilenames.PD_PULL_REQUESTS.value, pull_request_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequestsFilenames.PD_PULL_REQUESTS_COMMENTS.value, pull_request_comment_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequestsFilenames.PD_PULL_REQUESTS_REACTIONS.value, pull_request_reaction_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequestsFilenames.PD_PULL_REQUESTS_COMMITS.value, pull_request_commit_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequestsFilenames.PD_PULL_REQUESTS_FILES.value, pull_request_file_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequestsFilenames.PD_PULL_REQUESTS_REVIEWS.value, pull_request_review_list)
    utility.save_list_to_pandas_table(data_dir_, RawPullRequestsFilenames.PD_PULL_REQUESTS_REVIEWS_REQUESTS.value, pull_request_review_request_list)
    return True