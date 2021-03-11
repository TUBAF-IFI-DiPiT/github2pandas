#!/usr/bin/python

import os

from pathlib import Path
import pygit2 as git2
import stat
import pandas as pd
import github
import pickle

def replace_dublicates(pd_table, column_name, dublicates):

    for name in dublicates:
        pd_table[column_name].replace(name[0], name[1],
                                        inplace=True)

    return pd_table


def get_repo(repo_name, token):

    g = github.Github(token)
    for repo in g.get_user().get_repos():
        if repo_name == repo.name:
            return repo
    return None

def extract_assignees(github_assignees):
    assignees = ""
    for assignee in github_assignees:
        assignees += extract_user_data(assignee) + "&"
    if len(assignees) > 0:
        assignees = assignees[:-1]
    return assignees

def extract_labels(github_labels):
    labels = ""
    for label in github_labels:
        labels += github_object.labels.name + "&"
    if len(labels) > 0:
        labels = labels[:-1]
    return labels

# https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html
def extract_user_data(author):
    if author:
        return author.name
    return None

# https://pygithub.readthedocs.io/en/latest/github_objects/Reaction.html
def extract_reaction_data(reaction, parent_id, parent_name):
    reaction_data = dict() 
    reaction_data[parent_name + "_id"] = parent_id
    reaction_data["content"] = reaction.content
    reaction_data["created_at"] = reaction.created_at
    reaction_data["id"] = reaction.id
    if reaction.user:
        reaction_data["author"] = extract_user_data(reaction.user)
    return reaction_data

def save_list_to_pandas_table(dir, filename, data_list):
    Path(dir).mkdir(parents=True, exist_ok=True)
    data_frame_ = pd.DataFrame(data_list)
    pd_file = Path(dir, filename)
    with open(pd_file, "wb") as f:
        pickle.dump(data_frame_, f)

# getting os permissions to remove (write) readonly files
def readonly_handler(func, local_directory, execinfo):

    os.chmod(local_directory, stat.S_IWRITE)
    func(local_directory)


def apply_python_date_format(pd_table, source_colum, destination_column):

    pd_table[destination_column] = pd.to_datetime(pd_table[source_colum], format="%Y-%m-%d %H:%M:%S")

    return pd_table

def extract_event_data(event, parent_id, parent):
        """
        extract_event_data(event, id, parent)

        Extracting general event data from a issue or pull request.

        Parameters
        ----------
        event: IssueEvent
            IssueEvent object from pygithub.
        parent_id: int
            Id from parent as foreign key.
        parent: str
            Is it issue or pull_request Event

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            IssueEvent object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueEvent.html

        """
        issue_event_data = dict()
        issue_event_data[parent + "_id"] = parent_id
        issue_event_data["author"] = extract_user_data(event.actor)
        issue_event_data["commit_id"] = event.commit_id
        issue_event_data["created_at"] = event.created_at
        issue_event_data["event"] = event.event
        issue_event_data["id"] = event.id
        if event.label:
            issue_event_data["label"] = event.label.name
        issue_event_data["assignee"] = extract_user_data(event.assignee)
        issue_event_data["assigner"] = extract_user_data(event.assigner)
        return issue_event_data