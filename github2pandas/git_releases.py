import logging
from pathlib import Path
import pandas as pd
# github imports
from github import GithubObject
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
from github.GitRelease import GitRelease as GitHubGitRelease
# github2pandas imports
from github2pandas.core import Core

class GitReleases(Core):
    """
    Class to aggregate git releases.

    Attributes
    ----------
    git_releases_df : DataFrame
        Pandas DataFrame object with git releases data.
    
    Methods
    -------
    __init__(self, github_connection, repo, data_root_dir, request_maximum = 40000, log_level=logging.INFO)
        Initializes git releases object with general information.
    generate_pandas_tables(self, check_for_updates=False)
        Generates pandas tables for git releases data.
    __extract_git_releases_data(self, git_release)
        Extracts general git releases data.
    
    """

    class Files(Core.Files):
        """
        A file class that holds all file names and the folder name.

        Attributes
        ----------
        DATA_DIR : str
            Folder name for this module.
        GIT_RELEASES : str
            Filename of the git releases pandas table.

        """
        DATA_DIR = "Releases"
        GIT_RELEASES = "Releases.p"

    def __init__(self, github_connection: Github, repo: GitHubRepository, data_root_dir: Path, request_maximum: int = 40000, log_level: int = logging.INFO) -> None:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum = 40000, log_level=logging.INFO)

        Initializes git releases object with general information.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.
        repo : GitHubRepository
            Repository object from pygithub.
        data_root_dir : Path
            Data root directory for the repository.
        request_maximum : int, default=40000
            Maximum amount of returned informations for a general api call.
        log_level : int
            Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET), default value is enumaration value logging.INFO    

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
            GitReleases.Files.DATA_DIR,
            request_maximum=request_maximum,
            log_level=log_level
        )

    @property
    def git_releases_df(self) -> pd.DataFrame:
        """
        git_releases_df(self)

        Pandas DataFrame object with git releases data.

        Returns
        -------
        pd.DataFrame
            DataFrame of git releases.
            
        """
        return Core.get_pandas_data_frame(self.current_dir,GitReleases.Files.GIT_RELEASES)

    def generate_pandas_tables(self, check_for_updates: bool = False) -> None:
        """
        generate_pandas_tables(self, check_for_updates=False)

        Generates pandas tables for git releases data from a repository.
        Checks first if there are any new git releases information in dependence of parameter check_for_updates.

        Parameters
        ----------
        check_for_updates : bool, default=False
            Determines whether update is necessary.
        
        """
        git_releases = self.save_api_call(self.repo.get_releases)
        total_count = self.get_save_total_count(git_releases)
        if total_count == 0:
            return
        if check_for_updates:
            old_git_releases = self.git_releases_df
            if not self.check_for_updates_paginated(git_releases, total_count, old_git_releases):
                self.logger.info("No new Git Releases information!")
                return
        git_releases_list = []
        for i in self.progress_bar(range(total_count), "Git Releases: "):
            # git release data
            git_release = self.get_save_api_data(git_releases, i)
            git_release_data = self.__extract_git_releases_data(git_release)
            git_releases_list.append(git_release_data)
        git_releases_df = pd.DataFrame(git_releases_list)
        self.save_pandas_data_frame(GitReleases.Files.GIT_RELEASES, git_releases_df)
    
    def __extract_git_releases_data(self, git_release: GitHubGitRelease) -> dict:
        """
        __extract_git_releases_data(self, git_release)

        Extracts general git releases data from pygithub GitRelease object.
        Returns dictionary with the extracted data.

        Parameters
        ----------
        git_release : GitHubGitRelease
            GitRelease object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted general git releases data.

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
