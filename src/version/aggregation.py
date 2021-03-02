import os
from pathlib import Path
import sqlite3
import pickle
import pandas as pd
from src.utility import clone_repository, generate_data_base, readonly_handler


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


# For fast local testing. Can be removed when module is done.
if __name__ == "__main__":

    github_token = os.environ['TOKEN']

    git_repo_name = "xAPI_for_GitHubData"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    clone_repository(git_repo_owner=git_repo_owner,
                        git_repo_name=git_repo_name,
                        git_repo_dir=default_repo_folder,
                        git_hub_token=github_token)

    generate_data_base(git_repo_dir=default_repo_folder,
                     data_dir=default_data_folder,
                     git_repo_name=git_repo_name)

    generate_pandas_tables(data_dir=default_data_folder,
                        git_repo_name=git_repo_name)

    result = get_commit_raw_pandas_table(default_data_folder)

    print(result.columns)