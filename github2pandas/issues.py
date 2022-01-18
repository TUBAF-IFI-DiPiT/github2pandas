import pandas as pd
from pathlib import Path
from github import GithubObject
from github.MainClass import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository as GitHubRepository
from github.Issue import Issue as GitHubIssue
from github.IssueComment import IssueComment as GitHubIssueComment
from github.IssueEvent import IssueEvent as GitHubIssueEvent
from github.Reaction import Reaction as GitHubReaction
from github2pandas.core import Core
from github2pandas.utility import progress_bar, copy_valid_params
class Issues(Core):
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
    issues_df : DataFrame
        Pandas DataFrame object with general issues data.
    issues_comments_df : DataFrame
        Pandas DataFrame object with issues comments data.
    issues_events_df : DataFrame
        Pandas DataFrame object with issues events data.
    issues_reactions_df : DataFrame
        Pandas DataFrame object with issues reactions data.

    Methods
    -------
    __init__(self, github_connection, repo, data_root_dir, request_maximum)
        Initial Issues object with general information.
    generate_pandas_tables(self, extract_reactions=False, check_for_updates=True)
        Extracting the complete issues from a repository.
    extract_issue_data(self, issue)
        Extracting general issue data.
    __extract_issue_reactions(self, extract_function, issue_id)
        Extracting issue reactions.
    extract_reaction_data(self, reaction, issue_id)
        Extracting issue reaction data.
    extract_issue_comment_data(self, issue_comment)
        Extracting issue comment data.
    __extract_issue_events(self, issue_events, index, issue_id=None)
        Extracting issue events.
    extract_issue_event_data(self, issue_event, issue_id=None)
        Extracting issue event data.
    get_pandas_table(data_root_dir, filename=ISSUES)
        Get a genearted pandas table.
    
    """
    ISSUES_DIR = "Issues"
    ISSUES = "pdIssues.p"
    ISSUES_COMMENTS = "pdIssuesComments.p"
    ISSUES_REACTIONS = "pdIssuesReactions.p"
    ISSUES_EVENTS = "pdIssuesEvents.p"
    EXTRACTION_PARAMS = {
        "reactions": False,
        "events": False,
        "comments": False
    }

    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000) -> None:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum)

        Initial Issues object with general information.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.
        repo : GitHubRepository
            Repository object from pygithub.
        data_root_dir : Path
            Data root directory for the repository.
        request_maximum : int, default=40000
            Maxmimum amount of returned informations for a general api call

        Notes
        -----
            PyGithub Github object structure: https://pygithub.readthedocs.io/en/latest/github.html
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        Core.__init__(
            self,
            github_connection,
            repo,
            data_root_dir,
            Path(data_root_dir, Issues.ISSUES_DIR),
            request_maximum
        )
    
    @property
    def issues_df(self):
        return Issues.get_pandas_table(self.data_root_dir)
    @property
    def issues_comments_df(self):
        return Issues.get_pandas_table(self.data_root_dir, Issues.ISSUES_COMMENTS)
    @property
    def issues_events_df(self):
        return Issues.get_pandas_table(self.data_root_dir, Issues.ISSUES_EVENTS)
    @property
    def issues_reactions_df(self):
        return Issues.get_pandas_table(self.data_root_dir, Issues.ISSUES_REACTIONS)

    def generate_pandas_tables(self, check_for_updates:bool = False, extraction_params:dict = {}):
        """
        generate_pandas_tables(self, extract_reactions=False, check_for_updates=True)

        Extracting the complete issues from a repository.

        Parameters
        ----------
        extract_reactions : bool, default=False
            If reactions should also be exracted. The extraction of all reactions increases significantly the aggregation speed.
        check_for_updates : bool, default=True
            Check first if there are any new issues information. Does not work when extract_reaction is True.
        
        """
        params = copy_valid_params(self.EXTRACTION_PARAMS,extraction_params)
        issues = self.save_api_call(self.repo.get_issues, state='all', sort="updated")
        total_count = self.get_save_total_count(issues)
        if check_for_updates:
            if params["reactions"]:
                print("Check for update does not work when extract_reactions is True")
            else:
                old_issues = Issues.get_pandas_table(self.data_root_dir)
                if not self.check_for_updates_paginated(issues, total_count, old_issues):
                    print("No new Issue information!")
                    return
        if params["events"]:
            events = self.save_api_call(self.repo.get_issues_events)
            events_overflow = False
            events_total_count = self.get_save_total_count(events)
            if events_total_count >= self.request_maximum:
                events_overflow = True
                print("Issues Events will be processed in Issues")

        issue_list = []
        issue_comment_list = []
        issue_event_list = []
        issue_reaction_list = []

        # issue data
        last_issue_id = 0
        extract_data = True
        issues = issues.reversed
        while True:
            if total_count >= self.request_maximum:
                print("Issues >= request_maximum ==> mutiple Issues progress bars")
                total_count = self.request_maximum
            for i in progress_bar(range(total_count), "Issues:          "):
                issue = self.get_save_api_data(issues, i)

                if extract_data:
                    issue_data = self.extract_issue_data(issue)
                    issue_list.append(issue_data)
                    # reaction data
                    if params["reactions"]:
                        issue_reaction_list += self.extract_reactions(
                            issue.get_reactions, 
                            issue.id, 
                            "issue")
                    if params["events"]:
                        # events data >= request maximum
                        if events_overflow:
                            issue_events = self.save_api_call(issue.get_events)
                            for i in range(self.request_maximum):
                                try:
                                    event = self.get_save_api_data(issue_events, i)
                                    issue_event_data = self.save_api_call(self.extract_issue_event_data, event, issue_id=issue.id)
                                    issue_event_list.append(issue_event_data)
                                except IndexError:
                                    break
                elif issue.id == last_issue_id:
                    extract_data = True
                else:
                    print(f"Skip Issue with ID: {issue.id}")

            if total_count == self.request_maximum:
                last_issue_id = issue_data["id"]
                extract_data = False
                issues = self.save_api_call(self.repo.get_issues, state='all', since=issue_data["updated_at"], sort="updated", direction="asc")
                total_count = self.get_save_total_count(issues)
            else:
                break
        if params["events"]:
            # issue event data < request maximum
            if not events_overflow:
                for i in progress_bar(range(events_total_count), "Issues Events:   "):
                    event = self.get_save_api_data(events, i)
                    issue_event_data = self.save_api_call(self.extract_issue_event_data, event, issue_id=issue.id)
                    issue_event_list.append(issue_event_data)
        if params["comments"]:
            # extract comments
            comments = self.save_api_call(self.repo.get_issues_comments, sort="updated", direction="asc")
            comments_total_count = self.get_save_total_count(comments)
            last_issue_comment_id = 0
            extract_data = True
            while True:
                if comments_total_count >= self.request_maximum:
                    print("Issues Comments >= request_maximum ==> mutiple Issue Comments progress bars")
                    comments_total_count = self.request_maximum
                for i in progress_bar(range(comments_total_count), "Issues Comments: "):
                    issue_comment = self.get_save_api_data(comments, i)
                    if extract_data:
                        issue_comment_data = self.save_api_call(self.extract_issue_comment_data, issue_comment)
                        issue_comment_list.append(issue_comment_data)
                        # issue comment reaction data
                        if params["reactions"]:
                            issue_reaction_list += self.extract_reactions(
                                issue.get_reactions, 
                                issue.id, 
                                "issue_comment")
                    elif issue_comment.id == last_issue_comment_id:
                        extract_data = True
                    else:
                        print(f"Skip Issue Comment with ID: {issue_comment.id}")
                if comments_total_count == self.request_maximum:
                    last_issue_comment_id = issue_comment_data["id"]
                    extract_data = False
                    comments = self.save_api_call(self.repo.get_issues_comments, since=issue_comment_data["updated_at"], sort="updated", direction="asc")
                    comments_total_count = self.get_save_total_count(comments)
                else:
                    break
        
        # Save lists
        issues_df = pd.DataFrame(issue_list)
        self.save_pandas_data_frame(Issues.ISSUES, issues_df)
        if params["comments"]:
            issues_comments_df = pd.DataFrame(issue_comment_list)
            self.save_pandas_data_frame(Issues.ISSUES_COMMENTS, issues_comments_df)
        if params["events"]:
            issues_events_df = pd.DataFrame(issue_event_list)
            self.save_pandas_data_frame(Issues.ISSUES_EVENTS, issues_events_df)
        if params["reactions"]:
            issues_reactions_df = pd.DataFrame(issue_reaction_list)
            self.save_pandas_data_frame(Issues.ISSUES_REACTIONS, issues_reactions_df)
    
    def extract_issue_data(self, issue:GitHubIssue):
        """
        extract_issue_data(self, issue)

        Extracting general issue data.

        Parameters
        ----------
        issue : GitHubIssue
            Issue object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted general issue data.

        Notes
        -----
            PyGithub Issue object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Issue.html

        """
        issue_data = {}
        #if not issue._assignee == GithubObject.NotSet:
        #    issue_data["assignee"] = self.extract_user_data(issue.closed_by) 
        issue_data["assignees"]  = self.extract_users(issue.assignees)
        issue_data["body"] = issue.body
        issue_data["closed_at"] = issue.closed_at
        if not issue._closed_by == GithubObject.NotSet:
            issue_data["closed_by"] = self.extract_user_data(issue.closed_by)
        issue_data["comments"] = issue.comments
        issue_data["created_at"] = issue.created_at
        issue_data["id"] = issue.id
        issue_data["labels"]  = self.extract_labels(issue.labels)
        issue_data["last_modified"] = issue.comments
        issue_data["locked"] = issue.comments
        # milestone ?
        issue_data["number"] = issue.number
        issue_data["state"] = issue.state
        issue_data["title"] = issue.title
        issue_data["updated_at"] = issue.updated_at
        issue_data["url"] = issue.url
        if not issue._user == GithubObject.NotSet:
            issue_data["author"] = self.extract_user_data(issue.user)
        if issue._pull_request == GithubObject.NotSet:
            issue_data["is_pull_request"] = False
        else:
            issue_data["is_pull_request"] = True
        return issue_data

    def extract_issue_comment_data(self, issue_comment:GitHubIssueComment):
        """
        extract_issue_comment_data(self, issue_comment)

        Extracting issue comment data.

        Parameters
        ----------
        issue_comment : GitHubIssueComment 
            IssueComment object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted issue comment data.

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
            issue_comment_data["author"] = self.extract_user_data(issue_comment.user)
        return issue_comment_data  

    def extract_issue_event_data(self, issue_event:GitHubIssueEvent, issue_id:int=None):
        """
        extract_issue_event_data(self, issue_event, issue_id=None)

        Extracting issue event data.

        Parameters
        ----------
        issue_event: GitHubIssueEvent
            IssueEvent object from pygithub.
        issue_id : int, default=None
            Id from issue as foreign key.

        Returns
        -------
        dict
            Dictionary with the extracted issue event data.

        Notes
        -----
            IssueEvent object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueEvent.html

        """
        issue_event_data = {}
        if not issue_event._actor == GithubObject.NotSet:
            issue_event_data["author"] = self.extract_user_data(issue_event.actor)
        if not issue_event._assignee == GithubObject.NotSet:
            issue_event_data["assignee"] = self.extract_user_data(issue_event.assignee)
        if not issue_event._assigner == GithubObject.NotSet:
            issue_event_data["assigner"] = self.extract_user_data(issue_event.assigner)
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
        get_pandas_table(data_root_dir, filename=ISSUES)

        Get a genearted issue pandas table.

        Parameters
        ----------
        data_root_dir : Path
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
