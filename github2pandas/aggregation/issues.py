import pandas as pd
from pathlib import Path
import pickle
import os
import shutil
from .utility import Utility
import github

class AggIssues():
    """
    Class to aggregate Issues

    Attributes
    ----------
    ISSUES_DIR : str
        Pull request dir where all files are saved in.
    ISSUES : str
        Pandas table file for raw issue data.
    ISSUES_COMMENTS : str
        Pandas table file for raw comments data in issues.
    ISSUES_REACTIONS : str
        Pandas table file for raw reactions data in issues.
    ISSUES_EVENTS : str
        Pandas table file for raw reviews data in issues.

    Methods
    -------
    extract_issue_data(issue, data_root_dir)
        Extracting general issue data.
    generate_issue_pandas_tables(repo, data_root_dir)
        Extracting the complete issue data from a repository.
    get_raw_issues(data_root_dir, filename)
        Get the genearted pandas table.
    
    """
    ISSUES_DIR = "Issues"
    ISSUES = "pdIssues.p"
    ISSUES_COMMENTS = "pdIssuesComments.p"
    ISSUES_REACTIONS = "pdIssuesReactions.p"
    ISSUES_EVENTS = "pdIssuesEvents.p"

    @staticmethod
    def extract_issue_data(issue, data_root_dir):
        """
        extract_issue_data(issue, data_root_dir)

        Extracting general issue data.

        Parameters
        ----------
        issue: Issue
            Issue object from pygithub.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        IssueData
            Dictionary with the extracted data.

        Notes
        -----
            Issue object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Issue.html

        """
        issue_data = AggIssues.IssueData()  
        issue_data["assignees"]  = Utility.extract_assignees(issue.assignees, data_root_dir)
        issue_data["body"] = issue.body
        issue_data["closed_at"] = issue.closed_at
        if not issue._closed_by == github.GithubObject.NotSet:
            issue_data["closed_by"] = Utility.extract_user_data(issue.closed_by, data_root_dir)
        issue_data["created_at"] = issue.created_at
        issue_data["id"] = issue.id
        issue_data["labels"]  = Utility.extract_labels(issue.labels)
        issue_data["state"] = issue.state
        issue_data["title"] = issue.title
        issue_data["updated_at"] = issue.updated_at
        if not issue._user == github.GithubObject.NotSet:
            issue_data["author"] = Utility.extract_user_data(issue.user, data_root_dir)
        return issue_data

    @staticmethod
    def generate_issue_pandas_tables(repo, data_root_dir):
        """
        generate_issue_pandas_tables(repo, data_root_dir)

        Extracting the complete issue data from a repository.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        data_root_dir: str
            Path to the repo folder of the repository

        Returns
        -------
        bool
            Code runs without errors 
        
        Notes
        -----
            Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        issues_dir = Path(data_root_dir, AggIssues.ISSUES_DIR)
        issues = repo.get_issues(state='all') 
        issue_list = list()
        issue_comment_list = list()
        issue_event_list = list()
        issue_reaction_list = list()
        for issue in issues:
            # remove pull_requests from issues
            if issue._pull_request == github.GithubObject.NotSet:
                # issue data
                issue_data = AggIssues.extract_issue_data(issue, data_root_dir)
                issue_list.append(issue_data)
                # issue comment data
                for comment in issue.get_comments():
                    issue_comment_data = Utility.extract_comment_data(comment, issue.id, "issue", data_root_dir)
                    issue_comment_list.append(issue_comment_data)
                    # issue comment reaction data
                    for reaction in comment.get_reactions():
                        reaction_data = Utility.extract_reaction_data(reaction,comment.id,"comment", data_root_dir)
                        issue_reaction_list.append(reaction_data)
                # issue event data
                for event in issue.get_events():
                    issue_event_data = Utility.extract_event_data(event, issue.id, "issue", data_root_dir)
                    issue_event_list.append(issue_event_data)
                # issue reaction data
                for reaction in issue.get_reactions():
                    issue_reaction_data = Utility.extract_reaction_data(reaction,issue.id, "issue", data_root_dir)
                    issue_reaction_list.append(issue_reaction_data)    
        # Save lists
        Utility.save_list_to_pandas_table(issues_dir, AggIssues.ISSUES, issue_list)
        Utility.save_list_to_pandas_table(issues_dir, AggIssues.ISSUES_COMMENTS, issue_comment_list)
        Utility.save_list_to_pandas_table(issues_dir, AggIssues.ISSUES_EVENTS, issue_event_list)
        Utility.save_list_to_pandas_table(issues_dir, AggIssues.ISSUES_REACTIONS, issue_reaction_list)
        return True

    @staticmethod
    def get_raw_issues(data_root_dir, filename = ISSUES):
        """
        get_raw_issues(data_root_dir, filename)

        Get the genearted pandas table.

        Parameters
        ----------
        data_root_dir: str
            Path to the repo folder of the repository.
        filename: str, default: ISSUES
            A filename of Issues

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the issue data

        """
        issues_dir = Path(data_root_dir, AggIssues.ISSUES_DIR)
        pd_issues_file = Path(issues_dir, filename)
        if pd_issues_file.is_file():
            return pd.read_pickle(pd_issues_file)
        else:
            return pd.DataFrame()
    
    class IssueData(dict):
        """
        Class extends a dict in order to restrict the issue data set to defined keys.

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
            "assignees",
            "body",
            "closed_at",
            "closed_by",
            "created_at",
            "id",
            "labels",
            "state",
            "title",
            "updated_at",
            "author"
        ]
        
        def __init__(self):
            """
            __init__(self)

            Set all keys in KEYS to None.

            """

            for key in AggIssues.IssueData.KEYS:
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

            if key not in AggIssues.IssueData.KEYS:
                raise KeyError
            dict.__setitem__(self, key, val)