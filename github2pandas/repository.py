from pathlib import Path
from github import GithubException
from numpy import nan as np_nan
from pandas import DataFrame, read_pickle, to_datetime
# github imports
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
# github2pandas imports
from github2pandas.core import Core
from github2pandas.utility import progress_bar

class Repository(Core):
    """
    Class to aggregate Repository

    Attributes
    ----------
    REPOSITORY_DIR : str
        repository dir where all files are saved in.
    REPOSITORY : str
        Pandas table file for basic repository data.

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
            Path(data_root_dir, Repository.REPOSITORY_DIR),
            request_maximum
        )

    @property
    def repository_df(self):
        return Repository.get_repository_keyparameter(self.data_root_dir)

    def generate_pandas_tables(self, contributor_companies_included:bool = False):
        """
        generate_pandas_tables(contributor_companies_included = False)

        Extracting the basic repository data.

        Parameters
        ----------
        contributor_companies_included: bool default False
            Starts evaluation of contributor affiliations (huge effort in large projects).
            
        """
        repository_data_list = []
        repository_data = self.save_api_call(self.extract_repository_data,contributor_companies_included)
        repository_data_list.append(repository_data)
        repository_df = DataFrame(repository_data_list)
        self.save_pandas_data_frame(Repository.REPOSITORY, repository_df)

    def extract_repository_data(self, contributor_companies_included:bool = False):
        """
        extract_repository_data(contributor_companies_included)

        Extracting general repository data.

        Parameters
        ----------
        contributor_companies_included: bool default False
            Starts evaluation of contributor affiliations (huge effort in large projects).

        Returns
        -------
        dict
            Dictionary with the extracted data.

        """
        repository_data = {}

        repo_name = self.repo.full_name.split('/')[-1]
        user_name = self.repo.url.split('/')[-2]

        commits = self.repo.get_commits()
        try:
            # problem: No commits in repo
            last_commit_date = to_datetime(commits[0].commit.committer.date , format="%Y-%m-%d M:%S")
            commit_count = commits.totalCount
        except GithubException:
            commit_count = 0
            last_commit_date = np_nan
            print("No commits found!")   

        contributor = self.repo.get_contributors( 'all')
        try:
            # problem: history or contributor is too large to list them via the API.
            contributors_count = len (list (contributor))
        except GithubException:
            print("Too many contributors, not covered by API!")   
            contributors_count = np_nan

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
            readme_content = self.repo.get_readme().content
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
            tag_count = self.repo.get_tags().totalCount
        except GithubException:
            tag_count = 0
            print("No tags assigned to repository")

        try:
            # problem: organization entry empty
            organization_name = self.repo.organization.name
            repo_type = self.repo.organization.type
        except:
            organization_name = "not known"
            repo_type = "not known"
            print("Organization not valid")

        try:
            # problem: no pull request comments
            pulls_review_comments = self.repo.get_pulls_review_comments().totalCount
        except GithubException:
            pulls_review_comments = "not known"
            print("No pull request comments")

        try:
            # problem: ???
            release_count = self.repo.get_releases().totalCount,
        except GithubException:
            release_count = 0
            print("Wrong release count output")

        repository_data = {
            'repo_name': repo_name,
            'organization_name' : organization_name,
            'repo_type' : repo_type,
            'user_name': user_name,
            'creation_date': to_datetime(self.repo.created_at, format="%Y-%m-%d %H:%M:%S"),
            'stars': self.repo.stargazers_count,
            'size': self.repo.size,
            'contributor_count': contributors_count,
            'contributor_companies': filtered_companies,
            'contributor_companies_count': len(filtered_companies),
            'repo_url': self.repo.url,
            'repo_html_url':self.repo.html_url,
            'branch_count': self.repo.get_branches().totalCount,
            'commit_count': commit_count,
            'commit_comment_count': self.repo.get_comments().totalCount,
            'last_commit_date': last_commit_date,
            'labels_count': self.repo.get_labels().totalCount,
            'tag_count': tag_count,
            'milestone_count': self.repo.get_milestones(state="all").totalCount,
            'pullrequest_count': self.repo.get_pulls(state="all").totalCount,
            'pullrequest_review_count': pulls_review_comments,
            'release_count':  release_count,
            'workflow_count': self.repo.get_workflows().totalCount,
            'readme_length': readme_length,
            'issues_count': self.repo.get_issues(state="all").totalCount,
            'issues_comment_count': self.repo.get_issues_comments().totalCount,
            'has_wiki': bool(self.repo.has_wiki),
            'has_pages': bool(self.repo.has_pages),
            'has_projects': bool(self.repo.has_projects),
            'has_downloads': bool(self.repo.has_downloads),
            'watchers_count': bool(self.repo.watchers_count),
            'is_fork': self.repo.fork,
            'prog_language': self.repo.language
        }
        return repository_data
    
    @staticmethod
    def get_repository_keyparameter(data_root_dir:Path):
        """
        get_repository_keyparameter(data_root_dir)

        Get a generated pandas tables.

        Parameters
        ----------
        data_root_dir : Path
            Data root directory for the repository.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can include the desired data.

        """
        repository_dir = Path(data_root_dir, Repository.REPOSITORY_DIR)
        pd_repository_file = Path(repository_dir, Repository.REPOSITORY)
        if pd_repository_file.is_file():
            return read_pickle(pd_repository_file)
        else:
            return DataFrame()
