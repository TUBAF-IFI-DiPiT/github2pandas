import json
import logging
import os
from pathlib import Path
import numpy
import pandas as pd
# github imports
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
from github2pandas.core import Core
from github2pandas.git_releases import GitReleases
from github2pandas.issues import Issues
from github2pandas.pull_requests import PullRequests
from github2pandas.repository import Repository
from github2pandas.version import Version
from github2pandas.workflows import Workflows

class GitHub2Pandas():
    """
    An object of the class GitHub2Pandas is required to use the program package. 
    The object obtains general informations about the Github repository: github access token and
    path to a root directory. The class provides methods for accessing the repository.

    Attributes
    ----------
    __github_token : str
        Github access token.
    github_connection : Github
        Github object from pygithub.
    data_root_dir : Path 
        Root directory of the repository.
    request_maximum : int
        Maximum amount of returned informations for a general api call, default=40000.
    log_level : int
        Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET) 
    __core : Core
        Core object, contains common information about GitHub2Pandas request.

    Methods
    -------
    __init__(self, github_token, data_root_dir, request_maximum = 40000, log_level=logging.INFO)
        Initializes Github2Pandas object with general informations.
    generate_git_releases_pandas_tables(self, repo)
        Generates git releases pandas tables for given Github repository depending on extraction parameters. 
    generate_issues_pandas_tables(self, repo, issues_params=Issues.Params())
        Generates issues pandas tables for given Github repository depending on extraction parameters.
    generate_pull_requests_pandas_tables(self, repo, pull_requests_params=PullRequests.Params())
        Generates pull requests pandas tables for given Github repository depending on extraction parameters.
    generate_repository_pandas_tables(self, repo, repository_params=Repository.Params())
        Generates repository pandas tables for given Github repository depending on extraction parameters.
    generate_version_pandas_tables(self, repo, number_of_processes=os.cpu_count())
        Generates version pandas tables for given Github repository depending on extraction parameters.
    generate_workflows_pandas_tables(self, repo, workflows_params=Workflows.Params())
        Generates workflows pandas tables for given Github repository depending on extraction parameters.
    generate_pandas_tables(self, repo, extraction_params)
        Generates pandas tables for given Github repository depending on extraction parameters.
    get_repos(self, whitelist_patterns=None, blacklist_patterns=None)
        Returns repositories corresponding with the pattern in the given lists.
    get_repo(self, repo_owner, repo_name)
        Gets a repository by owner and name.
    save_tables_to_excel(repo_data_dir, filename)
        Converts all pandas tables into one excel file.
    get_pandas_data_frame(repo_data_dir, data_dir_name, filename)
        Returns a pandas data frame stored in file.    
    get_unknown_users(repo_data_dir)
        Get all unknown users from commits.  
    define_unknown_user(unknown_user_name, uuid, data_root_dir, new_user=False)
        Define unknown user in commits pandas table.
    get_repo_informations(data_root_dir)
        Gets repository data (owner and name) as list of strings.

    """
    REPOSITORIES_KEY = "repos"

    class Params(Core.Params):
        """
        A parameter class that holds all possible parameters for the data extraction.

        Methods
        -------
        __init__(self, git_releases, issues_params, pull_requests_params, repository_params, version, workflows_params)
            Initializes all parameters with a default.
        
        """
        def __init__(self, git_releases: bool = True, issues_params: Issues.Params = Issues.Params(), pull_requests_params: PullRequests.Params = PullRequests.Params(), repository_params: Repository.Params = Repository.Params(), version: bool = True, workflows_params: Workflows.Params = Workflows.Params()) -> None:
            """
            __init__(self, git_releases, issues_params, pull_requests_params, repository_params, version, workflows_params)
       
            Initializes all parameters with a default.

            Parameters
            ----------
            git_releases : bool, default=True
                Extract git releases?
            issues_params : bool, default=Issues.Params()
                Extract issues with these parameters.
            pull_requests_params : bool, default=PullRequests.Params()
                Extract pull requests with these parameters.
            git_releases : bool, default=True
                Extract git_releases?
            repository_params : bool, default=Repository.Params()
                Extract repository with these parameters.
            version : bool, default=True
                Extract version?
            workflows_params : bool, default=Workflows.Params()
                Extract workflows with these parameters.
            
            """
            self.git_releases = git_releases
            self.issues_params = issues_params
            self.pull_requests_params = pull_requests_params
            self.repository_params = repository_params
            self.version = version
            self.workflows_params = workflows_params

    class Files(Core.Files):
        """
        A file class that holds all file names and the folder name.

        Attributes
        ----------
        REPOS : str
            Filename of the repos json file.
        GIT_RELEASES : GitReleases.Files
            Folder and files for git releases.
        ISSUES : Issues.Files
            Folder and files for issues.
        PULL_REQUESTS : PullRequests.Files
            Folder and files for pull requests.
        REPOSITORY : Repository.Files
            Folder and files for repository.
        VERSION : Version.Files
            Folder and files for version.
        WORKFLOWS : Workflows.Files
            Folder and files for workflows.
        USER : Core.UserFiles
            User pandas files.

        Methods
        -------
        to_list()
            Returns a list of all filenames.
        to_dict()
            Returns a dict with the folder as key and the list of all filenames as value.
        
        """
        REPOS = "Repos.json"
        GIT_RELEASES = GitReleases.Files
        ISSUES = Issues.Files
        PULL_REQUESTS = PullRequests.Files
        REPOSITORY = Repository.Files
        VERSION = Version.Files
        WORKFLOWS = Workflows.Files
        USER = Core.UserFiles

        @classmethod
        def to_dict(cls) -> dict:
            """
            to_dict(cls)
            
            Returns a dict with the folder as key and the list of all pandas filenames as value.
            
            Returns
            -------
            dict
                Dictionary with the folder as key and the list of all pandas filenames as value.

            """
            files = {}
            for var, value in vars(cls).items():
                if not isinstance(value,str):
                    if hasattr(value, "DATA_DIR"):
                        files[value.DATA_DIR] = value.to_list()
            return files

    def __init__(self, github_token: str, data_root_dir: Path, request_maximum: int = 40000, log_level: int = logging.INFO) -> None:
        """
        __init__(self, github_token, data_root_dir, request_maximum = 40000, log_level=logging.INFO)

        Initializes Github2Pandas object with general informations.

        Parameters
        ----------
        github_token : str
            Github access token.
        data_root_dir : Path
            Data root directory for the repository.
        request_maximum : int, default=40000
            Maxmimum amount of returned informations for a general api call.
        log_level : int
            Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET) .

        Notes
        -----
            PyGithub Github object structure: https://pygithub.readthedocs.io/en/latest/github.html
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        self.__github_token = github_token
        self.github_connection = Github(github_token, per_page=100)
        data_root_dir.mkdir(parents=True, exist_ok=True)
        self.data_root_dir = data_root_dir
        self.request_maximum = request_maximum
        self.log_level = log_level
        self.__core = Core(self.github_connection,None,self.data_root_dir,None,log_level=log_level)

    def generate_git_releases_pandas_tables(self, repo: GitHubRepository) -> GitReleases:
        """
        generate_git_releases_pandas_tables(self, repo)

        Generates git releases pandas tables for given Github repository depending on extraction parameters.

        Parameters
        ----------
        repo : GitHubRepository
            Repository object from pygithub.

        Returns
        -------
        GitReleases
            A GitReleases object.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        git_releases = GitReleases(self.github_connection,repo,self.data_root_dir,self.request_maximum,self.log_level)
        try:
            git_releases.generate_pandas_tables()
        except Exception as e:
            self.__core.logger.error("Error in releases. Releases are not extracted!", exc_info=e)
        return git_releases

    def generate_issues_pandas_tables(self, repo: GitHubRepository, issues_params: Issues.Params = Issues.Params()) -> Issues:
        """
        generate_issues_pandas_tables(self, repo, issues_params=Issues.Params())

        Generates issues pandas tables for given Github repository depending on extraction parameters.

        Parameters
        ----------
        repo : GitHubRepository
            Repository object from pygithub.
        issues_params : Issues.Params, default=Issues.Params()
            Parameters that define what should be extracted.

        Returns
        -------
        Issues
            A Issues object.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        issues = Issues(self.github_connection,repo,self.data_root_dir,self.request_maximum,self.log_level)
        try:
            issues.generate_pandas_tables(params=issues_params)
        except Exception as e:
            self.__core.logger.error("Error in issues. Issues are not extracted!", exc_info=e)
        return issues
        
    def generate_pull_requests_pandas_tables(self, repo: GitHubRepository, pull_requests_params: PullRequests.Params = PullRequests.Params()) -> PullRequests:
        """
        generate_pull_requests_pandas_tables(self, repo, pull_requests_params=PullRequests.Params())

        Generates pull requests pandas tables for given Github repository depending on extraction parameters.

        Parameters
        ----------
        repo : GitHubRepository
            Repository object from pygithub.
        pull_requests_params : PullRequests.Params, default=PullRequests.Params()
            Parameters that define what should be extracted.

        Returns
        -------
        PullRequests
            A PullRequests object.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        pull_requests = PullRequests(self.github_connection,repo,self.data_root_dir,self.request_maximum,self.log_level)
        try:
            pull_requests.generate_pandas_tables(params=pull_requests_params)
        except Exception as e:
            self.__core.logger.error("Error in pull requests. Pull requests are not extracted!", exc_info=e)
        return pull_requests

    def generate_repository_pandas_tables(self, repo: GitHubRepository, repository_params: Repository.Params = Repository.Params()) -> Repository:
        """
        generate_repository_pandas_tables(self, repo, repository_params=Repository.Params())

        Generates repository pandas tables for given Github repository depending on extraction parameters.

        Parameters
        ----------
        repo : GitHubRepository
            Repository object from pygithub.
        repository_params : Repository.Params, default=Repository.Params()
            Parameters that define what should be extracted.

        Returns
        -------
        Repository
            A Repository object.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        repository = Repository(self.github_connection,repo,self.data_root_dir,self.request_maximum,self.log_level)
        try:
            repository.generate_pandas_tables(params=repository_params)
        except Exception as e:
            self.__core.logger.error("Error in repository. Repository is not extracted!", exc_info=e)
        return repository

    def generate_version_pandas_tables(self, repo: GitHubRepository, number_of_processes: int = os.cpu_count()) -> Version:
        """
        generate_version_pandas_tables(self, repo, number_of_processes=os.cpu_count())

        Generates version pandas tables for given Github repository depending on extraction parameters.

        Parameters
        ----------
        repo : GitHubRepository
            Repository object from pygithub.
        number_of_processes : int, default=os.cpu_count()
            Number of processes to use

        Returns
        -------
        Version
            A Version object.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        version = Version(self.github_connection,repo,self.data_root_dir,self.request_maximum,self.log_level, number_of_processes)
        try:
            version.clone_repository(self.__github_token)
            version.generate_pandas_tables()
        except Exception as e:
            self.__core.logger.error("Error in version. Version are not extracted!", exc_info=e)
        return version

    def generate_workflows_pandas_tables(self, repo: GitHubRepository, workflows_params: Workflows.Params = Workflows.Params()) -> Workflows:
        """
        generate_workflows_pandas_tables(self, repo, workflows_params=Workflows.Params())

        Generates workflows pandas tables for given Github repository depending on extraction parameters.

        Parameters
        ----------
        repo : GitHubRepository
            Repository object from pygithub.
        workflows_params : Workflows.Params, default=Workflows.Params()
            Parameters that define what should be extracted.

        Returns
        -------
        Workflows
            A Workflows object.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        workflows = Workflows(self.github_connection,repo,self.data_root_dir,self.request_maximum,self.log_level)
        try:
            workflows.generate_pandas_tables(params=workflows_params)
        except Exception as e:
            self.__core.logger.error("Error in workflows. Workflows are not extracted!", exc_info=e)
        return workflows

    def generate_pandas_tables(self, repo: GitHubRepository, params: Params = Params()) -> None:
        """
        generate_pandas_tables(self, repo, extraction_params)

        Generates pandas tables for given Github repository depending on extraction parameters.

        Parameters
        ----------
        repo : GitHubRepository
            Repository object from pygithub.
        params : Params, default=Params()
            Parameters that define what should be extracted.

        """
        if params.git_releases:
            git_releases = self.generate_git_releases_pandas_tables(repo)
        if params.issues_params.has_true():
            issues = self.generate_issues_pandas_tables(repo)
        if params.pull_requests_params.has_true():
            pull_requests = self.generate_pull_requests_pandas_tables(repo)
        if params.repository_params.has_true():
            repository = self.generate_repository_pandas_tables(repo)
        if params.version:
            version = self.generate_version_pandas_tables(repo)
        if params.workflows_params.has_true():
            workflows = self.generate_workflows_pandas_tables(repo)
     
    def get_repos(self, whitelist_patterns: list = None, blacklist_patterns: list = None) -> list:
        """
        get_repos(self, whitelist_patterns=None, blacklist_patterns=None)

        Returns a list of repositories whose names correspond with the pattern in the blacklist_patterns list
        and not correspond with the pattern in the blacklist_patterns list

        Parameters
        ----------
        whitelist_patterns : list
            the whitelist pattern of the desired repository.
        blacklist_patterns : list
            the blacklist pattern of the desired repository.
        
        Returns
        -------
        List
            List of Repository objects from pygithub.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        relevant_repos = []
        user = self.__core.save_api_call(self.github_connection.get_user)
        repos = self.__core.save_api_call(user.get_repos)
        repo_total_count = self.__core.get_save_total_count(repos)
        for i in self.__core.progress_bar(range(repo_total_count), "Repositories:   "):
            repo = self.__core.get_save_api_data(repos, i)
            whitelist_pass = False
            if whitelist_patterns == [] or whitelist_patterns == None:
                whitelist_pass = True
            else:
                for whitelist_pattern in whitelist_patterns:
                    if whitelist_pattern in repo.name:
                        whitelist_pass = True
                        break
            if whitelist_pass:
                blacklist_pass = True
                if blacklist_patterns != [] or blacklist_patterns is not None:
                    for blacklist_pattern in blacklist_patterns:
                        if blacklist_pattern in repo.name:
                            blacklist_pass = False
                            break
                if blacklist_pass:
                    repo_dir = Path(self.data_root_dir, repo.full_name)
                    repo_dir.mkdir(parents=True, exist_ok=True)
                    repo_file = Path(self.data_root_dir, GitHub2Pandas.Files.REPOS)
                    existing_repos = GitHub2Pandas.get_full_names_of_repositories(self.data_root_dir)
                    existing_repos.append(repo.full_name)
                    with open(repo_file, 'w') as json_file:
                        json.dump({GitHub2Pandas.REPOSITORIES_KEY: existing_repos}, json_file)
                    relevant_repos.append(repo)
        return relevant_repos
    
    def get_repo(self, repo_owner: str, repo_name: str) -> GitHubRepository:
        """
        get_repo(self, repo_owner, repo_name)

        Gets a repository by owner and name.

        Parameters
        ----------
        repo_owner : str
            the owner of the desired repository.
        repo_name : str
            the name of the desired repository.
        
        Returns
        -------
        GitHubRepository
            Repository object from pygithub.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        repo_file = Path(self.data_root_dir, GitHub2Pandas.Files.REPOS)
        existing_repos = GitHub2Pandas.get_full_names_of_repositories(self.data_root_dir)
        existing_repos.append(repo_owner + "/" + repo_name)
        with open(repo_file, 'w') as json_file:
            json.dump({GitHub2Pandas.REPOSITORIES_KEY: existing_repos}, json_file)
        return self.__core.save_api_call(self.github_connection.get_repo,repo_owner + "/" + repo_name)

    @staticmethod
    def save_tables_to_excel(repo_data_dir: Path, filename: str = "GitHub2Pandas") -> None:
        """
        save_tables_to_excel(repo_data_dir, filename)

        Converts all pandas tables into one excel file.

        Parameters
        ----------
        repo_data_dir : Path
            Path to repository
        filename : str
            Filename

        """
        writer = pd.ExcelWriter(Path(repo_data_dir,f'{filename}.xlsx'), engine='xlsxwriter')
        for folder, files in GitHub2Pandas.Files.to_dict().items():
            for file in files:
                if file.endswith(".p"):
                    df = GitHub2Pandas.get_pandas_data_frame(repo_data_dir,folder,file)
                    df.to_excel(writer, sheet_name=file[:-2])
        writer.save()

    @staticmethod
    def get_pandas_data_frame(repo_data_dir: Path, data_dir_name: str,  filename: str) -> pd.DataFrame:
        """
        get_pandas_data_frame(repo_data_dir, data_dir_name, filename)

        Returns a pandas data frame stored in file, if necessary creates one.

        Parameters
        ----------
        repo_data_dir : Path
            Path to repository
        data_dir_name : str
            Name of a data directory
        filename : str
            Filename

        Returns
        -------
        pd.DataFrame
            Returns pandas data frame stored in file if file exist, otherwise a new data frame object.

        """
        return Core.get_pandas_data_frame(Path(repo_data_dir,data_dir_name), filename)
    
    @staticmethod
    def get_unknown_users(repo_data_dir: str):
        """
        get_unknown_users(repo_data_dir)

        Get all unknown users from commits.

        Parameters
        ----------
        repo_data_dir : str
            Data root directory for the repository.

        Returns
        -------
        List
            List of unknown user names
        
        """
        pd_commits = Version.get_pandas_data_frame(Path(repo_data_dir,Version.Files.DATA_DIR), Version.Files.COMMITS)
        if "unknown_user" in pd_commits:
            unknown_user_commits = pd_commits.loc[pd_commits.unknown_user.notna()]
            unknown_users = unknown_user_commits.unknown_user.unique()
            return list(unknown_users)
    
    @staticmethod
    def define_unknown_user(repo_data_dir: str, unknown_user_name: str, uuid: str, new_user: bool = False):
        """
        define_unknown_user(unknown_user_name, uuid, data_root_dir, new_user=False)

        Define unknown user in commits pandas table.

        Parameters
        ----------
        unknown_user_name: str
            Name of unknown user. 
        uuid: str
            Uuid can be the anonym uuid of another user or random uuid for a new user. 
        new_user : bool, default=False
            A complete new user with uuid will be generated.

        """
        core = Core(None,None,repo_data_dir,None)
        pd_commits = Version.get_pandas_data_frame(Path(repo_data_dir,Version.Files.DATA_DIR), Version.Files.COMMITS)
        if "unknown_user" in pd_commits:
            unknown_users = pd_commits.unknown_user.unique()
            if unknown_user_name in unknown_users:
                users = Core.get_pandas_data_frame(repo_data_dir, Core.UserFiles.USERS)
                p_user = users.loc[users.anonym_uuid == uuid]
                new_uuid = None
                if not p_user.empty:
                    alias = []
                    user = p_user.iloc[0]
                    if "alias" in user:
                        user_alias = user["alias"]
                        if not pd.isnull(user_alias) and (user_alias is not None):
                            alias = user_alias
                    if not unknown_user_name in alias:
                        alias.append(unknown_user_name)
                    users.loc[users.anonym_uuid == uuid, 'alias'] = alias
                    core.save_pandas_data_frame(Core.UserFiles.USERS, users)
                    new_uuid = user["anonym_uuid"]
                else:
                    class UserData:
                        node_id = uuid
                        name = unknown_user_name
                        email = numpy.NaN
                        login = numpy.NaN
                    if new_user:
                        new_uuid = core.extract_user_data(UserData())
                    else:
                        new_uuid = core.extract_user_data(UserData(), node_id_to_anonym_uuid=True)
                if new_uuid is not None:
                    pd_commits.loc[pd_commits.unknown_user == unknown_user_name, 'author'] = new_uuid
                    pd_commits.loc[pd_commits.unknown_user == unknown_user_name, 'committer'] = new_uuid
                    pd_commits.loc[pd_commits.unknown_user == unknown_user_name, 'unknown_user'] = numpy.NaN
            core.current_dir = Path(repo_data_dir,Version.Files.DATA_DIR)
            core.save_pandas_data_frame(Version.Files.COMMITS,pd_commits)

    @staticmethod      
    def get_full_names_of_repositories(data_root_dir: str) -> list:
        """
        get_repo_informations(data_root_dir)

        Gets repository data (owner and name) as list of strings.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        
        Returns
        -------
        list
            Returns a list of strings for each repository owner and repository name.

        """
        repo_file = Path(data_root_dir, GitHub2Pandas.Files.REPOS)
        if repo_file.is_file():
            with open(repo_file, 'r') as json_file:
                repo_data = json.load(json_file)
                return repo_data[GitHub2Pandas.REPOSITORIES_KEY]
        return []
