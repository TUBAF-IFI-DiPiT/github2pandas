import stat
import pygit2 as git2
import git
import os
import shutil
import yaml
from pathlib import Path
import git2net
import sqlite3
import pickle
import pandas as pd
from src.utility import clone_repository, generate_data_base, readonly_handler




def generatePandasTables(data_dir, git_repo_name):

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


def getCommitRawPandasTable(data_dir):
    pd_commits_file = Path(data_dir, "pdCommits" + ".p")
    if pd_commits_file.is_file():
        return pd.read_pickle(pd_commits_file)
    else:
        return pd.DataFrame()


def getEditRawPandasTable(data_dir):
    pd_edits_file = Path(data_dir, "pdEdits" + ".p")
    if pd_edits_file.is_file():
        return pd.read_pickle(pd_edits_file)
    else:
        return pd.DataFrame()


# should be moved to execute.py?
if __name__ == "__main__":

    github_token = os.environ['TOKEN']

    git_repo_name = "xAPI_for_GitHubData"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    clone_repository(git_repo_owner=git_repo_owner,
                        git_repo_name=git_repo_name,
                        git_repo_dir=default_repo_folder,
                        GitHubToken=github_token)

    generate_data_base(git_repo_dir=default_repo_folder,
                     data_dir=default_data_folder,
                     git_repo_name=git_repo_name)

    generatePandasTables(data_dir=default_data_folder,
                        git_repo_name=git_repo_name)

    result = getCommitRawPandasTable(default_data_folder)

    print(result.columns)