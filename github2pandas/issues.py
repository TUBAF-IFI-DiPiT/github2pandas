import time
import pandas as pd
from pathlib import Path
import os
import github

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

    @staticmethod
    def extract_issue_data(issue, users_ids, data_root_dir):
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
        issue_data["assignees"]  = Utility.extract_assignees(issue.assignees, users_ids, data_root_dir)
        issue_data["body"] = issue.body
        issue_data["closed_at"] = issue.closed_at
        if not issue._closed_by == github.GithubObject.NotSet:
            issue_data["closed_by"] = Utility.extract_user_data(issue.closed_by, users_ids, data_root_dir)
        issue_data["created_at"] = issue.created_at
        issue_data["id"] = issue.id
        issue_data["labels"]  = Utility.extract_labels(issue.labels)
        issue_data["state"] = issue.state
        issue_data["title"] = issue.title
        issue_data["updated_at"] = issue.updated_at
        if not issue._user == github.GithubObject.NotSet:
            issue_data["author"] = Utility.extract_user_data(issue.user, users_ids, data_root_dir)
        return issue_data

    @staticmethod
    def generate_issue_pandas_tables(repo, data_root_dir, github_connection, reactions=False, check_for_updates=False):
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

        if check_for_updates:
            new_issues = repo.get_issues(state='all') 
            real_issues = []
            for issue in new_issues:
                if issue._pull_request == github.GithubObject.NotSet:
                    real_issues.append(issue)
            old_issues = Issues.get_issues(data_root_dir)
            if not Utility.check_for_updates(real_issues, old_issues):
                return

        issues_dir = Path(data_root_dir, Issues.ISSUES_DIR)
        issues = repo.get_issues(state='all') 
        users_ids = Utility.get_users_ids(data_root_dir)
        issue_list = []
        issue_comment_list = []
        issue_event_list = []
        issue_reaction_list = []
        remaining_requests = Utility.get_remaining_github_requests(github_connection)
        for issue in issues:
            print(f"Remaining requests: {remaining_requests}")
            tic = time.perf_counter()
            Utility.check_estimated_request_limit(github_connection, remaining_requests)
            print(f"Time1: {time.perf_counter() - tic:0.4f} seconds")
            tic = time.perf_counter()
            # remove pull_requests from issues
            if issue._pull_request == github.GithubObject.NotSet:
                # issue data
                issue_data = Issues.extract_issue_data(issue, users_ids, data_root_dir)
                issue_list.append(issue_data)
                # issue comment data
                remaining_requests -=1
                for comment in issue.get_comments():
                    issue_comment_data = Utility.extract_comment_data(comment, issue.id, "issue", users_ids, data_root_dir)
                    issue_comment_list.append(issue_comment_data)
                    # issue comment reaction data
                    if reactions:
                        remaining_requests -=1
                        for reaction in comment.get_reactions():
                            reaction_data = Utility.extract_reaction_data(reaction,comment.id,"comment", users_ids, data_root_dir)
                            issue_reaction_list.append(reaction_data)
                # issue event data
                remaining_requests -=1
                for event in issue.get_events():
                    issue_event_data = Utility.extract_event_data(event, issue.id, "issue", users_ids, data_root_dir)
                    issue_event_list.append(issue_event_data)
                # issue reaction data
                if reactions:
                    remaining_requests -=1
                    for reaction in issue.get_reactions():
                        issue_reaction_data = Utility.extract_reaction_data(reaction,issue.id, "issue", users_ids, data_root_dir)
                        issue_reaction_list.append(issue_reaction_data)    
            print(f"Time2: {time.perf_counter() - tic:0.4f} seconds")
        # Save lists
        Utility.save_list_to_pandas_table(issues_dir, Issues.ISSUES, issue_list)
        Utility.save_list_to_pandas_table(issues_dir, Issues.ISSUES_COMMENTS, issue_comment_list)
        Utility.save_list_to_pandas_table(issues_dir, Issues.ISSUES_EVENTS, issue_event_list)
        if reactions:
            Utility.save_list_to_pandas_table(issues_dir, Issues.ISSUES_REACTIONS, issue_reaction_list)
    
    @staticmethod
    def get_issues(data_root_dir, filename=ISSUES):
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
        
        issues_dir = Path(data_root_dir, Issues.ISSUES_DIR)
        pd_issues_file = Path(issues_dir, filename)
        if pd_issues_file.is_file():
            return pd.read_pickle(pd_issues_file)
        else:
            return pd.DataFrame()
