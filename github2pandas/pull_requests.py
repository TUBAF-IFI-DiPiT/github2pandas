import logging
from pandas import DataFrame
import pandas as pd
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

class PullRequests(Core):
    """
    Class to aggregate Pull Requests

    Attributes
    ----------
    pull_requests_df : DataFrame
        Pandas DataFrame object with general pull requests data.
    review_comments_df : DataFrame
        Pandas DataFrame object with pull request review comments data.
    reviews_df : DataFrame
        Pandas DataFrame object with pull request reviews data.
    reactions_df : DataFrame
        Pandas DataFrame object with pull request reactions data.

    Methods
    -------
    __init__(self, github_connection, repo, data_root_dir, request_maximum=40000, log_level=logging.INFO)
        Initializes pull request object with general information.
    generate_pandas_tables(self, check_for_updates=False, params=Params())
        Extracts the complete pull request data from a repository.
    extract_pull_request(self, pull_request, params)
        Extracts a pull request.
    extract_review_comment(self, data, params)
        Extracts a review comment from pull request.
    __extract_pull_request_data(self, pull_request, additional_information=False)
        Extracts general data of one pull request.
    __extract_review_comment_data(self, review_comment)
        Extracts data of one review comment.
    __extract_review_data(self, review, pull_request_id)
        Extracts general data of one review from a pull request.
    
    """
    class Params(Core.Params):
        """
        A parameter class that holds all possible parameters for the data extraction.

        Methods
        -------
        __init__(self, pull_requests, deep_pull_requests, commits, review_requests, review_comments, reactions, reviews)
            Initializes all parameters with a default.
        
        """
        def __init__(self, pull_requests: bool = True, deep_pull_requests: bool = False, commits: bool = False, review_requests: bool = False, review_comments: bool = True, reactions: bool = False, reviews: bool = False, issues_params: Issues.Params = Issues.Params()) -> None:
            """
            __init__(self, pull_requests, deep_pull_requests, commits, review_requests, review_comments, reactions, reviews)
            
            Initializes all parameters with a default.

            Parameters
            ----------
            pull_requests : bool, default=True
                Extract pull requests?
            deep_pull_requests : bool, default=True
                Extract deep pull requests?
            commits : bool, default=True
                Extract commits of pull requests?
            review_requests : bool, default=True
                Extract review requests of pull requests?
            review_comments : bool, default=True
                Extract review comments of pull requests?
            reactions : bool, default=True
                Extract reactions of pull requests?
            reviews : bool, default=True
                Extract reviews of pull requests?
            issues_params : Issues.Params, default=Issues.Params()
                Issue Parameters are only used if there are not extracted Issues.

            """
            self.pull_requests = pull_requests
            self.deep_pull_requests = deep_pull_requests
            self.commits = commits
            self.review_requests = review_requests
            self.review_comments = review_comments
            self.reactions = reactions
            self.reviews = reviews
            self.issues_params = issues_params

    class Files(Core.Files):
        """
        A file class that holds all file names and the folder name.

        Attributes
        ----------
        DATA_DIR : str
            Folder name for this module.
        PULL_REQUESTS : str
            Filename of the pull requests pandas table.
        REVIEWS_COMMENTS : str
            Filename of the pull requests review comments pandas table.
        PULL_REQUESTS_REACTIONS : str
            Filename of the pull requests reactions pandas table.
        REVIEWS : str
            Filename of the pull requests reviews pandas table.

        """
        DATA_DIR = "PullRequests"
        PULL_REQUESTS = "PullRequests.p"
        REVIEWS_COMMENTS = "ReviewsComments.p"
        PULL_REQUESTS_REACTIONS = "PullRequestsReactions.p"
        REVIEWS = "Reviews.p"

    def __init__(self, github_connection: Github, repo: GitHubRepository, data_root_dir: Path, request_maximum: int = 40000, log_level: int = logging.INFO) -> None:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum, log_level)

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
            PullRequests.Files.DATA_DIR,
            request_maximum=request_maximum,
            log_level=log_level
        )
    
    @property
    def pull_requests_df(self):
        """
        pull_requests_df(self)

        Pandas DataFrame object with general pull requests data.

        Returns
        -------
        pd.DataFrame
            DataFrame of pull request.
            
        """
        return Core.get_pandas_data_frame(self.current_dir, PullRequests.Files.PULL_REQUESTS)
    
    @property
    def review_comments_df(self):
        """
        review_comments_df(self)

        Pandas DataFrame object with general pull request comments data.

        Returns
        -------
        pd.DataFrame
            DataFrame of pull request comments.
            
        """
        return Core.get_pandas_data_frame(self.current_dir, PullRequests.Files.REVIEWS_COMMENTS)
    
    @property
    def reviews_df(self):
        """
        reviews_df(self)

        Pandas DataFrame object with general pull request reviews data.

        Returns
        -------
        pd.DataFrame
            DataFrame of pull request reviews.
            
        """
        return Core.get_pandas_data_frame(self.current_dir, PullRequests.Files.REVIEWS)
    
    @property
    def reactions_df(self):
        """
        reactions_df(self)

        Pandas DataFrame object with general pull request reactions data.

        Returns
        -------
        pd.DataFrame
            DataFrame of pull request reactions.
            
        """
        return Core.get_pandas_data_frame(self.current_dir, PullRequests.Files.PULL_REQUESTS_REACTIONS)
  
    def generate_pandas_tables(self, check_for_updates: bool = False, params: Params = Params()) -> None:
        """
        generate_pandas_tables(self, check_for_updates=False, params=Params())

        Extracts the complete pull request data from a repository. 
        Check first if there are any new pull requests information in dependence of parameter check_for_updates.

        Parameters
        ----------
        check_for_updates : bool, default=False
            Determines whether update is necessary. Does not work when params "reactions" is True.
        params : Params, default=Params()
            Can hold extraction parameters, that define what will be extracted.

        """
        extract_pull_requests = False
        if params.deep_pull_requests:
            params.pull_requests = True
        if params.review_requests:
            params.pull_requests = True
        if params.commits:
            params.pull_requests = True
        if params.pull_requests or params.reactions or params.reviews:
            extract_pull_requests = True
            pull_requests = self.save_api_call(self.repo.get_pulls, state='all', sort="updated")
            total_count = self.get_save_total_count(pull_requests)
            if total_count == 0:
                return
            if check_for_updates:
                if params.reactions:
                    self.logger.warning("Check for update does not work when param reactions is True")
                elif params.reviews:
                    self.logger.warning("Check for update does not work when param reviews is True")
                else:
                    old_pull_requests = self.pull_request_df
                    if not self.check_for_updates_paginated(pull_requests, total_count, old_pull_requests):
                        self.logger.info("No new Pull Request information!")
                        return
        self.__pull_request_list = []
        self.__review_comment_list = []
        self.__reviews_list = []
        self.__reactions_list = []
        if extract_pull_requests:
            # check if issues(with pull request data) are extracted
            issues_df = Core.get_pandas_data_frame(Path(self.repo_data_dir,Issues.Files.DATA_DIR), Issues.Files.ISSUES)
            if issues_df.empty or issues_df[issues_df["is_pull_request"] == True]["is_pull_request"].count() < total_count:
                self.logger.info("Issues are missing. Extracting Issues now!")
                issues = Issues(
                    self.github_connection,
                    self.repo,
                    self.repo_data_root_dir,
                    self.request_maximum
                    )
                issues.generate_pandas_tables(params=params.issues_params)
                issues_df = issues.issues_df
            if total_count < self.request_maximum:
                for i in self.progress_bar(range(total_count), "Pull Requests:   "):
                    pull_request = self.get_save_api_data(pull_requests, i)
                    self.extract_pull_request(pull_request, params)
            else:
                # get a pull request for each issue labeled as pull request
                pull_requests_df = issues_df[issues_df["is_pull_request"] == True]
                count = 0
                for index in self.progress_bar(range(int(pull_requests_df["number"].count())), "Pull Requests :"):
                    while issues_df.loc[count,"is_pull_request"] == False:
                        count += 1
                    number = int(issues_df.loc[count,"number"])
                    pull_request = self.save_api_call(self.repo.get_pull, number)
                    self.extract_pull_request(pull_request, params)
        if params.review_comments:
            # extract comments
            self.extract_with_updated_and_since(
                self.repo.get_pulls_comments,
                "Pull Request Comments",
                self.extract_review_comment,
                params)
        if extract_pull_requests:
            pull_request_df = DataFrame(self.__pull_request_list)
            self.save_pandas_data_frame(PullRequests.Files.PULL_REQUESTS, pull_request_df)
        if params.review_comments:
            review_comment_df = DataFrame(self.__review_comment_list)
            self.save_pandas_data_frame(PullRequests.Files.REVIEWS_COMMENTS, review_comment_df)
        if params.reviews:
            reviews_df = DataFrame(self.__reviews_list)
            self.save_pandas_data_frame(PullRequests.Files.REVIEWS, reviews_df)
        if params.reactions:
            reactions_df = DataFrame(self.__reactions_list)
            self.save_pandas_data_frame(PullRequests.Files.PULL_REQUESTS_REACTIONS, reactions_df)
    
    def extract_pull_request(self, pull_request: GitHubPullRequest, params: Params) -> None:
        """
        extract_pull_request(self, pull_request, params)

        Extracts a pull request.

        Parameters
        ----------
        pull_request : GitHubPullRequest
            PullRequest object from pygithub.
        params : Params
            Holds extraction parameters, that define what will be extracted.
        
        Notes
        -----
            PyGithub PullRequest object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html

        """
        pull_request_data = self.__extract_pull_request_data(pull_request, params.deep_pull_requests)
        if params.reviews:
            reviews = self.save_api_call(pull_request.get_reviews)
            for i in range(self.request_maximum):
                try:
                    review = self.get_save_api_data(reviews, i)
                    review_data = self.save_api_call(self.__extract_review_data, review, pull_request.id)
                    self.__reviews_list.append(review_data)
                except IndexError:
                    break
        if params.review_requests:
            pull_request_data["review_requested_users"] = []
            review_requests_users, review_requests_teams = self.save_api_call(pull_request.get_review_requests)
            for i in range(self.request_maximum):
                try:
                    review_request_user = self.get_save_api_data(review_requests_users, i)
                    pull_request_data["review_requested_users"].append(self.extract_user_data(review_request_user))
                except IndexError:
                    break
        
        if params.commits:
            # Maximum of 250 Commits
            pull_request_data["commits"] = []
            commits = self.save_api_call(pull_request.get_commits)
            for i in range(self.request_maximum):
                try:
                    commit = self.get_save_api_data(commits, i)
                    pull_request_data["commit_shas"].append(commit.sha)
                except IndexError:
                    break
        self.__pull_request_list.append(pull_request_data)

    def extract_review_comment(self, data: GitHubPullRequestComment, params: Params) -> None:
        """
        extract_review_comment(self, data, params)

        Extracts a review comment from pull request.

        Parameters
        ----------
        data : GitHubPullRequestComment 
            PullRequestComment object from pygithub.
        params : Params
            Holds extraction parameters, that define what will be extracted.
        
        Notes
        -----
            PyGithub PullRequestComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html

        """
        review_comment_data = self.save_api_call(self.__extract_review_comment_data, data)
        self.__review_comment_list.append(review_comment_data)
        if params.reactions:
            self.__reactions_list += self.extract_reactions(
                data.get_reactions,
                data.id,
                "review_comment")

    def __extract_pull_request_data(self, pull_request: GitHubPullRequest, additional_information: bool = False) -> dict:
        """
        __extract_pull_request_data(self, pull_request, additional_information=False)

        Extracts general data of one pull request.

        Parameters
        ----------
        pull_request : GitHubPullRequest
            PullRequest object from pygithub.
        additional_information : bool, default=False
            More information will be extracted if True, but it takes more time because of an additional api call

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

    def __extract_review_comment_data(self, review_comment: GitHubPullRequestComment) -> dict:
        """
        __extract_review_comment_data(self, review_comment)

        Extracts data of one review comment.

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

    def __extract_review_data(self, review: GitHubPullRequestReview, pull_request_id: int) -> dict:
        """
        __extract_review_data(self, review, pull_request_id)

        Extracts data of one review from a pull request.

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
