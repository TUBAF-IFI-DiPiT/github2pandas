#!/usr/bin/python

import os

from pathlib import Path
import pygit2 as git2
import stat
import pandas as pd
import github

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

# getting os permissions to remove (write) readonly files
def readonly_handler(func, local_directory, execinfo):

    os.chmod(local_directory, stat.S_IWRITE)
    func(local_directory)


def apply_python_date_format(pd_table, source_colum, destination_column):

    pd_table[destination_column] = pd.to_datetime(pd_table[source_colum], format="%Y-%m-%d %H:%M:%S")

    return pd_table
