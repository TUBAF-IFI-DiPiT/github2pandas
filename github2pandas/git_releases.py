import pandas as pd
from pathlib import Path
import github

from .utility import Utility

class GitReleases():
    """
    Class to aggregate git releases.

    Attributes
    ----------
    GIT_RELEASES_DIR : str
        Git releases dir where all files are saved in.
    GIT_RELEASES : str
        Pandas table file for git releases data.

    Methods
    -------
    extract_git_releases_data(git_release, users_ids, data_root_dir)
        Extracting general git release data.
    generate_git_releases_pandas_tables(repo, data_root_dir, check_for_updates=True)
        Extracting the complete git releases data from a repository.
    get_git_releases(data_root_dir, filename=GIT_RELEASES)
        Get a genearted pandas table.
    
    """

    GIT_RELEASES_DIR = "Issues"
    GIT_RELEASES = "pdReleases.p"

    @staticmethod
    def extract_git_releases_data(git_release, users_ids, data_root_dir):
        """
        extract_git_releases_data(git_release, users_ids, data_root_dir)

        Extracting general git release data.

        Parameters
        ----------
        GitRelease: GitRelease
            GitRelease object from pygithub.
        users_ids: dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir: str
            Data root directory for the repository.

        Returns
        -------
        dict
            Dictionary with the extracted general git release data.

        Notes
        -----
            PyGithub GitRelease object structure: https://pygithub.readthedocs.io/en/latest/github_objects/GitRelease.html

        """

        git_releases_data = {}
        git_releases_data["id"] = git_release.id
        git_releases_data["body"] = git_release.body
        git_releases_data["title"] = git_release.title
        git_releases_data["tag_name"] = git_release.tag_name
        git_releases_data["target_commitish"] = git_release.target_commitish
        git_releases_data["draft"] = git_release.draft
        git_releases_data["prerelease"] = git_release.prerelease
        if not git_release.author == github.GithubObject.NotSet:
            git_releases_data["author"] = Utility.extract_user_data(git_release.author, users_ids, data_root_dir)
        git_releases_data["created_at"] = git_release.created_at
        git_releases_data["published_at"] = git_release.published_at
        return git_releases_data

    @staticmethod
    def generate_git_releases_pandas_tables(repo, data_root_dir, check_for_updates=True):
        """
        generate_git_releases_pandas_tables(repo, data_root_dir, check_for_updates=True)

        Extracting the complete git releases data from a repository.

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.
        data_root_dir: str
            Data root directory for the repository.
        check_for_updates: bool, default=True
            Check first if there are any new git releases.
        
        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        
        git_releases = repo.get_releases()
        if check_for_updates:
            old_git_releases = GitReleases.get_git_releases(data_root_dir)
            if not Utility.check_for_updates_paginated(git_releases, old_git_releases):
                return

        git_releases_dir = Path(data_root_dir, GitReleases.GIT_RELEASES_DIR)
        users_ids = Utility.get_users_ids(data_root_dir)
        git_releases_list = []
        for git_release in git_releases:
            git_release_data = GitReleases.extract_git_releases_data(git_release, users_ids, data_root_dir)
            git_releases_list.append(git_release_data)
        Utility.save_list_to_pandas_table(git_releases_dir, GitReleases.GIT_RELEASES, git_releases_list)
    
    @staticmethod
    def get_git_releases(data_root_dir, filename=GIT_RELEASES):
        """
        get_git_releases(data_root_dir, filename=GIT_RELEASES)

        Get a genearted pandas table.

        Parameters
        ----------
        data_root_dir: str
            Data root directory for the repository.
        filename: str, default=GIT_RELEASES
            Pandas table file for git releases data

        Returns
        -------
        DataFrame
            Pandas DataFrame which can includes the desired data

        """

        git_releases_dir = Path(data_root_dir, GitReleases.GIT_RELEASES_DIR)
        pd_git_releases_file = Path(git_releases_dir, filename)
        if pd_git_releases_file.is_file():
            return pd.read_pickle(pd_git_releases_file)
        else:
            return pd.DataFrame()