import os
import sqlite3
import pickle
import pandas as pd
import pygit2 as git2
import git
import git2net
import shutil
from pathlib import Path

class AggVersion(object):
   
    VERSION_DIR = "Versions"
    VERSION_REPOSITORY_DIR = "repo"
    VERSION_COMMITS = "pdCommits.p"
    VERSION_EDITS = "pdEdits.p"
    VERSION_DB = "Versions.db"
    NO_OF_PROCESSES = 1

    @staticmethod
    def clone_repository(repo, data_root_dir, github_token=None):

        git_repo_name = repo.name
        git_repo_owner = repo.owner.login
        
        version_folder = Path(data_root_dir, AggVersion.VERSION_DIR)
        version_folder.mkdir(parents=True, exist_ok=True)

        repo_dir = version_folder.joinpath(AggVersion.VERSION_REPOSITORY_DIR)
        if repo_dir.exists ():
            shutil.rmtree(repo_dir.resolve())

        callbacks = None

        if github_token:
            callbacks = git2.RemoteCallbacks(
                git2.UserPass(github_token, 'x-oauth-basic'))
        repo_ref = f"https://github.com/{git_repo_owner}/{git_repo_name}"
        repo = git2.clone_repository(repo_ref, repo_dir, callbacks=callbacks)

        existing_branches = list(repo.branches)
        r = git.Repo.init(repo_dir)

        for ref in repo.references:
            branch_name = ref.split('/')[-1]
            if branch_name != 'HEAD' and branch_name not in existing_branches:
                print("  ", branch_name, end="")
                try:
                    r.git.branch('--track', branch_name,
                                'remotes/origin/'+branch_name)
                    print(" ")
                except Exception:
                    print(" -> An exception occurred")


        return True

    @staticmethod
    def generate_data_base(data_root_dir, no_of_processes=1):

        version_folder = Path(data_root_dir, AggVersion.VERSION_DIR)
        version_folder.mkdir(parents=True, exist_ok=True)
        repo_dir = version_folder.joinpath(AggVersion.VERSION_REPOSITORY_DIR)
        sqlite_db_file = version_folder.joinpath(AggVersion.VERSION_DB)

        if os.path.exists(sqlite_db_file):
            os.remove(sqlite_db_file)
        git2net.mine_git_repo(repo_dir, sqlite_db_file,
                            no_of_processes=AggVersion.NO_OF_PROCESSES,
                            max_modifications=1000)
        return True

    @staticmethod
    def generate_version_pandas_tables(data_root_dir):

        AggVersion.generate_data_base(data_root_dir, no_of_processes=1)

        version_folder = Path(data_root_dir, AggVersion.VERSION_DIR)
        sqlite_db_file = version_folder.joinpath(AggVersion.VERSION_DB)

        db = sqlite3.connect(sqlite_db_file)
        pdCommits = pd.read_sql_query("SELECT * FROM commits", db)
        pdEdits = pd.read_sql_query("SELECT * FROM edits", db)

        pd_commits_file = Path(version_folder, AggVersion.VERSION_COMMITS)
        with open(pd_commits_file, "wb") as f:
            pickle.dump(pdCommits, f)

        pd_edits_file = Path(version_folder, AggVersion.VERSION_EDITS)
        with open(pd_edits_file, "wb") as f:
            pickle.dump(pdEdits, f)

        return True

    @staticmethod
    def get_raw_commit(data_root_dir):
        pd_commits_file = Path(data_root_dir, AggVersion.VERSION_DIR).joinpath(AggVersion.VERSION_COMMITS)
        if pd_commits_file.is_file():
            return pd.read_pickle(pd_commits_file)
        else: 
            return None

    @staticmethod
    def get_raw_edit(data_root_dir):
        pd_edits_file = Path(data_root_dir, AggVersion.VERSION_DIR).joinpath(AggVersion.VERSION_EDITS)
        if pd_edits_file.is_file():
            return pd.read_pickle(pd_edits_file)
        else: 
            return None
