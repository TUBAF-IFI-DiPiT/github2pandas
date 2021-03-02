#!/usr/bin/python

import os
from pathlib import Path
import pygit2 as git2
import stat
import git
import shutil
import git2net
import pandas as pd

def clone_repository(git_repo_owner, git_repo_name, git_repo_dir,
                    git_hub_token=None):
    if os.path.exists(git_repo_dir):
        shutil.rmtree(git_repo_dir, onerror=readonly_handler)
    callbacks = None
    if git_hub_token:
        callbacks = git2.RemoteCallbacks(
            git2.UserPass(git_hub_token, 'x-oauth-basic'))
    repo_ref = f"https://github.com/{git_repo_owner}/{git_repo_name}"
    repo = git2.clone_repository(repo_ref, git_repo_dir, callbacks=callbacks)

    existing_branches = list(repo.branches)
    r = git.Repo.init(git_repo_dir)

    for ref in repo.references:
        branch_name = ref.split('/')[-1]
        if branch_name != 'HEAD' and branch_name not in existing_branches:
            print("  ", branch_name, sep=", ", end="")
            try:
                r.git.branch('--track', branch_name,
                             'remotes/origin/'+branch_name)
            except Exception:
                print("An exception occurred")
                print(" ")

    return True

# getting os permissions to remove (write) readonly files
def readonly_handler(func, local_directory, execinfo):
    os.chmod(local_directory, stat.S_IWRITE)
    func(local_directory)


def generate_data_base(git_repo_dir, data_dir, git_repo_name):

    p = Path(data_dir)
    p.mkdir(parents=True, exist_ok=True)
    sqlite_db_file = Path(data_dir, git_repo_name + ".db")
    if os.path.exists(sqlite_db_file):
        os.remove(sqlite_db_file)
    git2net.mine_git_repo(git_repo_dir, sqlite_db_file,
                          no_of_processes=1,
                          max_modifications=1000)

    return True

# Polishing data
def manage_author_dublicates(pd_table, 
                           dublicate_names = [],
                           dublicate_emails = []):
    """
    Polishing the pandas table:
        - Insert a space into author_names without space between first
          name and surname.
        - Make email addresses constant for specific authors

    :param pandas_commits_table: a pandas workflow table from git2net is
    :required
    :return: cleaned pandas__table
    """
    # taking care about names without the space
    dublicate_names = dublicate_names

    # taking care about different email adresses
    # we definitely need a better algo for replacing unofficial email
    # addresses, like if email adresses aren't something with tu-freiberg then
    # use one of the other given consistently
    dublicate_emails = dublicate_emails

    for name in dublicate_names:
        pd_table['author_name'].replace(name[0], name[1],
                                                    inplace=True)

    for email in dublicate_emails:
        pd_table['author_email'].replace(email[0], email[1],
                                                     inplace=True)

    return pd_table


def apply_python_date_format(pd_table):
  print("Adapt date formates")
  pd_table['timestamp'] = pd.to_datetime(pd_table['author_date'], format="%Y-%m-%d %H:%M:%S")
  return pd_table