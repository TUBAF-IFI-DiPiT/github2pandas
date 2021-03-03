import os
from pathlib import Path
import sqlite3
import pickle
import pandas as pd
import pygit2 as git2
import stat
import git
import shutil
import git2net

from .. import utility

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


def generate_pandas_tables(data_dir, git_repo_name):

    sqlite_db_file = Path(data_dir, git_repo_name + ".db")

    db = sqlite3.connect(sqlite_db_file)
    pdCommits = pd.read_sql_query("SELECT * FROM commits", db)
    pdEdits = pd.read_sql_query("SELECT * FROM edits", db)

    pd_commits_file = Path(data_dir, "pdCommits" + ".p")
    with open(pd_commits_file, "wb") as f:
        pickle.dump(pdCommits, f)

    pd_edits_file = Path(data_dir, "pdEdits" + ".p")
    with open(pd_edits_file, "wb") as f:
        pickle.dump(pdEdits, f)

    return True


def get_commit_raw_pandas_table(data_dir):
    pd_commits_file = Path(data_dir, "pdCommits" + ".p")
    if pd_commits_file.is_file():
        return pd.read_pickle(pd_commits_file)
    else:
        return pd.DataFrame()


def get_edit_raw_pandas_table(data_dir):
    pd_edits_file = Path(data_dir, "pdEdits" + ".p")
    if pd_edits_file.is_file():
        return pd.read_pickle(pd_edits_file)
    else:
        return pd.DataFrame()
