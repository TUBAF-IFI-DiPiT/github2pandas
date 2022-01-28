import logging
import os
import sqlite3
import pandas as pd
import pygit2 as git2
import git
import shutil
import numpy
from pathlib import Path
# github imports
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
# github2pandas imports
from github2pandas.core import Core

class Version(Core):
    """
    Class to aggregate Version

    Attributes
    ----------
    DATA_DIR : str
        Version dir where all files are saved in.
    REPOSITORY_DIR : str
        Folder of cloned repository.
    COMMITS : str
        Pandas table file for commits.
    EDITS : str
        Pandas table file for edit data per commit.
    BRANCHES : str
        Pandas table file for branch names.
    VERSION_DB : str
        MYSQL data base file containing version history.
    no_of_processes : int
        Number of processors used for crawling process.
    COMMIT_DELETEABLE_COLUMNS : list
        Commit colums from git2net which can be deleted.
    COMMIT_RENAMING_COLUMNS : dict
        Commit Colums from git2net which need to be renamed.
    EDIT_RENAMING_COLUMNS : dict
        Edit Colums from git2net which need to be renamed.

    Methods
    -------
    handleError(func, path, exc_info)
        Error handler function which will try to change file permission and call the calling function again.
    clone_repository(repo, data_root_dir, github_token=None, new_clone=False):
        Cloning repository from git.
    generate_data_base(data_root_dir)
        Extracting version data from a local repository and storing them in a mysql data base.
    generate_version_pandas_tables(repo, data_root_dir, check_for_updates=True)
        Extracting edits and commits in a pandas table.
    define_unknown_user(unknown_user_name, uuid, data_root_dir, new_user=False)
        Define unknown user in commits pandas table.
    get_unknown_users(data_root_dir)
        Get all unknown users in from commits.
    get_version(data_root_dir, filename=COMMITS)
        Get the generated pandas table.

    """  
    COMMIT_DELETEABLE_COLUMNS = ['author_email', 'author_name', 'committer_email', 'author_date', 'author_timezone', 'commit_message_len', 'project_name', 'merge']

    COMMIT_RENAMING_COLUMNS = {'hash':'commit_sha', 'committer_date': 'commited_at', 'parents': 'parent_sha'}

    EDIT_RENAMING_COLUMNS = {'commit_hash':'commit_sha'}

    class Files():
        DATA_DIR = "Versions"
        COMMITS = "Commits.p"
        EDITS = "Edits.p"
        BRANCHES = "Brances.p"
        REPOSITORY_DIR = "repo"
        VERSION_DB = "Versions.db"

        @staticmethod
        def to_list() -> list:
            return [
                Version.Files.COMMITS,
                Version.Files.EDITS,
                Version.Files.BRANCHES,
                {Version.Files.REPOSITORY_DIR:[Version.Files.VERSION_DB]}
            ]

        @staticmethod
        def to_dict() -> dict:
            return {Version.Files.DATA_DIR: Version.Files.to_list()}

    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000, log_level:int=logging.INFO, number_of_proceses:int = 1) -> None:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum)

        Initial pull request object with general information.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.
        repo : GitHubRepository
            Repository object from pygithub.
        data_root_dir : Path
            Data root directory for the repository.
        request_maximum : int, default=40000
            Maxmimum amount of returned informations for a general api call

        Notes
        -----
            PyGithub Github object structure: https://pygithub.readthedocs.io/en/latest/github.html
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        Core.__init__(
            self,
            github_connection,
            repo,
            data_root_dir,
            Version.Files.DATA_DIR,
            request_maximum=request_maximum,
            log_level=log_level
        )
        self.number_of_proceses = number_of_proceses
        self.repo_dir = self.current_dir.joinpath(Version.Files.REPOSITORY_DIR)
        self.sqlite_db_file = self.current_dir.joinpath(Version.Files.VERSION_DB)

    @property
    def commits_df(self):
        return Core.get_pandas_data_frame(self.current_dir, Version.Files.COMMITS)
    @property
    def edits_df(self):
        return Core.get_pandas_data_frame(self.current_dir, Version.Files.EDITS)
    @property
    def branches_df(self):
        return Core.get_pandas_data_frame(self.current_dir, Version.Files.BRANCHES)

    def generate_pandas_tables(self, check_for_updates=False):
        """
        generate_version_pandas_tables(repo, data_root_dir)

        Extracting edits and commits in a pandas table.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        data_root_dir: str
            Data root directory for the repository.
        check_for_updates : bool, default=True
            Check first if there are any new pull requests information.

        """

        # if check_for_updates:
        #     commits = self.save_api_call(self.repo.get_commits)
        #     total_count = self.get_save_total_count(commits)
        #     old_commits = self.commits_df
        #     if not self.check_for_updates_paginated(commits, total_count, old_commits):
        #         self.logger.info("No new Commit information!")
        #         return

        self.generate_data_base()

        db = sqlite3.connect(self.sqlite_db_file)
        pd_commits = pd.read_sql_query("SELECT * FROM commits", db)
        pd_edits = pd.read_sql_query("SELECT * FROM edits", db)

        pd_commits.rename(columns=self.COMMIT_RENAMING_COLUMNS, inplace = True)
        pd_commits.drop(columns=self.COMMIT_DELETEABLE_COLUMNS, axis = 1, inplace = True)
        pd_commits = self.apply_datetime_format(pd_commits, 'commited_at')
        pd_edits.rename(columns=self.EDIT_RENAMING_COLUMNS, inplace = True)
        pd_edits = pd_edits.fillna(value=0).astype({'total_added_lines' : 'int', 'total_removed_lines' : 'int'})

        # Embed author uuid
        pd_commits['author'] = ""
        pd_commits['committer'] = ""
        commiter_list = pd_commits.committer_name.unique()
        for commiter_name in self.progress_bar(commiter_list, "Version parse user:"):
            if commiter_name == "GitHub":
                pd_selected_commits = pd_commits[pd_commits.committer_name == commiter_name]
                for index, row in pd_selected_commits.iterrows():
                    author_id = self.extract_author_data_from_commit(row.commit_sha)   
                    committer_id = self.extract_committer_data_from_commit(row.commit_sha)   
                    pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'author'] = author_id   
                    pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'committer'] = committer_id 
                    if (author_id is None) and (committer_id is None):
                        users = Core.get_pandas_data_frame(self.repo_data_dir, Core.Files.USERS)
                        found = False
                        if "alias" in users:
                            users = users[users["alias"].notna()]
                            for index2, row2 in users.iterrows():
                                all_alias = row2["alias"]
                                if all_alias is not None:
                                    for alias in all_alias:
                                        if commiter_name == alias:
                                            pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'author'] = row2["anonym_uuid"] 
                                            pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'committer'] = row2["anonym_uuid"]
                                            found = True
                                            break
                                if found:
                                    break
                        if not found:
                            pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'unknown_user'] = row.committer_name
            else:
                commit_sha = pd_commits[pd_commits.committer_name == commiter_name].iloc[0].commit_sha 
                author_id = self.extract_author_data_from_commit(commit_sha)   
                committer_id = self.extract_committer_data_from_commit(commit_sha)   
                pd_commits.loc[pd_commits.committer_name == commiter_name, 'author'] = author_id   
                pd_commits.loc[pd_commits.committer_name == commiter_name, 'committer'] = committer_id 
                if (author_id is None) and (committer_id is None):
                    users = Core.get_pandas_data_frame(self.repo_data_dir, Core.Files.USERS)
                    found = False
                    if "alias" in users:
                        users = users[users["alias"].notna()]
                        for index, row in users.iterrows():
                            all_alias = row["alias"]
                            if all_alias is not None:
                                for alias in all_alias:
                                    if commiter_name == alias:
                                        pd_commits.loc[pd_commits.committer_name == commiter_name, 'author'] = row["anonym_uuid"] 
                                        pd_commits.loc[pd_commits.committer_name == commiter_name, 'committer'] = row["anonym_uuid"]
                                        found = True
                                        break
                            if found:
                                break
                    if not found:
                        pd_commits.loc[pd_commits.committer_name == commiter_name, 'unknown_user'] = commiter_name 
        pd_commits.drop(['committer_name'], axis=1, inplace=True)  

        users = Core.get_pandas_data_frame(self.repo_data_dir, Core.Files.USERS)
        if "unknown_user" in pd_commits:
            unknown_user_commits = pd_commits.loc[pd_commits.unknown_user.notna()]
            unknown_users = unknown_user_commits.unknown_user.unique()
            for unknown_user in unknown_users:
                if not users.empty:
                    for index, row in users.iterrows():
                        if (row["email"] == unknown_user) or (row["name"] == unknown_user) or (row["login"] == unknown_user):
                            pd_commits.loc[pd_commits.unknown_user == unknown_user, 'author'] = row["anonym_uuid"]
                            pd_commits.loc[pd_commits.unknown_user == unknown_user, 'committer'] = row["anonym_uuid"]
                            pd_commits.loc[pd_commits.unknown_user == unknown_user, 'unknown_user'] = numpy.NaN
        # Extract Tags
        pd_commits['tag'] = ""
        tags = self.save_api_call(self.repo.get_tags)
        tags_total_count = self.get_save_total_count(tags)
        for i in self.progress_bar(range(tags_total_count), "Version tags:   "):
            tag = self.get_save_api_data(tags, i)
            pd_commits.loc[pd_commits.commit_sha == tag.commit.sha, 'tag'] = tag.name   
            

        # Extract branch names
        branch_entries = [x.split(',') for x in pd_commits.branches.values]
        branch_list = [item for sublist in branch_entries for item in sublist]
        branches = list(set(branch_list))
        pd_Branches = pd.DataFrame(branches, columns =['branch_names'])

        branch_ids = []
        for index, row in pd_commits.iterrows():
            idxs = [branches.index(branch_name) for branch_name in row.branches.split(',')]
            branch_ids.append(idxs)
        pd_commits['branch_ids'] = branch_ids
        pd_commits.drop(['branches'], axis = 1, inplace=True)
        
        self.save_pandas_data_frame(Version.Files.COMMITS, pd_commits)
        self.save_pandas_data_frame(Version.Files.EDITS, pd_edits)
        self.save_pandas_data_frame(Version.Files.BRANCHES, pd_Branches)      

    def generate_data_base(self, new_extraction=False):
        """
        generate_data_base(data_root_dir)

        Extracting version data from a local repository and storing them in a mysql data base.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        new_extraction: bool, default = False
            Start a new complete extraction run
        
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
        self.current_dir.mkdir(parents=True, exist_ok=True)
        if new_extraction & os.path.exists(self.sqlite_db_file):
            os.remove(self.sqlite_db_file)
        # overwrite git2net progress bar
        import tqdm
        def version_progress_bar(iterable=None, total:int=None, desc:str="", **kwargs):
            if iterable is None:
                if total is not None:
                    iterable = range(total)
                else:
                    logging.error("Error in progressbar for version")
                    return
            return self.progress_bar(iterable, f"Version {desc}:")
        tqdm.tqdm = version_progress_bar
        import git2net
        git2net.mine_git_repo(self.repo_dir, self.sqlite_db_file,
                                extract_complexity=True,
                                extract_text=True,
                                no_of_processes=self.number_of_proceses,
                                all_branches=True,
                                max_modifications=1000)

    def clone_repository(self, github_token=None, new_clone=False):
        """
        Clone_repository(repo, data_root_dir, github_token=None)

        Cloning repository from git.

        Parameters
        ----------
        github_token : str
            Token string.
        new_clone : bool, default=True
            Initiating a completely new clone of the repository

        Notes
        -----
            Pygit2 documentation: https://github.com/libgit2/pygit2
        
        """ 
        git_repo_name = self.repo.name
        git_repo_owner = self.repo.owner.login
        self.current_dir.mkdir(parents=True, exist_ok=True)
        # Issue  #62
        #if (repo_dir.exists ()) & (not new_clone):
        #    old_path = Path.cwd()
        #    os.chdir(repo_dir)
        #    try:
        #        git2output = subprocess.check_output(["git", "pull"])
        #    except:
        #        print("This repository is empty, git pull generates an error")
        #        print('git said:', git2output)
        #    os.chdir(old_path)
        #    return
        if self.repo_dir.exists ():
            shutil.rmtree(self.repo_dir.resolve(), onerror=self.file_error_handling)
        callbacks = None
        if github_token:
            callbacks = git2.RemoteCallbacks(
                git2.UserPass(github_token, 'x-oauth-basic'))
        repo_ref = f"https://github.com/{git_repo_owner}/{git_repo_name}"
        repo = git2.clone_repository(repo_ref, self.repo_dir, callbacks=callbacks)
        existing_branches = list(repo.branches)
        r = git.Repo.init(self.repo_dir)
        for branch_name in repo.references:
            branch_pattern = ['refs/heads/', 'refs/remotes/origin/']
            for pattern in branch_pattern:
                branch_name = branch_name.replace(pattern, '')
            if branch_name != 'HEAD' and branch_name not in existing_branches:
                try:
                    r.git.branch('--track', branch_name,
                                'remotes/origin/'+branch_name)
                except Exception:
                    self.logger.debug(" -> An exception occurred")
