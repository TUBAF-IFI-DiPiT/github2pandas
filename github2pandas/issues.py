import logging
from tkinter.tix import Tree
from pandas import DataFrame
import pandas as pd
from pathlib import Path
# github imports
from github import GithubObject
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
from github.Issue import Issue as GitHubIssue
from github.IssueComment import IssueComment as GitHubIssueComment
from github.IssueEvent import IssueEvent as GitHubIssueEvent
# github2pandas imports
from github2pandas.core import Core

class Issues(Core):
    """
    Class to aggregate Issues.

    Attributes
    ----------
    DATA_DIR : str
        Issues directory where all files are saved in.
    ISSUES : str
        Pandas table file for issues data.
    COMMENTS : str
        Pandas table file for comments data in issues.
    ISSUES_REACTIONS : str
        Pandas table file for reactions data in issues.
    EVENTS : str
        Pandas table file for events data in issues.
    EXTRACTION_PARAMS : dict
        Holds all extraction parameters with a default setting.
    FILES : dict
        Mappings from data directories to pandas table files.
    issues_df : DataFrame
        Pandas DataFrame object with general issues data.
    comments_df : DataFrame
        Pandas DataFrame object with comments data.
    events_df : DataFrame
        Pandas DataFrame object with events data.
    reactions_df : DataFrame
        Pandas DataFrame object with reactions data.

    Methods
    -------
    __init__(self, github_connection, repo, data_root_dir, request_maximum, log_level)
        Initializes Issues object with general information.
    generate_pandas_tables(check_for_updates=False, extraction_params={})
        Extracts the complete issues from a repository.
    extract_issue(data, params, events_overflow)
        Extracts the issue.
    extract_comment(data, params)
        Extracts the comments from issues.
    __extract_issue_data(issue)
        Extracts general data of one issue.
    __extract_comment_data(comment)
        Extracts data of one issue comment.
    __extract_event_data(event, issue_id=None)
        Extracts data of one issue event.
    
    """
    class Params(Core.Params):
        """
        A parameter class that holds all possible parameters for the data extraction.

        Methods
        -------
        __init__(self, issues, reactions, events, comments)
            Initializes all parameters with a default.
        
        """
        def __init__(self, issues: bool = True, reactions: bool = False, events: bool = True, comments: bool = True) -> None:
            """
            __init__(self, issues, reactions, events, comments)
       
            Initializes all parameters with a default.

            Parameters
            ----------
            issues : bool, default=True
                Extract issues?
            reactions : bool, default=True
                Extract reactions of issues?
            events : bool, default=True
                Extract events of issues?
            comments : bool, default=True
                Extract comments of issues?
            
            """
            self.issues = issues
            self.reactions = reactions
            self.events = events
            self.comments = comments
    
    class Files(Core.Files):
        """
        A file class that holds all file names and the folder name.

        Attributes
        ----------
        DATA_DIR : str
            Folder name for this module.
        ISSUES : str
            Filename of the issues pandas table.
        COMMENTS : str
            Filename of the issues comments pandas table.
        ISSUES_REACTIONS : str
            Filename of the issues reactions pandas table.
        EVENTS : str
            Filename of the issues events pandas table.

        """
        DATA_DIR = "Issues"
        ISSUES = "Issues.p"
        COMMENTS = "Comments.p"
        ISSUES_REACTIONS = "IssuesReactions.p"
        EVENTS = "Events.p"

    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000, log_level:int=logging.INFO) -> None:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum, log_level)

        Initializes Issues object with general information.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.
        repo : GitHubRepository
            Repository object from pygithub.
        data_root_dir : Path
            Data root directory for the repository.
        request_maximum : int, default=40000
            Maximum amount of returned informations for a general api call.
        log_level : int
            Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET), default value is enumaration value logging.INFO    
           

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
            Issues.Files.DATA_DIR,
            request_maximum=request_maximum,
            log_level=log_level
        )
    
    @property
    def issues_df(self) -> pd.DataFrame:
        return Core.get_pandas_data_frame(self.current_dir, Issues.Files.ISSUES)
    
    @property
    def comments_df(self) -> pd.DataFrame:
        return Core.get_pandas_data_frame(self.current_dir, Issues.Files.COMMENTS)
    
    @property
    def events_df(self) -> pd.DataFrame:
        return Core.get_pandas_data_frame(self.current_dir, Issues.Files.EVENTS)
    
    @property
    def reactions_df(self) -> pd.DataFrame:
        return Core.get_pandas_data_frame(self.current_dir, Issues.Files.ISSUES_REACTIONS)

    def generate_pandas_tables(self, check_for_updates:bool = False, params:Params = Params()) -> None:
        """
        generate_pandas_tables(check_for_updates=False, extraction_params={})

        Extracts the complete issues from a repository.
        Checks first if there are any new issues information in dependence of parameter check_for_updates.

        Parameters
        ----------
        check_for_updates : bool, default=False
            Determines whether update is necessary. Does not work when EXTRACTION_PARAMS "reactions" is True.
        extraction_params : dict, default={}
            Can hold extraction parameters, that define what will be extracted.
        
        """
        extract_issues = False
        if params.issues or params.reactions:
            extract_issues = True
            issues = self.save_api_call(self.repo.get_issues, state='all', sort="updated")
            total_count = self.get_save_total_count(issues)
            if check_for_updates:
                if params.reactions:
                    self.logger.warning("Check for update does not work when EXTRACTION_PARAMS \"reactions\" is True")
                else:
                    old_issues = self.issues_df
                    if not self.check_for_updates_paginated(issues, total_count, old_issues):
                        self.logger.info("No new Issue information!")
                        return
        events_overflow = False
        if params.events:
            events = self.save_api_call(self.repo.get_issues_events)
            events_total_count = self.get_save_total_count(events)
            if events_total_count >= self.request_maximum:
                events_overflow = True
                extract_issues = True
                self.logger.info("Issues Events will be processed in Issues")
        self.__issue_list = []
        self.__comment_list = []
        self.__event_list = []
        self.__reaction_list = []
        # issue data
        if extract_issues:
            issues = issues.reversed
            self.extract_with_updated_and_since(
                self.repo.get_issues,
                "Issues",
                self.extract_issue,
                params,
                events_overflow,
                initial_data_list=issues,
                initial_total_count=total_count,
                state="all")
        if params.events:
            # issue event data < request maximum
            if not events_overflow:
                for i in self.progress_bar(range(events_total_count), "Issues Events:   "):
                    event = self.get_save_api_data(events, i)
                    event_data = self.save_api_call(self.__extract_event_data, event)
                    self.__event_list.append(event_data)
        if params.comments:
            self.extract_with_updated_and_since(
                self.repo.get_issues_comments,
                "Issues Comments",
                self.extract_comment,
                params)
        # Save lists
        if extract_issues:
            issues_df = DataFrame(self.__issue_list)
            self.save_pandas_data_frame(Issues.Files.ISSUES, issues_df)
        if params.comments:
            comments_df = DataFrame(self.__comment_list)
            self.save_pandas_data_frame(Issues.Files.COMMENTS, comments_df)
        if params.events:
            events_df = DataFrame(self.__event_list)
            self.save_pandas_data_frame(Issues.Files.EVENTS, events_df)
        if params.reactions:
            reactions_df = DataFrame(self.__reaction_list)
            self.save_pandas_data_frame(Issues.Files.ISSUES_REACTIONS, reactions_df)
    
    def extract_issue(self, data:GitHubIssue, params:Params, events_overflow:bool) -> None:
        """
        extract_issue(data, params, events_overflow)

        Extracts the issue.

        Parameters
        ----------
        data : GitHubIssue
            Issue object from pygithub.
        params : dict
            Holds extraction parameters, that define what will be extracted.
        events_overflow : bool
            Downloads Events in Issues, if event amount greater than request_maximum
        
        Notes
        -----
            PyGithub Issue object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Issue.html

        """
        issue_data = self.__extract_issue_data(data)
        self.__issue_list.append(issue_data)
        # reaction data
        if params.reactions:
            self.__reaction_list += self.extract_reactions(
                data.get_reactions, 
                data.id, 
                "issue")
        if params.events:
            # events data >= request maximum
            if events_overflow:
                events = self.save_api_call(data.get_events)
                for i in range(self.request_maximum):
                    try:
                        event = self.get_save_api_data(events, i)
                        event_data = self.save_api_call(self.__extract_event_data, event, issue_id=data.id)
                        self.__event_list.append(event_data)
                    except IndexError:
                        break

    def extract_comment(self, data:GitHubIssueComment, params:Params) -> None:
        """
        extract_comment(data, params)

        Extracts the comments from issues.

        Parameters
        ----------
        data : GitHubIssueComment 
            IssueComment object from pygithub.
        params : dict
            Holds extraction parameters, that define what will be extracted.
        
        Notes
        -----
            IssueComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueComment.html

        """
        comment_data = self.save_api_call(self.__extract_comment_data, data)
        self.__comment_list.append(comment_data)
        # issue comment reaction data
        if params.reactions:
            self.__reaction_list += self.extract_reactions(
                data.get_reactions, 
                data.id, 
                "comment")
                
    def __extract_issue_data(self, issue:GitHubIssue) -> dict:
        """
        __extract_issue_data(issue)

        Extracts general data of one issue.

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
        # issue_data["last_modified"] = issue.last_modified NaN?
        issue_data["locked"] = issue.locked
        issue_data["active_lock_reason"] = issue.active_lock_reason
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

    def __extract_comment_data(self, comment:GitHubIssueComment) -> dict:
        """
        __extract_comment_data(comment)

        Extracts the data of one issue comment.

        Parameters
        ----------
        comment : GitHubIssueComment 
            IssueComment object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted issue comment data.

        Notes
        -----
            IssueComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueComment.html

        """
        comment_data = {}
        comment_data["body"] = comment.body
        comment_data["created_at"] = comment.created_at
        comment_data["id"] = comment.id
        comment_data["issue_url"] = comment.issue_url
        comment_data["updated_at"] = comment.updated_at
        if not comment._user == GithubObject.NotSet:
            comment_data["author"] = self.extract_user_data(comment.user)
        return comment_data  

    def __extract_event_data(self, event:GitHubIssueEvent, issue_id:int=None) -> dict:
        """
        __extract_event_data(event, issue_id=None)

        Extracts the data of one issue event.

        Parameters
        ----------
        event: GitHubIssueEvent
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
        event_data = {}
        if not event._actor == GithubObject.NotSet:
            event_data["author"] = self.extract_user_data(event.actor)
        if not event._assignee == GithubObject.NotSet:
            event_data["assignee"] = self.extract_user_data(event.assignee)
        if not event._assigner == GithubObject.NotSet:
            event_data["assigner"] = self.extract_user_data(event.assigner)
        event_data["commit_sha"] = event.commit_id
        event_data["created_at"] = event.created_at
        # dismissed_review ?
        event_data["event"] = event.event
        event_data["id"] = event.id
        if issue_id is None:
            event_data["issue_id"] = event.issue.id
        else:
            event_data["issue_id"] = issue_id
        if not event._label == GithubObject.NotSet:
            event_data["label"] = event.label.name
        # event_data["last_modified"] = event.last_modified NaN?
        # milestone ?
        return event_data
