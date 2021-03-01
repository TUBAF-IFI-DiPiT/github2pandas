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


# getting os permissions to remove (write) readonly files
def readonly_handler(func, local_directory, execinfo):
    os.chmod(local_directory, stat.S_IWRITE)
    func(local_directory)


def cloneRepository(git_repo_owner, git_repo_name, git_repo_dir,
                    GitHubToken=None):

    if os.path.exists(git_repo_dir):
        shutil.rmtree(git_repo_dir, onerror=readonly_handler)
    callbacks = git2.RemoteCallbacks(
        git2.UserPass(GitHubToken, 'x-oauth-basic'))
    repo_ref = f"https://github.com/{git_repo_owner}/{git_repo_name}"
    if GitHubToken:
        repo = git2.clone_repository(repo_ref, git_repo_dir, callbacks=callbacks)
    else:
        repo = git2.clone_repository(repo_ref, git_repo_dir, callbacks=None)

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

def generateDataBase(git_repo_dir, data_dir, git_repo_name):

    p = Path(data_dir)
    p.mkdir(parents=True, exist_ok=True)
    sqlite_db_file = Path(data_dir, git_repo_name + ".db")
    if os.path.exists(sqlite_db_file):
        os.remove(sqlite_db_file)
    git2net.mine_git_repo(git_repo_dir, sqlite_db_file,
                          no_of_processes=1,
                          max_modifications=1000)

    return True


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


if __name__ == "__main__":

    github_token = os.environ['TOKEN']

    git_repo_name = "xAPI_for_GitHubData"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    cloneRepository(git_repo_owner=git_repo_owner,
                        git_repo_name=git_repo_name,
                        git_repo_dir=default_repo_folder,
                        GitHubToken=github_token)

    generateDataBase(git_repo_dir=default_repo_folder,
                     data_dir=default_data_folder,
                     git_repo_name=git_repo_name)

    generatePandasTables(data_dir=default_data_folder,
                        git_repo_name=git_repo_name)

    result = getCommitRawPandasTable(default_data_folder)

    print(result.columns)