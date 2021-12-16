import pandas as pd
from pathlib import Path
from github import GithubObject
from github.Repository import Repository as GitHubRepository
from github.Issue import Issue as GitHubIssue
from github.IssueComment import IssueComment as GitHubIssueComment
from github.IssueEvent import IssueEvent as GitHubIssueEvent
from github.Reaction import Reaction as GitHubReaction
from .utility import Utility

class Issues():
    """
    Class to aggregate Issues

    Attributes
    ----------
    ISSUES_DIR : str
        Issues dir where all files are saved in.
    ISSUES : str
        Pandas table file for issues data.
    ISSUES_COMMENTS : str
        Pandas table file for comments data in issues.
    ISSUES_REACTIONS : str
        Pandas table file for reactions data in issues.
    ISSUES_EVENTS : str
        Pandas table file for reviews data in issues.

    Methods
    -------
    extract_issue_data(issue, users_ids, data_root_dir)
        Extracting general issue data.
    generate_issue_pandas_tables(repo, data_root_dir, reactions=False, check_for_updates=True)
        Extracting the complete issue data from a repository.
    get_issues(data_root_dir, filename=ISSUES)
        Get a genearted pandas table.
    
    """
    ISSUES_DIR = "Issues"
    ISSUES = "pdIssues.p"
    ISSUES_COMMENTS = "pdIssuesComments.p"
    ISSUES_REACTIONS = "pdIssuesReactions.p"
    ISSUES_EVENTS = "pdIssuesEvents.p"

    def __init__(self, repo:GitHubRepository, data_root_dir:Path, github_token:str, request_maximum:int = 40000) -> None:
        self.repo = repo
        self.data_root_dir = data_root_dir
        self.github_token = github_token
        self.issues_dir = Path(data_root_dir, Issues.ISSUES_DIR)
        self.users_ids = Utility.get_users_ids(data_root_dir)

        self.request_maximum = request_maximum
        self.issue_list = []
        self.issue_comment_list = []
        self.issue_event_list = []
        self.issue_reaction_list = []

    def generate_pandas_tables(self, extract_reactions:bool = False, check_for_updates:bool = False):
        """
        generate_issue_pandas_tables(repo, data_root_dir, reactions=False, check_for_updates=False)

        Extracting the complete issue data from a repository.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        data_root_dir : str
            Data root directory for the repository.
        reactions : bool, default=False
            If reactions should also be exracted. The extraction of all reactions increases significantly the aggregation speed.
        check_for_updates : bool, default=False
            Check first if there are any new issues information.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html
        
        """
        issues = Utility.save_api_call(self.repo.get_issues, self.github_token, state='all')
        if check_for_updates:
            old_issues = Issues.get_issues(self.data_root_dir)
            if not Utility.check_for_updates_paginated(issues, old_issues):
                return

        comments = Utility.save_api_call(self.repo.get_issues_comments, self.github_token)
        comments_overflow = False
        if comments.totalCount == self.request_maximum:
            comments_overflow = True
        events = Utility.save_api_call(self.repo.get_issues_events, self.github_token)
        events_overflow = False
        if events.totalCount == self.request_maximum:
            events_overflow = True

        print(f"Issues: {issues.totalCount}")
        print(f"Issues comments {comments.totalCount}")
        print(f"Issues events {events.totalCount}")

        self.users_ids = Utility.get_users_ids(self.data_root_dir)
        #issue data
        while True:
            for i in range(issues.totalCount):
                issue = Utility.get_save_api_data(issues, i, self.github_token)
                issue_data = self.extract_issue_data(issue)
                self.issue_list.append(issue_data)
                # reaction data
                if extract_reactions:
                    self.extract_issue_reactions(issue.get_reactions, issue.id, "issue")
                # comment data
                if comments_overflow:
                    self.extract_issue_comments(issue.get_comments, extract_reactions)
                # events data
                if events_overflow:
                    self.extract_issue_events(issue.get_events, issue_id=issue.id)
            if issues.totalCount == self.request_maximum:
                issues = Utility.save_api_call(self.repo.get_issues, self.github_token, state='all', since=issue_data["created_at"])
            else:
                break
        
        # issue comment data
        if not comments_overflow:
            self.extract_issue_comments(self.repo.get_issues_comments, extract_reactions)
        # issue event data
        if not comments_overflow:
            self.extract_issue_events(self.repo.get_issues_events)
        # Save lists
        Utility.save_list_to_pandas_table(self.issues_dir, Issues.ISSUES, self.issue_list)
        Utility.save_list_to_pandas_table(self.issues_dir, Issues.ISSUES_COMMENTS, self.issue_comment_list)
        Utility.save_list_to_pandas_table(self.issues_dir, Issues.ISSUES_EVENTS, self.issue_event_list)
        if extract_reactions:
            Utility.save_list_to_pandas_table(self.issues_dir, Issues.ISSUES_REACTIONS, self.issue_reaction_list)
    
    def extract_issue_data(self, issue:GitHubIssue):
        """
        extract_issue_data(issue, users_ids, data_root_dir)

        Extracting general issue data.

        Parameters
        ----------
        issue : Issue
            Issue object from pygithub.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Data root directory for the repository.

        Returns
        -------
        dict
            Dictionary with the extracted general issue data.

        Notes
        -----
            PyGithub Issue object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Issue.html

        """

        issue_data = {}
        # assignee ?
        issue_data["assignees"]  = Utility.extract_assignees(issue.assignees, self.users_ids, self.data_root_dir)
        issue_data["body"] = issue.body
        issue_data["closed_at"] = issue.closed_at
        if not issue._closed_by == GithubObject.NotSet:
            issue_data["closed_by"] = Utility.extract_user_data(issue.closed_by, self.users_ids, self.data_root_dir)
        issue_data["comments"] = issue.comments
        issue_data["created_at"] = issue.created_at
        issue_data["id"] = issue.id
        issue_data["labels"]  = Utility.extract_labels(issue.labels)
        issue_data["last_modified"] = issue.comments
        issue_data["locked"] = issue.comments
        # milestone ?
        issue_data["number"] = issue.number
        issue_data["state"] = issue.state
        issue_data["title"] = issue.title
        issue_data["updated_at"] = issue.updated_at
        issue_data["url"] = issue.url
        if not issue._user == GithubObject.NotSet:
            issue_data["author"] = Utility.extract_user_data(issue.user, self.users_ids, self.data_root_dir)
        if issue._pull_request == GithubObject.NotSet:
            issue_data["is_pull_request"] = False
        else:
            issue_data["is_pull_request"] = True
        return issue_data

    def extract_issue_reactions(self, extract_function, parent_id:int, parent_name:str):
        reactions = Utility.save_api_call(extract_function, self.github_token)
        for i in range(reactions.totalCount):
            reaction = Utility.get_save_api_data(reactions, i, self.github_token)
            reaction_data = Utility.save_api_call(self.extract_reaction_data, self.github_token, reaction, parent_id, parent_name)
            self.issue_reaction_list.append(reaction_data) 

    def extract_reaction_data(self, reaction:GitHubReaction, parent_id:int, parent_name:str):
        """
        extract_reaction_data(reaction, parent_id, parent_name, users_ids, data_root_dir)

        Extracting general reaction data.

        Parameters
        ----------
        reaction : Reaction
            Reaction object from pygithub.
        parent_id : int
            Id from parent as foreign key.
        parent_name : str
            Name of the parent.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Repo dir of the project.

        Returns
        -------
        ReactionData
            Dictionary with the extracted data.

        Notes
        -----
            Reaction object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Reaction.html

        """
        reaction_data = {} 
        reaction_data[parent_name + "_id"] = parent_id
        reaction_data["content"] = reaction.content
        reaction_data["created_at"] = reaction.created_at
        reaction_data["id"] = reaction.id
        if not reaction._user == GithubObject.NotSet:
            reaction_data["author"] = Utility.extract_user_data(reaction.user, self.users_ids, self.data_root_dir)
        return reaction_data

    def extract_issue_comments(self, extract_function, extract_reactions:bool):
        comments = Utility.save_api_call(extract_function, self.github_token)
        for i in range(comments.totalCount):
            comment = Utility.get_save_api_data(comments, i, self.github_token)
            issue_comment_data = Utility.save_api_call(self.extract_issue_comment_data, self.github_token, comment)
            self.issue_comment_list.append(issue_comment_data)
            # issue comment reaction data
            if extract_reactions:
                Issues.extract_issue_reactions(
                    comment.get_reactions,
                    comment.id,
                    "comment")

    def extract_issue_comment_data(self, issue_comment:GitHubIssueComment):
        """
        extract_comment_data(comment, parent_id, parent_name, users_ids, data_root_dir)

        Extracting general comment data from a pull request or issue.

        Parameters
        ----------
        comment : github_object 
            PullRequestComment or IssueComment object from pygithub.
        parent_id : int
            Id from parent as foreign key.
        parent_name : str
            Name of the parent.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Repo dir of the project.

        Returns
        -------
        CommentData
            Dictionary with the extracted data.

        Notes
        -----
            IssueComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueComment.html

        """
        issue_comment_data = {}
        issue_comment_data["body"] = issue_comment.body
        issue_comment_data["created_at"] = issue_comment.created_at
        issue_comment_data["id"] = issue_comment.id
        issue_comment_data["issue_url"] = issue_comment.issue_url
        issue_comment_data["updated_at"] = issue_comment.updated_at
        if not issue_comment._user == GithubObject.NotSet:
            issue_comment_data["author"] = Utility.extract_user_data(issue_comment.user, self.users_ids, self.data_root_dir)
        return issue_comment_data

    def extract_issue_events(self, extract_function, issue_id:int=None):
        events = Utility.save_api_call(extract_function, self.github_token)
        for i in range(events.totalCount):
            event = Utility.get_save_api_data(events, i, self.github_token)
            issue_event_data = Utility.save_api_call(self.extract_issue_event_data, self.github_token, event, issue_id=issue_id)
            self.issue_event_list.append(issue_event_data)

    def extract_issue_event_data(self, issue_event:GitHubIssueEvent, issue_id:int=None):
        """
        extract_event_data(event, parent_id, parent_name, users_ids, data_root_dir)

        Extracting general event data from a issue or pull request.

        Parameters
        ----------
        even t: IssueEvent
            IssueEvent object from pygithub.
        parent_id : int
            Id from parent as foreign key.
        parent_name : str
            Name of the parent.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Repo dir of the project.

        Returns
        -------
        EventData
            Dictionary with the extracted data.

        Notes
        -----
            IssueEvent object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueEvent.html

        """
        issue_event_data = {}
        if not issue_event._actor == GithubObject.NotSet:
            issue_event_data["author"] = Utility.extract_user_data(issue_event.actor, self.users_ids, self.data_root_dir)
        if not issue_event._assignee == GithubObject.NotSet:
            issue_event_data["assignee"] = Utility.extract_user_data(issue_event.assignee, self.users_ids, self.data_root_dir)
        if not issue_event._assigner == GithubObject.NotSet:
            issue_event_data["assigner"] = Utility.extract_user_data(issue_event.assigner, self.users_ids, self.data_root_dir)
        issue_event_data["commit_sha"] = issue_event.commit_id
        issue_event_data["created_at"] = issue_event.created_at
        # dismissed_review ?
        issue_event_data["event"] = issue_event.event
        issue_event_data["id"] = issue_event.id
        if issue_id is None:
            issue_event_data["issue_id"] = issue_event.issue.id
        else:
            issue_event_data["issue_id"] = issue_id
        if not issue_event._label == GithubObject.NotSet:
            issue_event_data["label"] = issue_event.label.name
        issue_event_data["last_modified"] = issue_event.last_modified
        # lock_reason ?
        # milestone ?
        # node_id ?
        # rename ?
        # requested_reviewer ?
        # review_requesters ?
        return issue_event_data
    
    @staticmethod
    def get_pandas_table(data_root_dir:Path, filename:str=ISSUES):
        """
        get_issues(data_root_dir, filename=ISSUES)

        Get a genearted pandas table.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        filename : str, default=ISSUES
            Pandas table file for issues or comments or reactions or events data.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can include the desired data

        """
        
        pd_issues_file = Path(data_root_dir, Issues.ISSUES_DIR, filename)
        if pd_issues_file.is_file():
            return pd.read_pickle(pd_issues_file)
        else:
            return pd.DataFrame()
