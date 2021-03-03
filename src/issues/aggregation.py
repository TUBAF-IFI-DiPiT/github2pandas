import pandas as pd
from pathlib import Path
import pickle
import enum

class RawIssuesFilenames(enum.Enum):
    PD_ISSUES = 1
    PD_ISSUES_COMMENTS = 2
    PD_ISSUES_EVENTS = 3
    PD_ISSUES_REACTIONS = 4

# https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html
def extract_user_data(author):
    return author.name

# https://pygithub.readthedocs.io/en/latest/github_objects/Issue.html
def extract_issue_data(issue):
    issue_data = dict()  
    issue_data["assignees_count"] = 0
    issue_data["assignees"] = ""
    for assignee in issue.assignees:
        issue_data["assignees_count"] += 1
        issue_data["assignees"] += extract_user_data(assignee) + "&"
    if len(issue_data["assignees"]) > 0:
        issue_data["assignees"] = issue_data["assignees"][:-1]
    issue_data["body"] = issue.body
    issue_data["closed_at"] = issue.closed_at
    if issue.closed_by:
        issue_data["closedBy"] = extract_user_data(issue.closed_by)
    issue_data["comments"] = issue.comments
    issue_data["created_at"] = issue.created_at
    issue_data["id"] = issue.id
    issue_data["labels_count"] = 0
    issue_data["labels"] = ""
    for label in issue.labels:
        issue_data["labels_count"] += 1
        issue_data["labels"] += issue.labels.name + "&"
    if len(issue_data["labels"]) > 0:
        issue_data["labels"] = issue_data["labels"][:-1]    
    if issue.milestone:
        issue_data["milestone_id"] = issue.milestone.id
    if issue.pull_request:
        issue_data["pull_request"] = True
    else:
        issue_data["pull_request"] = False
    issue_data["state"] = issue.state
    issue_data["title"] = issue.title
    issue_data["updated_at"] = issue.updated_at
    if issue.user:
        issue_data["author"] = extract_user_data(issue.user)
    issue_data["status"] = issue.state
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
    issue_comment_data["updated_at"] = comment.updated_at
    if comment.user:
        issue_comment_data["author"] = extract_user_data(comment.user)
    issue_comment_data["reactions"] = comment.get_reactions().totalCount
    return issue_comment_data

# https://pygithub.readthedocs.io/en/latest/github_objects/Reaction.html
def extract_reaction_data(reaction, comment_id = None, issue_id = None):
    reaction_data = dict() 
    if comment_id:
        reaction_data["comment_id"] = comment_id
    if issue_id:
        reaction_data["issue_id"] = issue_id
    reaction_data["content"] = reaction.content
    reaction_data["created_at"] = reaction.created_at
    reaction_data["id"] = reaction.id
    if reaction.user:
        reaction_data["author"] = extract_user_data(reaction.user)
    return reaction_data

# https://pygithub.readthedocs.io/en/latest/github_objects/IssueEvent.html
def extract_issue_event_data(event, issue_id):
    issue_event_data = dict()
    issue_event_data["issue_id"] = issue_id
    if event.actor:
        issue_event_data["author"] = extract_user_data(event.actor)
    issue_event_data["commit_id"] = event.commit_id
    issue_event_data["created_at"] = event.created_at
    issue_event_data["event"] = event.event
    issue_event_data["id"] = event.id
    issue_event_data["node_id"] = event.node_id
    if event.label:
        issue_event_data["label"] = event.label.name
    if event.assignee:
        issue_event_data["assignee"] = extract_user_data(event.assignee)
    if event.assigner:
        issue_event_data["assigner"] = extract_user_data(event.assigner)
    if event.review_requester:
        issue_event_data["review_requester"] = extract_user_data(event.review_requester)
    if event.requested_reviewer:
        issue_event_data["requested_reviewer"] = extract_user_data(event.requested_reviewer)
    return issue_event_data

def generate_pandas_tables(data_dir, git_repo_name, repo):
    data_dir_ = Path(data_dir, "Issues")
    issues = repo.get_issues(state="all") 
    issue_list = list()
    issue_comment_list = list()
    issue_event_list = list()
    issue_reaction_list = list()
    for issue in issues:
        # issue data
        issue_data = extract_issue_data(issue)
        issue_list.append(issue_data)
        for comment in issue.get_comments():
            # issue comment data
            issue_comment_data = extract_issue_comment_data(comment, issue.id)
            issue_comment_list.append(issue_comment_data)
            # issue comment reaction data
            for reaction in comment.get_reactions():
                reaction_data = extract_reaction_data(reaction,comment_id=comment.id)
                issue_reaction_list.append(reaction_data)
        # issue event data
        for event in issue.get_events():
            issue_event_data = extract_issue_event_data(event, issue.id)
            issue_event_list.append(issue_event_data)
        # issue reaction data
        for reaction in issue.get_reactions():
            issue_reaction_data = extract_reaction_data(reaction,issue_id=issue.id)
            issue_reaction_list.append(issue_reaction_data)    
    # Save lists
    save_list_to_raw_issues(data_dir, RawIssuesFilenames.PD_ISSUES, issue_list)
    save_list_to_raw_issues(data_dir, RawIssuesFilenames.PD_ISSUES_COMMENTS, issue_comment_list)
    save_list_to_raw_issues(data_dir, RawIssuesFilenames.PD_ISSUES_EVENTS, issue_event_list)
    save_list_to_raw_issues(data_dir, RawIssuesFilenames.PD_ISSUES_REACTIONS, issue_reaction_list)

def get_raw_issues(data_dir, raw_issue_filename = RawIssuesFilenames.PD_ISSUES):
    pd_issues_file = Path(data_dir, raw_issue_filename + ".p")
    if pd_issues_file.is_file():
        return pd.read_pickle(pd_issues_file)
    else:
        return pd.DataFrame()

def save_list_to_raw_issues(data_dir, raw_issue_filename, data_list):
    data_frame_ = pd.DataFrame(data_list)
    pd_file = Path(data_dir, raw_issue_filename.name)
    with open(pd_file, "wb") as f:
        pickle.dump(data_frame_, f)





