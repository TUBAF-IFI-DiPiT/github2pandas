import json
from pathlib import Path
import numpy
import pandas as pd
# github imports
from github import GithubObject
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
from github2pandas.core import Core
from github2pandas.git_releases import GitReleases
from github2pandas.issues import Issues
from github2pandas.pull_requests import PullRequests
from github2pandas.repository import Repository
from github2pandas.version import Version
from github2pandas.utility import progress_bar, copy_valid_params
from github2pandas.workflows import Workflows
class GitHub2Pandas():

    REPO = "Repo.json"
    
    EXTRACTION_PARAMS = {
        "git_releases": True,
        "issues": True,
        "issues_params": Issues.EXTRACTION_PARAMS,
        "pull_requests": True,
        "pull_requests_params": PullRequests.EXTRACTION_PARAMS,
        "repository": True,
        "version": True,
        "workflows": True,
        "workflows_params": Workflows.EXTRACTION_PARAMS
    }

    def __init__(self, github_token:str, data_root_dir:Path, request_maximum:int = 40000) -> None:
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
        self.__github_token = github_token
        self.github_connection = Github(github_token, per_page=100)
        data_root_dir.mkdir(parents=True, exist_ok=True)
        self.data_root_dir = data_root_dir
        self.request_maximum = request_maximum
        self.__core = Core(self.github_connection,None,self.data_root_dir,self.data_root_dir)

    def generate_pandas_tables(self, repo:GitHubRepository, extraction_params:dict = {}):
        data_folder = Path(self.data_root_dir,repo.owner.login,repo.name)
        data_folder.mkdir(parents=True, exist_ok=True)
        params = copy_valid_params(self.EXTRACTION_PARAMS,extraction_params)
        if params["git_releases"]:
            git_releases = GitReleases(self.github_connection,repo,data_folder,self.request_maximum)
            git_releases.generate_pandas_tables()
        if params["issues"]:
            issues = Issues(self.github_connection,repo,data_folder,self.request_maximum)
            issues.generate_pandas_tables(extraction_params=params["issues_params"])
        if params["pull_requests"]:
            pull_requests = PullRequests(self.github_connection,repo,data_folder,self.request_maximum)
            pull_requests.generate_pandas_tables(extraction_params=params["pull_requests_params"])
        if params["repository"]:
            repository = Repository(self.github_connection,repo,data_folder,self.request_maximum)
            repository.generate_pandas_tables()
        if params["version"]:
            version = Version(self.github_connection,repo,data_folder,self.request_maximum)
            version.clone_repository(self.__github_token)
            version.generate_pandas_tables()
        if params["workflows"]:
            workflows = Workflows(self.github_connection,repo,data_folder,self.request_maximum)
            workflows.generate_pandas_tables(extraction_params=params["workflows_params"])

    def define_unknown_user(self, unknown_user_name:str, uuid:str, new_user:bool = False):
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
        pd_commits = Version.get_version(self.data_root_dir)
        if "unknown_user" in pd_commits:
            unknown_users = pd_commits.unknown_user.unique()
            if unknown_user_name in unknown_users:
                users = Core.get_users(self.data_root_dir)
                p_user = users.loc[users.anonym_uuid == uuid]
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
                    self.__core.save_pandas_data_frame(Core.USERS, users)
                    new_uuid = user["anonym_uuid"]
                else:
                    class UserData:
                        node_id = uuid
                        name = unknown_user_name
                        email = numpy.NaN
                        login = numpy.NaN
                    if new_user:
                        new_uuid = self.__core.extract_user_data(UserData())
                    else:
                        new_uuid = self.__core.extract_user_data(UserData(), node_id_to_anonym_uuid=True)
                    if new_uuid is not None:
                        pd_commits.loc[pd_commits.unknown_user == unknown_user_name, 'author'] = new_uuid
                        pd_commits.loc[pd_commits.unknown_user == unknown_user_name, 'committer'] = new_uuid
                        pd_commits.loc[pd_commits.unknown_user == unknown_user_name, 'unknown_user'] = numpy.NaN
            version_folder = Path(self.data_root_dir, Version.VERSION_DIR)
            self.__core.current_dir = version_folder
            self.__core.save_pandas_data_frame(Version.VERSION_COMMITS,pd_commits)
            self.__core.current_dir = self.data_root_dir

    def get_unknown_users(self, data_root_dir):
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
     
    def get_repos(self, whitelist_patterns=None, blacklist_patterns=None):
        """
        get_repos(token, data_root_dir, whitelist_patterns=None, blacklist_patterns=None)

        Get mutiple repositorys by mutiple pattern and token.

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
        for i in progress_bar(range(repo_total_count), "Repositories:   "):
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
                    repo_dir = Path(self.data_root_dir, repo.owner.login + "/" + repo.name)
                    repo_dir.mkdir(parents=True, exist_ok=True)
                    repo_file = Path(repo_dir, self.REPO)
                    with open(repo_file, 'w') as json_file:
                        json.dump({"repo_owner": repo.owner.login,"repo_name":repo.name}, json_file)
                    relevant_repos.append(repo)
        return relevant_repos
    
    def get_repo(self, repo_owner:str, repo_name:str):
        """
        get_repo(repo_owner, repo_name, token, data_root_dir)

        Get a repository by owner, name and token.

        Parameters
        ----------
        repo_owner : str
            the owner of the desired repository.
        repo_name : str
            the name of the desired repository.
        token : str
            A valid Github Token.
        data_root_dir : Path
            Data root directory for the repository.
        
        Returns
        -------
        repo
            Repository object from pygithub.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        repo_file = Path(self.data_root_dir, self.REPO)
        with open(repo_file, 'w') as json_file:
            json.dump({"repo_owner": repo_owner,"repo_name":repo_name}, json_file)
        return self.__core.save_api_call(self.github_connection.get_repo,repo_owner + "/" + repo_name)
 
    @staticmethod      
    def get_repo_informations(data_root_dir):
        """
        get_repo_informations(data_root_dir)

        Get a repository data (owner and name).

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        
        Returns
        -------
        tuple
            Repository Owner and name

        """
        repo_file = Path(data_root_dir, GitHub2Pandas.REPO)
        if repo_file.is_file():
            with open(repo_file, 'r') as json_file:
                repo_data = json.load(json_file)
                return (repo_data["repo_owner"], repo_data["repo_name"])
        return None, None