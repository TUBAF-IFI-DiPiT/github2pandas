import os
import sqlite3
import pickle
import pandas as pd
import pygit2 as git2
import git
import git2net
import shutil
from pathlib import Path

class AggVersion():
    """
    Class to aggregate Pull Requests

    Attributes
    ----------
    VERSION_DIR : str
        Version dir where all files are saved in.
    VERSION_REPOSITORY_DIR : str
        Folder of cloned repository.
    VERSION_COMMITS : str
        Pandas table file for commits.
    VERSION_EDITS : str
        Pandas table file for edit data per commit.
    VERSION_DB : str
        MYSQL data base file containing version history.
    NO_OF_PROCESSES : int
        Number of processors used for crawling process.

    Methods
    -------
    clone_repository(repo, data_root_dir, github_token=None)
        Cloning repository from git.
    generate_data_base(data_root_dir)
        Extracting version data from a local repository and storing them in a mysql data base.
    generate_version_pandas_tables(data_root_dir)
        Extracting edits and commits in a pandas table.
    get_raw_commit(data_root_dir):
        Get the generated pandas table.
    get_raw_edit(data_root_dir)
        Get the generated pandas table.
    """  

    VERSION_DIR = "Versions"
    VERSION_REPOSITORY_DIR = "repo"
    VERSION_COMMITS = "pdCommits.p"
    VERSION_EDITS = "pdEdits.p"
    VERSION_DB = "Versions.db"
    NO_OF_PROCESSES = 1

    @staticmethod
    def clone_repository(repo, data_root_dir, github_token=None):
        """
        Clone_repository(repo, data_root_dir, github_token=None)

        Cloning repository from git.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        data_root_dir: str
            Repo dir of the project.
        github_token: str
            Token string

        Returns
        -------
        Bool
            Code runs without errors 

        Notes
        -----
            Pygit2 documentation: https://github.com/libgit2/pygit2
        """
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

        for branch_name in repo.references:

            branch_pattern = ['refs/heads/', 'refs/remotes/origin/']
            for pattern in branch_pattern:
                branch_name = branch_name.replace(pattern, '')

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
    def generate_data_base(data_root_dir):
        """
        generate_data_base(data_root_dir)

        Extracting version data from a local repository and storing them in a mysql data base.

        Parameters
        ----------
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        bool
            Code runs without errors 
        
        Notes
        -----
        Be aware of the large number of configuration parameters for appling the crawling process given by
        https://github.com/gotec/git2net/blob/master/git2net/extraction.py

        .. code-block:: python
        
            def mine_git_repo(git_repo_dir, sqlite_db_file, commits=[],
                            use_blocks=False, no_of_processes=os.cpu_count(), chunksize=1, exclude=[],
                            blame_C='', blame_w=False, max_modifications=0, timeout=0, extract_text=False,
                            extract_complexity=False, extract_merges=True, extract_merge_deletions=False,
                            all_branches=False):
        """
        version_folder = Path(data_root_dir, AggVersion.VERSION_DIR)
        version_folder.mkdir(parents=True, exist_ok=True)
        repo_dir = version_folder.joinpath(AggVersion.VERSION_REPOSITORY_DIR)
        sqlite_db_file = version_folder.joinpath(AggVersion.VERSION_DB)

        if os.path.exists(sqlite_db_file):
            os.remove(sqlite_db_file)

        print("--------------------------------------")
        print(AggVersion.NO_OF_PROCESSES)
        print("--------------------------------------")
        git2net.mine_git_repo(repo_dir, sqlite_db_file,
                              use_blocks=True,
                              no_of_processes=AggVersion.NO_OF_PROCESSES,
                              max_modifications=1000)
        return True

    @staticmethod
    def generate_version_pandas_tables(data_root_dir):
        """
        generate_version_pandas_tables(data_root_dir)

        Extracting edits and commits in a pandas table.

        Parameters
        ----------
        data_root_dir: str
            Repo dir of the project.

        Returns
        -------
        bool
            Code runs without errors 
        """

        AggVersion.generate_data_base(data_root_dir)

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
        """
        get_raw_commit(data_root_dir)

        Get the generated pandas table.

        Parameters
        ----------
        data_root_dir: str
            Path to the data folder of the repository.

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the commit data set
        """
        pd_commits_file = Path(data_root_dir, AggVersion.VERSION_DIR).joinpath(AggVersion.VERSION_COMMITS)
        if pd_commits_file.is_file():
            return pd.read_pickle(pd_commits_file)
        else: 
            return None

    @staticmethod
    def get_raw_edit(data_root_dir):
        """
        get_raw_edit(data_root_dir)

        Get the generated pandas table.

        Parameters
        ----------
        data_root_dir: str
            Path to the data folder of the repository.

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the edit data set
        """
        pd_edits_file = Path(data_root_dir, AggVersion.VERSION_DIR).joinpath(AggVersion.VERSION_EDITS)
        if pd_edits_file.is_file():
            return pd.read_pickle(pd_edits_file)
        else: 
            return None

