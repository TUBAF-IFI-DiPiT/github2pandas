import pandas as pd
from pathlib import Path
from github import GithubException
from .utility import Utility
import numpy as np

class Repository(object):
    """
    Class to aggregate Workflows

    Attributes
    ----------
    REPOSITORY_DIR : str
        repository dir where all files are saved in.
    REPOSITORY : str
        Pandas table file for basic repository data.
    TEMPLATES : str
        Names of relevant templates in Github repositories
 
    Methods
    -------
    extract_repository_data(repo, contributor_companies_included = False):
        Extracting general repository data.
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
            
    @staticmethod    
    def getFirstAppearance(repo, templates_to_check):
        try:
            commits = repo.get_commits(path=templates_to_check)
            first_commit = commits[commits.totalCount - 1]
            return first_commit.commit.author.date
        except IndexError:
            return np.nan
                
    @staticmethod
    def extract_repository_data(repo, contributor_companies_included = False):
        """
        extract_repository_data(repo, contributor_companies_included)

        Extracting general repository data.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.

        contributor_companies_included: bool default False
            Starts evaluation of contributor affiliations (huge effort in large projects).

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
           PyGithub Workflow object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Workflow.html

        """
        repository_data = {}

        repo_name = repo.full_name.split('/')[-1]
        user_name = repo.url.split('/')[-2]

        commits = repo.get_commits()
        try:
            # problem: No commits in repo
            last_commit_date = pd.to_datetime(commits[0].commit.committer.date , format="%Y-%m-%d M:%S")
            commit_count = commits.totalCount
        except GithubException:
            commit_count = 0
            last_commit_date = np.nan
            print("No commits found!")   

        contributor = repo.get_contributors( 'all')
        try:
            # problem: history or contributor is too large to list them via the API.
            contributors_count = len (list (contributor))
        except GithubException:
            print("Too many contributors, not covered by API!")   
            contributors_count = np.nan

        companies = []
        if contributor_companies_included:
            for contributor in contributor:
                try:
                    companies.append(contributor.company)
                except GithubException:
                    print('Contributor does not exist anymore')
                    continue
        filtered_companies = list(filter(None.__ne__, companies))

        try:
            # problem: readme.md does not exist
            readme_content = repo.get_readme().content
        except GithubException:
            readme_content = ""
            print("Readme does not exist")
        # problem: sometimes get_readme outputs a NoneType result
        if readme_content is None:
            readme_length = 0
            print("Readme does not exist")
        else:
            readme_length = len(readme_content)

        try:
            # problem: empty list of tags
            tag_count = repo.get_tags().totalCount
        except GithubException:
            tag_count = 0
            print("No tags assigned to repository")

        try:
            # problem: organization entry empty
            organization_name = repo.organization.name
            repo_type = repo.organization.type
        except:
            organization_name = "not known"
            repo_type = "not known"
            print("Organization not valid")

        try:
            # problem: no pull request comments
            pulls_review_comments = repo.get_pulls_review_comments().totalCount
        except GithubException:
            pulls_review_comments = "not known"
            print("No pull request comments")

        try:
            # problem: ???
            release_count = repo.get_releases().totalCount,
        except GithubException:
            release_count = 0
            print("Wrong release count output")

        repository_data = {
            'repo_name': repo_name,
            'organization_name' : organization_name,
            'repo_type' : repo_type,
            'user_name': user_name,
            'creation_date': pd.to_datetime(repo.created_at, format="%Y-%m-%d %H:%M:%S"),
            'stars': repo.stargazers_count,
            'size': repo.size,
            'contributor_count': contributors_count,
            'contributor_companies': filtered_companies,
            'contributor_companies_count': len(filtered_companies),
            'repo_url': repo.url,
            'repo_html_url':repo.html_url,
            'branch_count': repo.get_branches().totalCount,
            'commit_count': commit_count,
            'commit_comment_count': repo.get_comments().totalCount,
            'last_commit_date': last_commit_date,
            'labels_count': repo.get_labels().totalCount,
            'tag_count': tag_count,
            'milestone_count': repo.get_milestones(state="all").totalCount,
            'pullrequest_count': repo.get_pulls(state="all").totalCount,
            'pullrequest_review_count': pulls_review_comments,
            'release_count':  release_count,
            'workflow_count': repo.get_workflows().totalCount,
            'readme_length': readme_length,
            'issues_count': repo.get_issues(state="all").totalCount,
            'issues_comment_count': repo.get_issues_comments().totalCount,
            'has_wiki': bool(repo.has_wiki),
            'has_pages': bool(repo.has_pages),
            'has_projects': bool(repo.has_projects),
            'has_downloads': bool(repo.has_downloads),
            'watchers_count': bool(repo.watchers_count),
            'is_fork': repo.fork,
            'prog_language': repo.language, 
            'file_readme': Repository.getFirstAppearance(repo, 
                                                         Repository.TEMPLATES_TO_CHECK['file_readme']),
            'file_code_of_conduct': Repository.getFirstAppearance(repo, 
                                                         Repository.TEMPLATES_TO_CHECK['file_code_of_conduct']),
            'file_contributing': Repository.getFirstAppearance(repo, 
                                                         Repository.TEMPLATES_TO_CHECK['file_contributing']),
            'file_funding': Repository.getFirstAppearance(repo, 
                                                         Repository.TEMPLATES_TO_CHECK['file_funding']),
            'file_IssuePR_templates': Repository.getFirstAppearance(repo, 
                                                         Repository.TEMPLATES_TO_CHECK['file_IssuePR_templates']),
            'file_security': Repository.getFirstAppearance(repo, 
                                                         Repository.TEMPLATES_TO_CHECK['file_security']),
            'file_support': Repository.getFirstAppearance(repo, 
                                                         Repository.TEMPLATES_TO_CHECK['file_support']),
        }
        return repository_data
    

    @staticmethod
    def generate_repository_pandas_table(repo, data_root_dir, contributor_companies_included = False):
        """
        generate_repository_pandas_table(repo, data_root_dir, contributor_companies_included = False)

        Extracting the basic repository data.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        data_root_dir : str
            Data root directory for the repository.
        contributor_companies_included: bool default False
            Starts evaluation of contributor affiliations (huge effort in large projects).
            
        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html
        
        """

        repository_dir = Path(data_root_dir, Repository.REPOSITORY_DIR)
        repository_dir.mkdir(parents=True, exist_ok=True)

        repository_data = Repository.extract_repository_data(repo, contributor_companies_included)
       
        repository_data_list = []
        repository_data_list.append(repository_data)
        Utility.save_list_to_pandas_table(repository_dir, Repository.REPOSITORY, repository_data_list)

    @staticmethod
    def get_repository_keyparameter(data_root_dir, filename=REPOSITORY):
        """
        get_repository_keyparameter(data_root_dir, filename=REPOSITORY)

        Get a generated pandas tables.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        filename : str, default=REPOSITORY
            Pandas table file for workflows or workflows runs data.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can include the desired data.

        """
        repository_dir = Path(data_root_dir, Repository.REPOSITORY_DIR)
        pd_repository_file = Path(repository_dir, filename)
        if pd_repository_file.is_file():
            return pd.read_pickle(pd_repository_file)
        else:
            return pd.DataFrame()
