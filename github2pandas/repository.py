import logging
from pathlib import Path
import numpy as np
#import numpy
from pandas import DataFrame
import pandas as pd
# github imports
from github import GithubException
from github import GithubObject
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
# github2pandas imports
from github2pandas.core import Core

class Repository(Core):
    """
    Class to aggregate Repository

    Attributes
    ----------
    DATA_DIR : str
        Repository dir where all files are saved in.
    REPOSITORY : str
        Pandas table file for basic repository data.
    TEMPLATES : str
        Names of relevant templates in Github repositories
 
    Methods
    -------
    generate_pandas_tables(contributor_companies_included = False)
        Extracting the basic repository data.
    extract_repository_data(contributor_companies_included)
        Extracting general repository data.
    get_repository_keyparameter(data_root_dir)
        Get a generated pandas tables.
        
    """
    REPOSITORY_DIR = "Repository"
    REPOSITORY = "pdRepository.p"
    TEMPLATES_TO_CHECK = {
        'file_readme': "README.md",
        'file_code_of_conduct': "CODE_OF_CONDUCT.md", # .... defines standards for how to engage in a community.
        'file_contributing': "CONTRIBUTING.md", # ... communicates how people should contribute to your project
        'file_funding': "FUNDING.yml", # ... displays a sponsor button in your repository ... 
        'file_IssuePR_templates': ".github/ISSUE_TEMPLATE/config.yml", # ... Issue and pull request templates customize and standardize the information you’d like contributors 
        'file_security': "SECURITY.md", # ... gives instructions for how to report a security vulnerability in your project. 
        'file_support': "SUPPORT.md", # ... lets people know about ways to get help with your project.
    }
    class Params(Core.Params):
        """
        A parameter class that holds all possible parameters for the data extraction.

        Methods
        -------
        __init__(self, contributor_companies)
            Initializes all parameters with a default.
        
        """
        def __init__(self, contributor_companies: bool = True) -> None:
            """
            __init__(self, contributor_companies)
       
            Initializes all parameters with a default.

            Parameters
            ----------
            contributor_companies : bool, default=True
                Extract contributor companies?

            """
            self.contributor_companies = contributor_companies

    class Files(Core.Files):
        """
        A file class that holds all file names and the folder name.

        Attributes
        ----------
        DATA_DIR : str
            Folder name for this module.
        REPOSITORY : str
            Filename of the repository pandas table.

        """
        DATA_DIR = "Repository"
        REPOSITORY = "Repository.p"
   
    def getFirstAppearance(self, templates_to_check):
        commits = self.save_api_call(self.repo.get_commits, path=templates_to_check)
        commit_count = self.get_save_total_count(commits)
        if commit_count == 0:
            return np.nan
        first_commit = self.get_save_api_data(commits,commit_count - 1)
        return first_commit.commit.author.date
          
    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000, log_level:int=logging.INFO) -> None:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum)

        Initializes git repository object with general information.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.
        repo : GitHubRepository
            Repository object from pygithub.
        data_root_dir : Path
            Data root directory for the repository.
        request_maximum : int, default=40000
            Maximum amount of returned informations for a general api call
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
            Repository.Files.DATA_DIR,
            request_maximum=request_maximum,
            log_level=log_level
        )

    @property
    def repository_df(self) -> pd.DataFrame:
        return Core.get_pandas_data_frame(self.current_dir, Repository.Files.REPOSITORY)

    def generate_pandas_tables(self, params:Params = Params()) -> None:
        """
        generate_pandas_tables(contributor_companies_included = False)

        Extracts the basic repository data.

        Parameters
        ----------
        contributor_companies_included: bool, default=False
            Regulates evaluation of contributor affiliations (huge effort in large projects).
            
        """
        repository_data_list = []
        repository_data = self.__extract_repository_data(params)
        repository_data_list.append(repository_data)
        repository_df = DataFrame(repository_data_list)
        self.save_pandas_data_frame(Repository.Files.REPOSITORY, repository_df)

    def __extract_repository_data(self, params:Params) -> dict:
        """
        __extract_repository_data(contributor_companies_included)

        Extracts general data of repository.

        Parameters
        ----------
        contributor_companies_included: bool, default=False
            Regulates evaluation of contributor affiliations (huge effort in large projects).

        Returns
        -------
        dict
            Dictionary with the extracted data.

        """
        repository_data = {}

        repo_name = self.repo.name
        user_name = self.repo.full_name.split("/")[0]

        commits = self.save_api_call(self.repo.get_commits)
        commit_count = self.get_save_total_count(commits)
        if commit_count == 0:
            print("No commits found!") 
            last_commit_date = None 
        else:
            last_commit = self.get_save_api_data(commits,0)
            last_commit_date = pd.to_datetime(last_commit.commit.committer.date , format="%Y-%m-%d M:%S")
        # last_commit_date on main Branch

        # commits = self.repo.get_commits()
        # try:
        #     # problem: No commits in repo
        #     last_commit_date = pd.to_datetime(commits[0].commit.committer.date , format="%Y-%m-%d M:%S")
        #     commit_count = commits.totalCount
        # except GithubException:
        #     commit_count = 0
        #     last_commit_date = numpy.nan
        #     print("No commits found!")  
         
        contributors = self.save_api_call(self.repo.get_contributors,"True")
        contributors_count = self.get_save_total_count(contributors)
        # contributor = self.repo.get_contributors( 'all')
        # try:
        #     # problem: history or contributor is too large to list them via the API.
        #     contributors_count = len (list (contributor))
        # except GithubException:
        #     print("Too many contributors, not covered by API!")   
        #     contributors_count = numpy.nan

        companies = []
        contributors_count2 = contributors_count
        if contributors_count > 500:
            print("Only first 500 Contributor can hold information!")
            contributors_count2 = 500
        if params.contributor_companies:
            for i in self.progress_bar(range(contributors_count2), "Contributor Companies: "):
                contributor = self.get_save_api_data(contributors,i)
                if not contributor._organizations_url == GithubObject.NotSet:
                    companies.append(contributor.company)
        filtered_companies = list(filter(None.__ne__, companies))
        # companies = []
        # if contributor_companies_included:
        #     for contributor in contributor:
        #         try:
        #             companies.append(contributor.company)
        #         except GithubException:
        #             print('Contributor does not exist anymore')
        #             continue
        # filtered_companies = list(filter(None.__ne__, companies))
        
        read_me = self.save_api_call(self.repo.get_readme)
        if read_me is None or read_me._content == GithubObject.NotSet:
            readme_content = ""
            print("Readme does not exist")
        else:
            readme_content = read_me.content
        # try:
        #     # problem: readme.md does not exist
        #     readme_content = self.repo.get_readme().content
        # except GithubException:
        #     readme_content = ""
        #     print("Readme does not exist")
        # problem: sometimes get_readme outputs a None result
        if readme_content is None:
            readme_length = 0
            print("Readme does not exist")
        else:
            readme_length = len(readme_content)
        
        tags = self.save_api_call(self.repo.get_tags)
        tag_count = self.get_save_total_count(tags)
        # try:
        #     # problem: empty list of tags
        #     tag_count = self.repo.get_tags().totalCount
        # except GithubException:
        #     tag_count = 0
        #     print("No tags assigned to repository")

        if self.repo._organization == GithubObject.NotSet:
            organization_name = "not known"
            repo_type = "not known"
            print("Organization not valid")
        else:
            organization_name = self.repo.organization.name
            repo_type = self.repo.organization.type
        # try:
        #     # problem: organization entry empty
        #     organization_name = self.repo.organization.name
        #     repo_type = self.repo.organization.type
        # except:
        #     organization_name = "not known"
        #     repo_type = "not known"
        #     print("Organization not valid")
        
        pulls_review_comments_obj = self.save_api_call(self.repo.get_pulls_review_comments)
        pulls_review_comments = self.get_save_total_count(pulls_review_comments_obj)
        # try:
        #     # problem: no pull request comments
        #     pulls_review_comments = self.repo.get_pulls_review_comments().totalCount
        # except GithubException:
        #     pulls_review_comments = "not known"
        #     print("No pull request comments")

        releases = self.save_api_call(self.repo.get_releases)
        release_count = self.get_save_total_count(releases)
        # try:
        #     # problem: ???
        #     release_count = self.repo.get_releases().totalCount,
        # except GithubException:
        #     release_count = 0
        #     print("Wrong release count output")

        branches = self.save_api_call(self.repo.get_branches)
        branches_count = self.get_save_total_count(branches)
        commit_comments = self.save_api_call(self.repo.get_comments)
        commit_comments_count = self.get_save_total_count(commit_comments)
        labels = self.save_api_call(self.repo.get_labels)
        labels_count = self.get_save_total_count(labels)
        milestones = self.save_api_call(self.repo.get_milestones,state="all")
        milestones_count = self.get_save_total_count(milestones)
        pull_requests = self.save_api_call(self.repo.get_pulls,state="all")
        pull_requests_count = self.get_save_total_count(pull_requests)
        workflows = self.save_api_call(self.repo.get_workflows)
        workflows_count = self.get_save_total_count(workflows)
        issues = self.save_api_call(self.repo.get_issues,state="all")
        issues_count = self.get_save_total_count(issues)
        issues_comments = self.save_api_call(self.repo.get_issues_comments)
        issues_comments_count = self.get_save_total_count(issues_comments)

        repository_data = {
            'repo_name': repo_name,
            'organization_name' : organization_name,
            'repo_type' : repo_type,
            'user_name': user_name,
            'creation_date': pd.to_datetime(self.repo.created_at, format="%Y-%m-%d %H:%M:%S"),
            'stars': self.repo.stargazers_count,
            'size': self.repo.size,
            'contributor_count': contributors_count,
            'contributor_companies': filtered_companies,
            'contributor_companies_count': len(filtered_companies),
            'repo_url': self.repo.url,
            'repo_html_url':self.repo.html_url,
            'branch_count': branches_count,
            'commit_count': commit_count,
            'commit_comment_count': commit_comments_count,
            'last_commit_date': last_commit_date,
            'labels_count': labels_count,
            'tag_count': tag_count,
            'milestone_count': milestones_count,
            'pullrequest_count': pull_requests_count,
            'pullrequest_review_count': pulls_review_comments,
            'release_count':  release_count,
            'workflow_count': workflows_count,
            'readme_length': readme_length,
            'issues_count': issues_count,
            'issues_comment_count': issues_comments_count,
            'has_wiki': bool(self.repo.has_wiki),
            'has_pages': bool(self.repo.has_pages),
            'has_projects': bool(self.repo.has_projects),
            'has_downloads': bool(self.repo.has_downloads),
            'watchers_count': bool(self.repo.watchers_count),
            'is_fork': self.repo.fork,
            'prog_language': self.repo.language,
            'file_readme': self.getFirstAppearance(Repository.TEMPLATES_TO_CHECK['file_readme']),
            'file_code_of_conduct': self.getFirstAppearance(Repository.TEMPLATES_TO_CHECK['file_code_of_conduct']),
            'file_contributing': self.getFirstAppearance(Repository.TEMPLATES_TO_CHECK['file_contributing']),
            'file_funding': self.getFirstAppearance(Repository.TEMPLATES_TO_CHECK['file_funding']),
            'file_IssuePR_templates': self.getFirstAppearance(Repository.TEMPLATES_TO_CHECK['file_IssuePR_templates']),
            'file_security': self.getFirstAppearance(Repository.TEMPLATES_TO_CHECK['file_security']),
            'file_support': self.getFirstAppearance(Repository.TEMPLATES_TO_CHECK['file_support'])
        }
        return repository_data
