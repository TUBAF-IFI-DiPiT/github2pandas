from pathlib import Path
from pandas import DataFrame, read_pickle
# github imports
from github import GithubObject
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
from github.GitRelease import GitRelease as GitHubGitRelease
# github2pandas imports
from github2pandas.core import Core
from github2pandas.utility import progress_bar

class GitReleases(Core):
    """
    Class to aggregate git releases.

    Attributes
    ----------
    GIT_RELEASES_DIR : str
        Git releases dir where all files are saved in.
    GIT_RELEASES : str
        Pandas table file for git releases data.
    git_releases_df : DataFrame
        Pandas DataFrame object with git releases data.
    
    Methods
    -------
    __init__(self, github_connection, repo, data_root_dir, request_maximum)
        Initial git releases object with general information.
    generate_pandas_tables(check_for_updates=False)
        Extracting the complete git releases data from a repository.
    extract_git_releases_data(git_release)
        Extracting general git release data.
    get_git_releases(data_root_dir)
        Get the git releases pandas dataframe.
    
    """

    GIT_RELEASES_DIR = "Releases"
    GIT_RELEASES = "pdReleases.p"

    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000) -> None:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum)

        Initial git releases object with general information.

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
            Path(data_root_dir, GitReleases.GIT_RELEASES_DIR),
            request_maximum
        )

    @property
    def git_releases_df(self):
        return GitReleases.get_git_releases(self.data_root_dir)

    def generate_pandas_tables(self, check_for_updates:bool = False):
        """
        generate_pandas_tables(self, check_for_updates=False)

        Extracting the complete git releases data from a repository.

        Parameters
        ----------
        check_for_updates : bool, default=True
            Check first if there are any new git releases information.
        
        """
        git_releases = self.repo.get_releases()
        total_count = self.get_save_total_count(git_releases)
        if total_count == 0:
            return
        if check_for_updates:
            old_git_releases = self.git_releases_df
            if not self.check_for_updates_paginated(git_releases, total_count, old_git_releases):
                print("No new Git Releases information!")
                return
        git_releases_list = []
        for i in progress_bar(range(total_count), "Git Releases: "):
            # git release data
            git_release = self.get_save_api_data(git_releases, i)
            git_release_data = self.extract_git_releases_data(git_release)
            git_releases_list.append(git_release_data)
        git_releases_df = DataFrame(git_releases_list)
        self.save_pandas_data_frame(GitReleases.GIT_RELEASES, git_releases_df)
    
    def extract_git_releases_data(self, git_release:GitHubGitRelease):
        """
        extract_git_releases_data(git_release)

        Extracting general git release data.

        Parameters
        ----------
        git_release : GitHubGitRelease
            GitRelease object from pygithub.

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
        if not git_release._author == GithubObject.NotSet:
            git_releases_data["author"] = self.extract_user_data(git_release.author)
        git_releases_data["created_at"] = git_release.created_at
        git_releases_data["published_at"] = git_release.published_at
        return git_releases_data

    @staticmethod
    def get_git_releases(data_root_dir:Path):
        """
        get_git_releases(data_root_dir)

        Get the git releases pandas dataframe.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can includes the desired data

        """
        git_releases_dir = Path(data_root_dir, GitReleases.GIT_RELEASES_DIR)
        pd_git_releases_file = Path(git_releases_dir, GitReleases.GIT_RELEASES)
        if pd_git_releases_file.is_file():
            return read_pickle(pd_git_releases_file)
        else:
            return DataFrame()