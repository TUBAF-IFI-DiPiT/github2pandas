from numpy import extract
from pandas import DataFrame, read_pickle
from pathlib import Path
# github imports
from github import GithubObject
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
from github.PullRequest import PullRequest as GitHubPullRequest
from github.PullRequestComment import PullRequestComment as GitHubPullRequestComment
from github.PullRequestReview import PullRequestReview as GitHubPullRequestReview
# github2pandas imports
from github2pandas.issues import Issues
from github2pandas.core import Core
from github2pandas.utility import progress_bar, copy_valid_params

class PullRequests(Core):
    """
    Class to aggregate Pull Requests

    Attributes
    ----------
    PULL_REQUESTS_DIR : str
        Pull request dir where all files are saved in.
    PULL_REQUESTS : str
        Pandas table file for pull request data.
    PULL_REQUESTS_COMMENTS : str
        Pandas table file for comments data in pull requests.
    PULL_REQUESTS_REACTIONS : str
        Pandas table file for reactions data in pull requests.
    PULL_REQUESTS_REVIEWS : str
        Pandas table file for reviews data in pull requests.
    EXTRACTION_PARAMS : dict
        Holds all extraction parameters with a default setting.
    pull_request_df : DataFrame
        Pandas DataFrame object with general pull requests data.
    review_comment_df : DataFrame
        Pandas DataFrame object with review comments data.
    reviews_df : DataFrame
        Pandas DataFrame object with reviews data.
    reactions_df : DataFrame
        Pandas DataFrame object with reactions data.

    Methods
    -------
    __init__(self, github_connection, repo, data_root_dir, request_maximum)
        Initial pull request object with general information.
    generate_pandas_tables(self, check_for_updates=False, extraction_params={})
        Extracting the complete pull request data from a repository.
    extract_pull_request(self, pull_request, params)
        Extracting a pull request.
    extract_review_comment(self, data, params)
        Extracting a review comment from pull request.
    extract_pull_request_data(self, pull_request, additional_information=False)
        Extracting general pull request data.
    extract_comment_data(self, review_comment)
        Extracting review comment data.
    extract_review_data(self, review, pull_request_id)
        Extracting general review data from a pull request.
    get_pull_requests(data_root_dir, filename=PULL_REQUESTS)
        Get a genearted pandas table.
    
    """
    PULL_REQUESTS_DIR = "PullRequests"
    PULL_REQUESTS = "pdPullRequests.p"
    PULL_REQUESTS_COMMENTS = "pdPullRequestsComments.p"
    PULL_REQUESTS_REACTIONS = "pdPullRequestsReactions.p"
    PULL_REQUESTS_REVIEWS = "pdPullRequestsReviews.p"
    EXTRACTION_PARAMS = {
        "pull_requests": True,
        "deep_pull_requests": False, # requires pull_requests
        "commits": False, # requires pull_requests
        "review_requested": False, # requires pull_requests
        "review_comment": True,
        "reactions": False,
        "reviews": False,
        "issues": Issues.EXTRACTION_PARAMS # if issues are not extracted
    }

    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000) -> None:
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
            Path(data_root_dir, PullRequests.PULL_REQUESTS_DIR),
            request_maximum
        )
    
    @property
    def pull_request_df(self):
        return PullRequests.get_pull_requests(self.data_root_dir)
    @property
    def review_comment_df(self):
        return PullRequests.get_pull_requests(self.data_root_dir, PullRequests.PULL_REQUESTS_COMMENTS)
    @property
    def reviews_df(self):
        return PullRequests.get_pull_requests(self.data_root_dir, PullRequests.PULL_REQUESTS_REVIEWS)
    @property
    def reactions_df(self):
        return PullRequests.get_pull_requests(self.data_root_dir, PullRequests.PULL_REQUESTS_REACTIONS)
  
    def generate_pandas_tables(self, check_for_updates:bool = False, extraction_params:dict = {}):
        """
        generate_pandas_tables(self, check_for_updates=False, extraction_params={})

        Extracting the complete pull request data from a repository.

        Parameters
        ----------
        check_for_updates : bool, default=True
            Check first if there are any new issues information. Does not work when extract_reaction is True.
        extraction_params : dict, default={}
            Can hold extraction parameters. This defines what will be extracted.

        """
        params = copy_valid_params(self.EXTRACTION_PARAMS,extraction_params)
        extract_pull_requests = False
        if params["deep_pull_requests"]:
            params["pull_requests"] = True
        if params["review_requested"]:
            params["pull_requests"] = True
        if params["commits"]:
            params["pull_requests"] = True
        if params["pull_requests"] or params["reactions"] or params["reviews"]:
            extract_pull_requests = True
            pull_requests = self.save_api_call(self.repo.get_pulls, state='all', sort="updated")
            total_count = self.get_save_total_count(pull_requests)
            if total_count == 0:
                return
            if check_for_updates:
                if params["reactions"]:
                    print("Check for update does not work when param reactions is True")
                elif params["reviews"]:
                    print("Check for update does not work when param reviews is True")
                else:
                    old_pull_requests = PullRequests.get_pull_requests(self.data_root_dir)
                    if not self.check_for_updates_paginated(pull_requests, total_count, old_pull_requests):
                        print("No new Pull Request information!")
                        return
        self.__pull_request_list = []
        self.__review_comment_list = []
        self.__reviews_list = []
        self.__reactions_list = []
        if extract_pull_requests:
            # check if issues(with pull request data) are extracted
            issues_df = Issues.get_pandas_table(self.data_root_dir)
            if issues_df.empty or issues_df[issues_df["is_pull_request"] == True]["is_pull_request"].count() < total_count:
                print("Issues are missing. Extracting Issues now!")
                issues = Issues(
                    self.github_connection,
                    self.repo,
                    self.data_root_dir,
                    self.request_maximum
                    )
                issues.generate_pandas_tables(extraction_params=params["issues"])
                issues_df = issues.issues_df
            if total_count < self.request_maximum:
                for i in progress_bar(range(total_count), "Pull Requests:   "):
                    pull_request = self.get_save_api_data(pull_requests, i)
                    self.extract_pull_request(pull_request, params)
            else:
                # get a pull request for each issue labeled as pull request
                pull_requests_df = issues_df[issues_df["is_pull_request"] == True]
                count = 0
                for index in progress_bar(range(int(pull_requests_df["number"].count())), "Pull Requests :"):
                    while issues_df.loc[count,"is_pull_request"] == False:
                        count += 1
                    number = int(issues_df.loc[count,"number"])
                    pull_request = self.save_api_call(self.repo.get_pull, number)
                    self.extract_pull_request(pull_request, params)
        if params["review_comment"]:
            # extract comments
            self.extract_with_updated_and_since(
                self.repo.get_pulls_comments,
                "Pull Request Comments",
                self.extract_review_comment,
                params)
        if extract_pull_requests:
            pull_request_df = DataFrame(self.__pull_request_list)
            self.save_pandas_data_frame(PullRequests.PULL_REQUESTS, pull_request_df)
        if params["review_comment"]:
            review_comment_df = DataFrame(self.__review_comment_list)
            self.save_pandas_data_frame(PullRequests.PULL_REQUESTS_COMMENTS, review_comment_df)
        if params["reviews"]:
            reviews_df = DataFrame(self.__reviews_list)
            self.save_pandas_data_frame(PullRequests.PULL_REQUESTS_REVIEWS, reviews_df)
        if params["reactions"]:
            reactions_df = DataFrame(self.__reactions_list)
            self.save_pandas_data_frame(PullRequests.PULL_REQUESTS_REACTIONS, reactions_df)
    
    def extract_pull_request(self, pull_request:GitHubPullRequest, params:dict):
        """
        extract_pull_request(self, pull_request, params)

        Extracting a pull request.

        Parameters
        ----------
        pull_request : GitHubPullRequest
            PullRequest object from pygithub.
        params : dict
            Holds extraction parameters. This defines what will be extracted.
        
        Notes
        -----
            PyGithub PullRequest object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html

        """
        pull_request_data = self.extract_pull_request_data(pull_request, params["deep_pull_requests"])
        if params["reviews"]:
            reviews = self.save_api_call(pull_request.get_reviews)
            for i in range(self.request_maximum):
                try:
                    review = self.get_save_api_data(reviews, i)
                    review_data = self.save_api_call(self.extract_review_data, review, pull_request.id)
                    self.__reviews_list.append(review_data)
                except IndexError:
                    break
        if params["review_requested"]:
            pull_request_data["review_requested_users"] = []
            review_requests_users, review_requests_teams = self.save_api_call(pull_request.get_review_requests)
            for i in range(self.request_maximum):
                try:
                    review_request_user = self.get_save_api_data(review_requests_users, i)
                    pull_request_data["review_requested_users"].append(self.extract_user_data(review_request_user))
                except IndexError:
                    break
        
        if params["commits"]:
            # Maximum of 250 Commits
            pull_request_data["commits"] = []
            commits = self.save_api_call(pull_request.get_commits)
            for i in range(self.request_maximum):
                try:
                    commit = self.get_save_api_data(commits, i)
                    pull_request_data["commits"].append(commit)
                except IndexError:
                    break
        self.__pull_request_list.append(pull_request_data)

    def extract_review_comment(self, data:GitHubPullRequestComment, params:dict):
        """
        extract_review_comment(self, data, params)

        Extracting a review comment from pull request.

        Parameters
        ----------
        data : GitHubPullRequestComment 
            PullRequestComment object from pygithub.
        params : dict
            Holds extraction parameters. This defines what will be extracted.
        
        Notes
        -----
            PyGithub PullRequestComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html

        """
        review_comment_data = self.save_api_call(self.extract_review_comment_data, data)
        self.__review_comment_list.append(review_comment_data)
        if params["reactions"]:
            self.__reactions_list += self.extract_reactions(
                data.get_reactions,
                data.id,
                "review_comment")

    def extract_pull_request_data(self, pull_request:GitHubPullRequest, additional_information:bool = False):
        """
        extract_pull_request_data(self, pull_request, additional_information=False)

        Extracting general pull request data.

        Parameters
        ----------
        pull_request : GitHubPullRequest
            PullRequest object from pygithub.
        additional_information : bool, default=False
            extracts more information, but it takes 1 additionally api call and more time

        Returns
        -------
        dict
            Dictionary with the extracted general pull request data.

        Notes
        -----
            PyGithub PullRequest object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html

        """
        pull_request_data = {
            "id": pull_request.id,
            "number": pull_request.number,
            "merged_at": pull_request.merged_at,
            "merge_commit_sha": pull_request.merge_commit_sha,
            "draft": pull_request.draft,
            "updated_at": pull_request.updated_at,
            "url": pull_request.url
        }
        if additional_information:
            pull_request_data["additions"] = pull_request.additions
            pull_request_data["changed_files"] = pull_request.changed_files
            pull_request_data["comments"] = pull_request.comments
            pull_request_data["commits"] = pull_request.commits
            pull_request_data["deletions"] = pull_request.deletions
            pull_request_data["mergeable"] = pull_request.mergeable
            pull_request_data["mergeable_state"] = pull_request.mergeable_state
            pull_request_data["merged"] = pull_request.merged
            pull_request_data["rebaseable"] = pull_request.rebaseable
            pull_request_data["review_comments"] = pull_request.review_comments
            pull_request_data["maintainer_can_modify"] = pull_request.maintainer_can_modify
            pull_request_data["merged_by"] = self.extract_user_data(pull_request.merged_by)
            #pull_request.head
            #pull_request.base
        # in Issue extracted:
        # assignees, body, closed_at, closed_by, comments, created_at, labels, last_modified, locked
        # state, title, author, assignee, (milestone)
        return pull_request_data

    def extract_review_comment_data(self, review_comment:GitHubPullRequestComment):
        """
        extract_comment_data(self, review_comment)

        Extracting review comment data.

        Parameters
        ----------
        review_comment : GitHubPullRequestComment 
            PullRequestComment object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted review comment data.

        Notes
        -----
            PyGithub PullRequestComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html

        """
        review_comment_data = {}
        review_comment_data["body"]= review_comment.body
        review_comment_data["commit_sha"]= review_comment.commit_id
        review_comment_data["created_at"]= review_comment.created_at
        review_comment_data["diff_hunk"]= review_comment.diff_hunk
        review_comment_data["id"]= review_comment.id
        # will cause api call! exclude for now
        #review_comment_data["in_reply_to_id"]= review_comment.in_reply_to_id
        review_comment_data["original_commit_id"]= review_comment.original_commit_id
        review_comment_data["original_position"]= review_comment.original_position
        review_comment_data["path"]= review_comment.path
        review_comment_data["pull_request_url"]= review_comment.pull_request_url
        review_comment_data["updated_at"]= review_comment.updated_at
        review_comment_data["position"]= review_comment.position
        if not review_comment._user == GithubObject.NotSet:
            review_comment_data["author"] = self.extract_user_data(review_comment.user)
        return review_comment_data

    def extract_review_data(self, review:GitHubPullRequestReview, pull_request_id:int):
        """
        extract_review_data(self, review, pull_request_id)

        Extracting review data from a pull request.

        Parameters
        ----------
        review : GitHubPullRequestReview
            PullRequestReview object from pygithub.
        pull_request_id : int
            Pull request id as foreign key.

        Returns
        -------
        dict
            Dictionary with the extracted review data.

        Notes
        -----
            PyGithub PullRequestReview object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html

        """
        review_data = {}
        review_data["pull_request_id"] = pull_request_id
        review_data["id"] = review.id
        if not review._user == GithubObject.NotSet:
            review_data["author"] = self.extract_user_data(review.user)
        review_data["body"] = review.body
        review_data["state"] = review.state
        review_data["submitted_at"] = review.submitted_at
        return review_data
    
    @staticmethod
    def get_pull_requests(data_root_dir:Path, filename:str=PULL_REQUESTS) -> DataFrame:
        """
        get_pull_requests(data_root_dir, filename=PULL_REQUESTS)

        Get a genearted pandas table.

        Parameters
        ----------
        data_root_dir : Path
            Data root directory for the repository.
        filename : str, default=PULL_REQUESTS
            Pandas table file for pull requests or comments or reactions or reviews or events data.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can includes the desired data

        """
        pull_request_dir = Path(data_root_dir, PullRequests.PULL_REQUESTS_DIR)
        pd_pull_requests_file = Path(pull_request_dir, filename)
        if pd_pull_requests_file.is_file():
            return read_pickle(pd_pull_requests_file)
        else:
            return DataFrame()
