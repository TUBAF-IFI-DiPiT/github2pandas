import pandas as pd
from pathlib import Path
import pickle
import enum
from .. import utility

ISSUES_DIR = "Issues"
class RawIssuesFilenames(enum.Enum):
    PD_ISSUES = "pdIssues.p"
    PD_ISSUES_COMMENTS = "pdIssuesComments.p"
    PD_ISSUES_EVENTS = "pdIssuesEvents.p"
    PD_ISSUES_REACTIONS = "pdIssuesReactions.p"

# https://pygithub.readthedocs.io/en/latest/github_objects/Issue.html
def extract_issue_data(issue):
    issue_data = dict()  
    issue_data["assignees"]  = utility.extract_assignees(issue.assignees)
    issue_data["assignees_count"] = len(issue.assignees)
    issue_data["body"] = issue.body
    issue_data["closed_at"] = issue.closed_at
    issue_data["closedBy"] = utility.extract_user_data(issue.closed_by)
    issue_data["created_at"] = issue.created_at
    issue_data["id"] = issue.id
    issue_data["labels"]  = utility.extract_labels(issue.labels)
    issue_data["labels_count"] = len(issue.labels)
    if issue.milestone:
        issue_data["milestone_id"] = issue.milestone.id
    issue_data["state"] = issue.state
    issue_data["title"] = issue.title
    issue_data["updated_at"] = issue.updated_at
    issue_data["author"] = utility.extract_user_data(issue.user)
    issue_data["comments_count"] = issue.get_comments().totalCount
    issue_data["event_count"] = issue.get_events().totalCount
    issue_data["reaction_count"] = issue.get_reactions().totalCount
    return issue_data

# https://pygithub.readthedocs.io/en/latest/github_objects/IssueComment.html
def extract_issue_comment_data(comment, issue_id):
    issue_comment_data = dict()  
    issue_comment_data["issue_id"] = issue_id
    issue_comment_data["body"] = comment.body
    issue_comment_data["created_at"] = comment.created_at
    issue_comment_data["id"] = comment.id
    issue_comment_data["author"] = utility.extract_user_data(comment.user)
    issue_comment_data["reactions"] = comment.get_reactions().totalCount
    return issue_comment_data

# https://pygithub.readthedocs.io/en/latest/github_objects/IssueEvent.html
def extract_issue_event_data(event, issue_id):
    issue_event_data = dict()
    issue_event_data["issue_id"] = issue_id
    issue_event_data["author"] = utility.extract_user_data(event.actor)
    issue_event_data["commit_id"] = event.commit_id
    issue_event_data["created_at"] = event.created_at
    issue_event_data["event"] = event.event
    issue_event_data["id"] = event.id
    if event.label:
        issue_event_data["label"] = event.label.name
    issue_event_data["assignee"] = utility.extract_user_data(event.assignee)
    issue_event_data["assigner"] = utility.extract_user_data(event.assigner)
    return issue_event_data

def generate_pandas_tables(data_dir, git_repo_name, repo):
    data_dir_ = Path(data_dir, ISSUES_DIR)
    issues = repo.get_issues(state='all') 
    issue_list = list()
    issue_comment_list = list()
    issue_event_list = list()
    issue_reaction_list = list()
    for issue in issues:
        # remove pull_requests from issues
        if not issue.pull_request:
            # issue data
            issue_data = extract_issue_data(issue)
            issue_list.append(issue_data)
            # issue comment data
            for comment in issue.get_comments():
                issue_comment_data = extract_issue_comment_data(comment, issue.id)
                issue_comment_list.append(issue_comment_data)
                # issue comment reaction data
                for reaction in comment.get_reactions():
                    reaction_data = utility.extract_reaction_data(reaction,comment.id,"comment")
                    issue_reaction_list.append(reaction_data)
            # issue event data
            for event in issue.get_events():
                issue_event_data = extract_issue_event_data(event, issue.id)
                issue_event_list.append(issue_event_data)
            # issue reaction data
            for reaction in issue.get_reactions():
                issue_reaction_data = utility.extract_reaction_data(reaction,issue.id, "issue")
                issue_reaction_list.append(issue_reaction_data)    
    # Save lists
    utility.save_list_to_pandas_table(data_dir_, RawIssuesFilenames.PD_ISSUES.value, issue_list)
    utility.save_list_to_pandas_table(data_dir_, RawIssuesFilenames.PD_ISSUES_COMMENTS.value, issue_comment_list)
    utility.save_list_to_pandas_table(data_dir_, RawIssuesFilenames.PD_ISSUES_EVENTS.value, issue_event_list)
    utility.save_list_to_pandas_table(data_dir_, RawIssuesFilenames.PD_ISSUES_REACTIONS.value, issue_reaction_list)
    return True

def get_raw_issues(data_dir, raw_issue_filename = RawIssuesFilenames.PD_ISSUES.value):
    pd_issues_file = Path(data_dir, raw_issue_filename)
    if pd_issues_file.is_file():
        return pd.read_pickle(pd_issues_file)
    else:
        return pd.DataFrame()



