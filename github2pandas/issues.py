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
from github2pandas.utility import Utility

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
    __init__(self, repo, data_root_dir, reactions=False, check_for_updates=False)
        Initial Issues object with general information.
    generate_pandas_tables(self, extract_reactions=False, check_for_updates=False)
        Extracting the complete issues from a repository.
    __extract_issue_data(self, issue)
        Extracting general issue data.
    __extract_issue_reactions(self, extract_function, issue_id)
        Extracting issue reactions.
    extract_reaction_data(self, reaction, issue_id)
        Extracting issue reaction data.
    __extract_issue_comments(self, issue_comments, index, extract_reactions)
        Extracting issue comments.
    __extract_issue_comment_data(self, issue_comment)
        Extracting issue comment data.
    __extract_issue_events(self, issue_events, index, issue_id=None)
        Extracting issue events.
    __extract_issue_event_data(self, issue_event, issue_id=None)
        Extracting issue event data.
    get_pandas_table(data_root_dir, filename=ISSUES)
        Get a genearted pandas table.
    
    """
    ISSUES_DIR = "Issues"
    ISSUES = "pdIssues.p"
    ISSUES_COMMENTS = "pdIssuesComments.p"
    ISSUES_REACTIONS = "pdIssuesReactions.p"
    ISSUES_EVENTS = "pdIssuesEvents.p"

    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000) -> None:
        """
        __init__(self, repo, data_root_dir, reactions=False, check_for_updates=False)

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
        self.__github_connection = github_connection
        self.__repo = repo
        self.__data_root_dir = data_root_dir
        self.__issues_dir = Path(data_root_dir, Issues.ISSUES_DIR)
        self.__users_ids = Utility.get_users_ids(data_root_dir)
        self.__request_maximum = request_maximum
        self.__issue_list = []
        self.__issue_comment_list = []
        self.__issue_event_list = []
        self.__issue_reaction_list = []
        self.__issues_df = pd.DataFrame()
        self.__issues_comments_df = pd.DataFrame()
        self.__issues_events_df = pd.DataFrame()
        self.__issues_reactions_df = pd.DataFrame()

    @property
    def issues_df(self):
        return self.__issues_df
    @property
    def issues_comments_df(self):
        return self.__issues_comments_df
    @property
    def issues_events_df(self):
        return self.__issues_events_df
    @property
    def issues_reactions_df(self):
        return self.__issues_reactions_df

    def generate_pandas_tables(self, extract_reactions:bool = False, check_for_updates:bool = False):
        """
        generate_pandas_tables(self, extract_reactions=False, check_for_updates=False)

        Extracting the complete issues from a repository.

        Parameters
        ----------
        extract_reactions : bool, default=False
            If reactions should also be exracted. The extraction of all reactions increases significantly the aggregation speed.
        check_for_updates : bool, default=False
            Check first if there are any new issues information. Does not work when extract_reaction is True.
        
        """
        issues = Utility.save_api_call(self.__repo.get_issues, self.__github_connection, state='all', sort="updated")
        total_count = Utility.get_save_total_count(issues, self.__github_connection)
        if check_for_updates:
            if extract_reactions:
                print("Check for update does not work when extract_reactions is True")
            else:
                old_issues = Issues.get_pandas_table(self.__data_root_dir)
                if not Utility.check_for_updates_paginated(issues, total_count, old_issues):
                    print("No new Issue information!")
                    return

        comments = Utility.save_api_call(self.__repo.get_issues_comments, self.__github_connection)
        comments_overflow = False
        comments_total_count = Utility.get_save_total_count(comments,self.__github_connection)
        if comments_total_count >= self.__request_maximum:
            comments_overflow = True
            print("Issues Comments will be processed in Issues")
        events = Utility.save_api_call(self.__repo.get_issues_events, self.__github_connection)
        events_overflow = False
        events_total_count = Utility.get_save_total_count(events,self.__github_connection)
        if events_total_count >= self.__request_maximum:
            events_overflow = True
            print("Issues Events will be processed in Issues")

        self.__users_ids = Utility.get_users_ids(self.__data_root_dir)
        # issue data
        last_issue_id = 0
        extract_data = True
        while True:
            issues = issues.reversed
            if total_count >= self.__request_maximum:
                print("Issues >= request_maximum ==> mutiple Issue progress bars")
                total_count = self.__request_maximum
            for i in Utility.progress_bar(range(total_count), "Issues:          "):
                issue = Utility.get_save_api_data(issues, i, self.__github_connection)

                if extract_data:
                    issue_data = self.__extract_issue_data(issue)
                    self.__issue_list.append(issue_data)
                    # reaction data
                    if extract_reactions:
                        self.__extract_issue_reactions(issue.get_reactions, issue.id, "issue")
                    # comment data >= request maximum
                    if comments_overflow:
                        issue_comments = Utility.save_api_call(issue.get_comments, self.__github_connection)
                        for i in range(self.__request_maximum):
                            try:
                                self.__extract_issue_comments(issue_comments, i, extract_reactions)
                            except IndexError:
                                break
                    # events data >= request maximum
                    if events_overflow:
                        issue_events = Utility.save_api_call(issue.get_events, self.__github_connection)
                        for i in range(self.__request_maximum):
                            try:
                                self.__extract_issue_events(issue_events, i, issue_id=issue.id)
                            except IndexError:
                                break
                elif issue.id == last_issue_id:
                    extract_data = True
                else:
                    print("Issue error!")

            if total_count == self.__request_maximum:
                last_issue_id = issue_data["id"]
                extract_data = False
                issues = Utility.save_api_call(self.__repo.get_issues, self.__github_connection, state='all', since=issue_data["updated_at"], sort="updated")
                total_count = Utility.get_save_total_count(issues, self.__github_connection)
            else:
                break
        # issue comment data < request maximum
        if not comments_overflow:
            for i in Utility.progress_bar(range(comments_total_count), "Issues Comments: "):
                self.__extract_issue_comments(comments, i, extract_reactions)
        # issue event data < request maximum
        if not events_overflow:
            for i in Utility.progress_bar(range(events_total_count), "Issues Events:   "):
                self.__extract_issue_events(events, i, issue_id=issue.id)
        # Save lists
        self.__issues_df = pd.DataFrame(self.__issue_list)
        self.__issues_comments_df = pd.DataFrame(self.__issue_comment_list)
        self.__issues_events_df = pd.DataFrame(self.__issue_event_list)
        Utility.save_pandas_data_frame(self.__issues_dir, Issues.ISSUES, self.__issues_df)
        Utility.save_pandas_data_frame(self.__issues_dir, Issues.ISSUES_COMMENTS, self.__issues_comments_df)
        Utility.save_pandas_data_frame(self.__issues_dir, Issues.ISSUES_EVENTS, self.__issues_events_df)
        if extract_reactions:
            self.__issues_reactions_df = pd.DataFrame(self.__issue_reaction_list)
            Utility.save_list_to_pandas_table(self.__issues_dir, Issues.ISSUES_REACTIONS, self.__issues_reactions_df)
        else:
            self.__issues_reactions_df = pd.DataFrame()
    
    def __extract_issue_data(self, issue:GitHubIssue):
        """
        __extract_issue_data(self, issue)

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
        # assignee ?
        issue_data["assignees"]  = Utility.extract_assignees(issue.assignees, self.__users_ids, self.__data_root_dir)
        issue_data["body"] = issue.body
        issue_data["closed_at"] = issue.closed_at
        if not issue._closed_by == GithubObject.NotSet:
            issue_data["closed_by"] = Utility.extract_user_data(issue.closed_by, self.__users_ids, self.__data_root_dir)
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
            issue_data["author"] = Utility.extract_user_data(issue.user, self.__users_ids, self.__data_root_dir)
        if issue._pull_request == GithubObject.NotSet:
            issue_data["is_pull_request"] = False
        else:
            issue_data["is_pull_request"] = True
        return issue_data

    def __extract_issue_reactions(self, extract_function, parent_id:int, parent_name:str):
        """
        __extract_issue_reactions(self, extract_function, parent_id)

        Extracting issue reactions.

        Parameters
        ----------
        extract_function : function
            A function to call issue reactions.
        issue_id : int
            Id from issue as foreign key.

        """
        reactions = Utility.save_api_call(extract_function, self.__github_connection)
        for i in range(self.__request_maximum):
            try:
                reaction = Utility.get_save_api_data(reactions, i, self.__github_connection)
                reaction_data = Utility.save_api_call(self.__extract_issue_reaction_data, self.__github_connection, reaction, parent_id, parent_name)
                self.__issue_reaction_list.append(reaction_data)
            except IndexError:
                break 

    def __extract_issue_reaction_data(self, reaction:GitHubReaction, parent_id:int, parent_name:str):
        """
        extract_reaction_data(self, reaction, issue_id)

        Extracting issue reaction data.

        Parameters
        ----------
        reaction : Reaction
            Reaction object from pygithub.
        parent_id : int
            Id as foreign key.
        parent_name : str
            Name of the parent (issue or comment).

        Returns
        -------
        dict
            Dictionary with the extracted reaction data.

        Notes
        -----
            Reaction object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Reaction.html

        """
        reaction_data = {} 
        reaction_data["parent_id"] = parent_id
        reaction_data["parent_name"] = parent_name
        reaction_data["content"] = reaction.content
        reaction_data["created_at"] = reaction.created_at
        reaction_data["id"] = reaction.id
        if not reaction._user == GithubObject.NotSet:
            reaction_data["author"] = Utility.extract_user_data(reaction.user, self.__users_ids, self.__data_root_dir)
        return reaction_data

    def __extract_issue_comments(self, issue_comments:PaginatedList, index:int, extract_reactions:bool):
        """
        __extract_issue_comments(self, issue_comments, index, extract_reactions)

        Extracting issue comments.

        Parameters
        ----------
        issue_comments : PaginatedList[GitHubIssueComment]
            A PaginatedList of GitHubIssueComment.
        index : int
            Current index of PaginatedList.
        extract_reactions : bool
            If reactions should also be exracted. The extraction of all reactions increases significantly the aggregation speed.

        """
        issue_comment = Utility.get_save_api_data(issue_comments, index, self.__github_connection)
        issue_comment_data = Utility.save_api_call(self.__extract_issue_comment_data, self.__github_connection, issue_comment)
        self.__issue_comment_list.append(issue_comment_data)
        # issue comment reaction data
        if extract_reactions:
            self.__extract_issue_reactions(
                issue_comment.get_reactions,
                issue_comment.id,
                "issue_comment")

    def __extract_issue_comment_data(self, issue_comment:GitHubIssueComment):
        """
        __extract_issue_comment_data(self, issue_comment)

        Extracting issue comment data.

        Parameters
        ----------
        issue_comment : GitHubIssueComment 
            IssueComment object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extractedissue comment data.

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
            issue_comment_data["author"] = Utility.extract_user_data(issue_comment.user, self.__users_ids, self.__data_root_dir)
        return issue_comment_data

    def __extract_issue_events(self, issue_events:PaginatedList, index:int, issue_id:int=None):
        """
        __extract_issue_events(self, issue_events, index, issue_id=None)

        Extracting issue events.

        Parameters
        ----------
        issue_events : PaginatedList[GitHubIssueEvent]
            A PaginatedList of GitHubIssueEvent.
        index : int
            Current index of PaginatedList.
        issue_id : int, default=None
            Id from issue as foreign key.

        """
        event = Utility.get_save_api_data(issue_events, index, self.__github_connection)
        issue_event_data = Utility.save_api_call(self.__extract_issue_event_data, self.__github_connection, event, issue_id=issue_id)
        self.__issue_event_list.append(issue_event_data)

    def __extract_issue_event_data(self, issue_event:GitHubIssueEvent, issue_id:int=None):
        """
        __extract_issue_event_data(self, issue_event, issue_id=None)

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
            issue_event_data["author"] = Utility.extract_user_data(issue_event.actor, self.__users_ids, self.__data_root_dir)
        if not issue_event._assignee == GithubObject.NotSet:
            issue_event_data["assignee"] = Utility.extract_user_data(issue_event.assignee, self.__users_ids, self.__data_root_dir)
        if not issue_event._assigner == GithubObject.NotSet:
            issue_event_data["assigner"] = Utility.extract_user_data(issue_event.assigner, self.__users_ids, self.__data_root_dir)
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
