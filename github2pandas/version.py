import os
import sqlite3
import pickle
import pandas as pd
import pygit2 as git2
import git
import git2net
import shutil
from pathlib import Path
import stat
import numpy
from .utility import Utility

class Version():
    """
    Class to aggregate Version

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
    VERSION_BRANCHES : str
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
    clone_repository(repo, data_root_dir, github_token=None)
        Cloning repository from git.
    generate_data_base(data_root_dir)
        Extracting version data from a local repository and storing them in a mysql data base.
    generate_version_pandas_tables(repo, data_root_dir)
        Extracting edits and commits in a pandas table.
    define_unknown_users(user_list, data_root_dir)
        Define unknown users in commits pandas table.
    get_unknown_users(data_root_dir)
        Get all unknown users in from commits.
    get_version(data_root_dir, filename=VERSION_COMMITS)
        Get the generated pandas table.

    """  

    VERSION_DIR = "Versions"
    VERSION_REPOSITORY_DIR = "repo"
    VERSION_COMMITS = "pdCommits.p"
    VERSION_EDITS = "pdEdits.p"
    VERSION_BRANCHES = "pdBrances.p"
    VERSION_DB = "Versions.db"
    no_of_proceses = 1

    COMMIT_DELETEABLE_COLUMNS = ['author_email', 'author_name', 'committer_email', 'author_date', 'author_timezone', 'commit_message_len', 'project_name', 'merge']

    COMMIT_RENAMING_COLUMNS = {'hash':'commit_sha', 'committer_date': 'commited_at', 'parents': 'parent_sha'}

    EDIT_RENAMING_COLUMNS = {'commit_hash':'commit_sha'}

    @staticmethod
    def handleError(func, path, exc_info):
        """
        handleError(func, path, exc_info)

        Error handler function which will try to change file permission and call the calling function again.

        Parameters
        ----------
        func : Function
            Calling function.
        path : str
            Path of the file which causes the Error.
        exc_info : str
            Execution information.
        
        """
        
        print('Handling Error for file ' , path)
        print(exc_info)
        # Check if file access issue
        if not os.access(path, os.W_OK):
            # Try to change the permision of file
            os.chmod(path, stat.S_IWUSR)
            # call the calling function again
            func(path)

    @staticmethod
    def clone_repository(repo, data_root_dir, github_token=None):
        """
        Clone_repository(repo, data_root_dir, github_token=None)

        Cloning repository from git.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        data_root_dir : str
            Repo dir of the project.
        github_token : str
            Token string.

        Notes
        -----
            Pygit2 documentation: https://github.com/libgit2/pygit2
        
        """
        
        git_repo_name = repo.name
        git_repo_owner = repo.owner.login
        
        version_folder = Path(data_root_dir, Version.VERSION_DIR)
        version_folder.mkdir(parents=True, exist_ok=True)

        repo_dir = version_folder.joinpath(Version.VERSION_REPOSITORY_DIR)
        if repo_dir.exists ():
            shutil.rmtree(repo_dir.resolve(), onerror=Version.handleError)

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
                try:
                    r.git.branch('--track', branch_name,
                                'remotes/origin/'+branch_name)
                except Exception:
                    print(" -> An exception occurred")

    @staticmethod
    def generate_data_base(data_root_dir):
        """
        generate_data_base(data_root_dir)

        Extracting version data from a local repository and storing them in a mysql data base.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        
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
        
        version_folder = Path(data_root_dir, Version.VERSION_DIR)
        version_folder.mkdir(parents=True, exist_ok=True)
        repo_dir = version_folder.joinpath(Version.VERSION_REPOSITORY_DIR)
        sqlite_db_file = version_folder.joinpath(Version.VERSION_DB)

        if os.path.exists(sqlite_db_file):
            os.remove(sqlite_db_file)

        git2net.mine_git_repo(repo_dir, sqlite_db_file,
                              extract_complexity=True,
                              extract_text=True,
                              no_of_processes=Version.no_of_proceses,
                              all_branches=True,
                              max_modifications=1000)

    @staticmethod
    def generate_version_pandas_tables(repo, data_root_dir):
        """
        generate_version_pandas_tables(repo, data_root_dir)

        Extracting edits and commits in a pandas table.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        data_root_dir: str
            Data root directory for the repository.

        """

        Version.generate_data_base(data_root_dir)

        version_folder = Path(data_root_dir, Version.VERSION_DIR)
        sqlite_db_file = version_folder.joinpath(Version.VERSION_DB)
        print("1")
        db = sqlite3.connect(sqlite_db_file)
        pd_commits = pd.read_sql_query("SELECT * FROM commits", db)
        pd_edits = pd.read_sql_query("SELECT * FROM edits", db)

        pd_commits.rename(columns=Version.COMMIT_RENAMING_COLUMNS, inplace = True)
        pd_commits.drop(columns=Version.COMMIT_DELETEABLE_COLUMNS, axis = 1, inplace = True)
        pd_commits = Utility.apply_datetime_format(pd_commits, 'commited_at')

        pd_edits.rename(columns=Version.EDIT_RENAMING_COLUMNS, inplace = True)

        pd_edits = pd_edits.astype({'total_added_lines' : 'int', 'total_removed_lines' : 'int'})

        # Embed author uuid
        users_ids = Utility.get_users_ids(data_root_dir)
        pd_commits['author'] = ""
        pd_commits['committer'] = ""
        commiter_list = pd_commits.committer_name.unique()
        for commiter_name in commiter_list:
            if commiter_name == "GitHub":
                pd_selected_commits = pd_commits[pd_commits.committer_name == commiter_name]
                for index, row in pd_selected_commits.iterrows():
                    author_id = Utility.extract_author_data_from_commit(repo, row.commit_sha, 
                                                                 users_ids, data_root_dir)   
                    committer_id = Utility.extract_committer_data_from_commit(repo, row.commit_sha, 
                                                                        users_ids, data_root_dir)   
                    pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'author'] = author_id   
                    pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'committer'] = committer_id 
                    if (author_id is None) and (committer_id is None):
                        pd_commits.loc[pd_commits.commit_sha == row.commit_sha, 'unknown_user'] = row.committer_name

            else:
                commit_sha = pd_commits[pd_commits.committer_name == commiter_name].iloc[0].commit_sha 
                author_id = Utility.extract_author_data_from_commit(repo, commit_sha, 
                                                                    users_ids, data_root_dir)   
                committer_id = Utility.extract_committer_data_from_commit(repo, commit_sha, 
                                                                    users_ids, data_root_dir)   
                pd_commits.loc[pd_commits.committer_name == commiter_name, 'author'] = author_id   
                pd_commits.loc[pd_commits.committer_name == commiter_name, 'committer'] = committer_id 
                if (author_id is None) and (committer_id is None):
                    pd_commits.loc[pd_commits.committer_name == commiter_name, 'unknown_user'] = commiter_name 
        pd_commits.drop(['committer_name'], axis=1, inplace=True)  

        users = Utility.get_users(data_root_dir)
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
        tags = repo.get_tags()
        for tag in tags:
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
        
        pd_commits_file = Path(version_folder, Version.VERSION_COMMITS)
        with open(pd_commits_file, "wb") as f:
            pickle.dump(pd_commits, f)

        pd_edits_file = Path(version_folder, Version.VERSION_EDITS)
        with open(pd_edits_file, "wb") as f:
            pickle.dump(pd_edits, f)

        pd_branches_file = Path(version_folder, Version.VERSION_BRANCHES)
        with open(pd_branches_file, "wb") as f:
            pickle.dump(pd_Branches, f)          

    @staticmethod
    def define_unknown_users(user_dict, data_root_dir):
        """
        define_unknown_users(user_dict, data_root_dir)

        Define unknown users in commits pandas table.

        Parameters
        ----------
        user_dict: dict
            Dictionary which contains users. 
        data_root_dir : str
            Data root directory for the repository.

        Notes
        -----
        Example User: {"unknown_user": "real user node id"}
        If the real user node id does not exist in the users table then a new user will be created
        
        """
        pd_commits = Version.get_version(data_root_dir)
        if "unknown_user" in pd_commits:
            unknown_user_commits = pd_commits.loc[pd_commits.unknown_user.notna()]
            unknown_users = unknown_user_commits.unknown_user.unique()
            for unknown_user in unknown_users:
                uuid = Utility.define_unknown_user(user_dict,unknown_user,data_root_dir)
                if uuid is not None:
                    pd_commits.loc[pd_commits.unknown_user == unknown_user, 'author'] = uuid
                    pd_commits.loc[pd_commits.unknown_user == unknown_user, 'committer'] = uuid
                    pd_commits.loc[pd_commits.unknown_user == unknown_user, 'unknown_user'] = numpy.NaN

            version_folder = Path(data_root_dir, Version.VERSION_DIR)
            pd_commits_file = Path(version_folder, Version.VERSION_COMMITS)
            with open(pd_commits_file, "wb") as f:
                pickle.dump(pd_commits, f)
        
    @staticmethod
    def get_unknown_users(data_root_dir):
        """
        get_unknown_users(data_root_dir)

        Get all unknown users in from commits.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.

        Returns
        -------
        List
            List of unknown user names
        
        """
        pd_commits = Version.get_version(data_root_dir)
        if "unknown_user" in pd_commits:
            unknown_user_commits = pd_commits.loc[pd_commits.unknown_user.notna()]
            unknown_users = unknown_user_commits.unknown_user.unique()
            return list(unknown_users)

    @staticmethod
    def get_version(data_root_dir, filename=VERSION_COMMITS):
        """
        get_version(data_root_dir, filename=VERSION_COMMITS)

        Get the generated pandas table.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        filename : str, default=VERSION_COMMITS
            Pandas table file for commits or edits.

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the commit or edit data set
        
        """
        
        workflows_dir = Path(data_root_dir, Version.VERSION_DIR)
        pd_workflows_file = Path(workflows_dir, filename)
        if pd_workflows_file.is_file():
            return pd.read_pickle(pd_workflows_file)
        else:
            return pd.DataFrame()
