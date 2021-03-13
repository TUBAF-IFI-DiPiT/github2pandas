#!/usr/bin/python

import os

from pathlib import Path
import pygit2 as git2
import stat
import pandas as pd
import github
import pickle
import uuid

def replace_dublicates(pd_table, column_name, dublicates):

    for name in dublicates:
        pd_table[column_name].replace(name[0], name[1],
                                        inplace=True)

    return pd_table

# getting os permissions to remove (write) readonly files
def readonly_handler(func, local_directory, execinfo):

    os.chmod(local_directory, stat.S_IWRITE)
    func(local_directory)

def apply_python_date_format(pd_table, source_colum, destination_column):

    pd_table[destination_column] = pd.to_datetime(pd_table[source_colum], format="%Y-%m-%d %H:%M:%S")

    return pd_table

class Utility():
    """
    Class which contains functions for mutiple modules.

    Methods
    -------
        extract_assignees(github_assignees, data_root_dir)
            Get all assignees as one string.
        extract_labels(github_labels)
            Get all labels as one string.
        extract_user_data(author, data_root_dir)
            Extracting general user data.
        extract_author_data_from_commit(repo, sha, data_root_dir)
            Extracting general author data from a commit.
        extract_committer_data_from_commit(repo, sha, data_root_dir)
            Extracting general committer data from a commit.
        extract_reaction_data(reaction, parent_id, parent_name, data_root_dir)
            Extracting general reaction data.
        extract_event_data(event, parent_id, parent_name, data_root_dir)
            Extracting general event data from a issue or pull request.
        save_list_to_pandas_table(dir, file, data_list)
            Save a data list to a pandas table.
        get_repo(repo_name, token)
            Get a repository by name and token.
    
    """

    USERS = "Users.p"

    @staticmethod
    def extract_assignees(github_assignees, data_root_dir):
        """
        extract_assignees(github_assignees, data_root_dir)

        Get all assignees as one string.

        Parameters
        ----------
        github_assignees: list
            List of NamedUser
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        str
            String which contains all assignees.

        Notes
        -----
            NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html

        """
        assignees = ""
        for assignee in github_assignees:
            assignees += Utility.extract_user_data(assignee, data_root_dir) + "&"
        if len(assignees) > 0:
            assignees = assignees[:-1]
        return assignees

    @staticmethod
    def extract_labels(github_labels):
        """
        extract_labels(github_labels)

        Get all labels as one string.

        Parameters
        ----------
        github_labels: list
            List of Label

        Returns
        -------
        str
            String which contains all labels.

        Notes
        -----
            NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Label.html

        """
        labels = ""
        for label in github_labels:
            labels += github_object.labels.name + "&"
        if len(labels) > 0:
            labels = labels[:-1]
        return labels

    @staticmethod
    def extract_user_data(user, data_root_dir):
        """
        extract_user_data(author, data_root_dir)

        Extracting general user data.

        Parameters
        ----------
        user: NamedUser
            NamedUser object from pygithub.
        data_root_dir: str
            Repo dir of the project.
        Returns
        -------
        str
            Anonym uuid of user.

        Notes
        -----
            NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html

        """
        if not user:
            return None
        users_file = Path(data_root_dir, Utility.USERS)
        users_df = pd.DataFrame({
            "anonym_uuid": [],
            "id": [],
            "name": [],
            "email": [],
            "login": []
        })
        if users_file.is_file():
            users_df = pd.read_pickle(users_file)
        saved_user = users_df.loc[users_df['id'] == user.id]
        if saved_user.empty:
            user_data = dict()
            user_data["anonym_uuid"] = str(uuid.uuid4())
            user_data["id"] = user.id
            user_data["name"] = user.name
            user_data["email"] = user.email
            user_data["login"] = user.login
            users_df = users_df.append(user_data, ignore_index=True)
            with open(users_file, "wb") as f:
                pickle.dump(users_df, f)
            return user_data["anonym_uuid"]
        else:
            return saved_user.iloc[0]["anonym_uuid"]
    
    @staticmethod
    def extract_author_data_from_commit(repo, sha, data_root_dir):
        """
        extract_author_data_from_commit(repo, sha, data_root_dir)

        Extracting general author data from a commit.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        sha: str
            sha from the commit.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        str
            Anonym uuid of user.

        Notes
        -----
            Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        if not sha:
            return None
        commit = repo.get_commit(sha)
        if not commit:
            return None
        return Utility.extract_user_data(commit.author, data_root_dir)
               
    @staticmethod
    def extract_committer_data_from_commit(repo, sha, data_root_dir):
        """
        extract_committer_data_from_commit(repo, sha, data_root_dir)

        Extracting general committer data from a commit.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        sha: str
            sha from the commit.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        str
            Anonym uuid of user.

        Notes
        -----
            Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        if not sha:
            return None
        commit = repo.get_commit(sha)
        if not commit:
            return None
        return Utility.extract_user_data(commit.committer, data_root_dir)

    @staticmethod
    def extract_reaction_data(reaction, parent_id, parent_name, data_root_dir):
        """
        extract_reaction_data(reaction, parent_id, parent_name)

        Extracting general reaction data.

        Parameters
        ----------
        reaction: Reaction
            Reaction object from pygithub.
        parent_id: int
            Id from parent as foreign key.
        parent_name: str
            Name of the parent.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            Reaction object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Reaction.html

        """
        reaction_data = dict() 
        reaction_data[parent_name + "_id"] = parent_id
        reaction_data["content"] = reaction.content
        reaction_data["created_at"] = reaction.created_at
        reaction_data["id"] = reaction.id
        if reaction.user:
            reaction_data["author"] = Utility.extract_user_data(reaction.user, data_root_dir)
        return reaction_data
    
    @staticmethod
    def extract_event_data(event, parent_id, parent_name, data_root_dir):
        """
        extract_event_data(event, id, parent_name)

        Extracting general event data from a issue or pull request.

        Parameters
        ----------
        event: IssueEvent
            IssueEvent object from pygithub.
        parent_id: int
            Id from parent as foreign key.
        parent_name: str
            Name of the parent.
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            IssueEvent object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueEvent.html

        """
        issue_event_data = dict()
        issue_event_data[parent_name + "_id"] = parent_id
        issue_event_data["author"] = Utility.extract_user_data(event.actor, data_root_dir)
        issue_event_data["commit_id"] = event.commit_id
        issue_event_data["created_at"] = event.created_at
        issue_event_data["event"] = event.event
        issue_event_data["id"] = event.id
        if event.label:
            issue_event_data["label"] = event.label.name
        issue_event_data["assignee"] = Utility.extract_user_data(event.assignee, data_root_dir)
        issue_event_data["assigner"] = Utility.extract_user_data(event.assigner, data_root_dir)
        return issue_event_data
    
    @staticmethod
    def save_list_to_pandas_table(dir, file, data_list):
        """
        save_list_to_pandas_table(dir, file, data_list)

        Save a data list to a pandas table.

        Parameters
        ----------
        dir: str
            Path to the desired save dir.
        file: str
            Name of the file.
        data_list: list
            list of data dictionarys

        """
        Path(dir).mkdir(parents=True, exist_ok=True)
        data_frame_ = pd.DataFrame(data_list)
        pd_file = Path(dir, file)
        with open(pd_file, "wb") as f:
            pickle.dump(data_frame_, f)

    @staticmethod      
    def get_repo(repo_name, token):
        """
        get_repo(repo_name, token)

        Get a repository by name and token.

        Parameters
        ----------
        repo_name: str
            the name of the desired repository.
        token: str
            A valid Github Token.
        
        Returns
        -------
        repo
            Repository object from pygithub.

        Notes
        -----
            Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        g = github.Github(token)
        for repo in g.get_user().get_repos():
            if repo_name == repo.name:
                return repo
        return None
    