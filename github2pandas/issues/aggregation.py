import pandas as pd
from pathlib import Path
import pickle
import os
import shutil
from ..utility import Utility

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
    extract_issue_data(issue)
        Extracting general issue data.
    extract_issue_comment_data(comment, issue_id)
        Extracting general comment data from a issue.
    generate_pandas_tables(data_dir, repo)
        Extracting the complete issue data from a repository.
    get_raw_issues(data_dir, filename)
        Get the genearted pandas table.
    
    """
    ISSUES_DIR = "Issues"
    ISSUES = "pdIssues.p"
    ISSUES_COMMENTS = "pdIssuesComments.p"
    ISSUES_REACTIONS = "pdIssuesReactions.p"
    ISSUES_EVENTS = "pdIssuesEvents.p"

    @staticmethod
    def extract_issue_data(issue):
        """
        extract_issue_data(issue)

        Extracting general issue data.

        Parameters
        ----------
        issue: Issue
            Issue object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            Issue object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Issue.html

        """
        issue_data = dict()  
        issue_data["assignees"]  = Utility.extract_assignees(issue.assignees)
        issue_data["assignees_count"] = len(issue.assignees)
        issue_data["body"] = issue.body
        issue_data["closed_at"] = issue.closed_at
        issue_data["closedBy"] = Utility.extract_user_data(issue.closed_by)
        issue_data["created_at"] = issue.created_at
        issue_data["id"] = issue.id
        issue_data["labels"]  = Utility.extract_labels(issue.labels)
        issue_data["labels_count"] = len(issue.labels)
        if issue.milestone:
            issue_data["milestone_id"] = issue.milestone.id
        issue_data["state"] = issue.state
        issue_data["title"] = issue.title
        issue_data["updated_at"] = issue.updated_at
        issue_data["author"] = Utility.extract_user_data(issue.user)
        issue_data["comments_count"] = issue.get_comments().totalCount
        issue_data["event_count"] = issue.get_events().totalCount
        issue_data["reaction_count"] = issue.get_reactions().totalCount
        return issue_data

    @staticmethod
    def extract_issue_comment_data(comment, issue_id):
        """
        extract_issue_comment_data(comment, issue_id)

        Extracting general comment data from a issue.

        Parameters
        ----------
        comment: IssueComment
            IssueComment object from pygithub.
        issue_id: int
            issue id as foreign key.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            IssueComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueComment.html

        """
        issue_comment_data = dict()  
        issue_comment_data["issue_id"] = issue_id
        issue_comment_data["body"] = comment.body
        issue_comment_data["created_at"] = comment.created_at
        issue_comment_data["id"] = comment.id
        issue_comment_data["author"] = Utility.extract_user_data(comment.user)
        issue_comment_data["reactions"] = comment.get_reactions().totalCount
        return issue_comment_data

    @staticmethod
    def generate_pandas_tables(data_dir, repo):
        """
        generate_pandas_tables(data_dir, repo)

        Extracting the complete issue data from a repository.

        Parameters
        ----------
        data_dir: str
            Path to the data folder of the repository
        repo: Repository
            Repository object from pygithub.

        Returns
        -------
        bool
            Code runs without errors 
        
        Notes
        -----
            Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        data_dir_ = Path(data_dir, AggIssues.ISSUES_DIR)
        issues = repo.get_issues(state='all') 
        issue_list = list()
        issue_comment_list = list()
        issue_event_list = list()
        issue_reaction_list = list()
        for issue in issues:
            # remove pull_requests from issues
            if not issue.pull_request:
                # issue data
                issue_data = AggIssues.extract_issue_data(issue)
                issue_list.append(issue_data)
                # issue comment data
                for comment in issue.get_comments():
                    issue_comment_data = AggIssues.extract_issue_comment_data(comment, issue.id)
                    issue_comment_list.append(issue_comment_data)
                    # issue comment reaction data
                    for reaction in comment.get_reactions():
                        reaction_data = Utility.extract_reaction_data(reaction,comment.id,"comment")
                        issue_reaction_list.append(reaction_data)
                # issue event data
                for event in issue.get_events():
                    issue_event_data = Utility.extract_event_data(event, issue.id, "issue")
                    issue_event_list.append(issue_event_data)
                # issue reaction data
                for reaction in issue.get_reactions():
                    issue_reaction_data = Utility.extract_reaction_data(reaction,issue.id, "issue")
                    issue_reaction_list.append(issue_reaction_data)    
        # Save lists
        if os.path.isdir(data_dir_):
            shutil.rmtree(data_dir_)
        Utility.save_list_to_pandas_table(data_dir_, AggIssues.ISSUES, issue_list)
        Utility.save_list_to_pandas_table(data_dir_, AggIssues.ISSUES_COMMENTS, issue_comment_list)
        Utility.save_list_to_pandas_table(data_dir_, AggIssues.ISSUES_EVENTS, issue_event_list)
        Utility.save_list_to_pandas_table(data_dir_, AggIssues.ISSUES_REACTIONS, issue_reaction_list)
        return True

    @staticmethod
    def get_raw_issues(data_dir, filename = ISSUES):
        """
        get_raw_issues(data_dir, filename)

        Get the genearted pandas table.

        Parameters
        ----------
        data_dir: str
            Path to the data folder of the repository.
        filename: str, default: ISSUES
            A filename of Issues

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the issue data

        """
        data_dir_ = Path(data_dir, AggIssues.ISSUES_DIR)
        pd_issues_file = Path(data_dir_, filename)
        if pd_issues_file.is_file():
            return pd.read_pickle(pd_issues_file)
        else:
            return pd.DataFrame()