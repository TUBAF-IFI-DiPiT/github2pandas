from asyncio.log import logger
import os
import stat
import typing
import sys
from pathlib import Path
from typing import Union
import pickle
import human_id
import time
import math
import pandas as pd
import logging
# github imports
from github import GithubObject
from github.MainClass import Github
from github.Reaction import Reaction as GitHubReaction
from github.Repository import Repository as GitHubRepository
from github.NamedUser import NamedUser as GitHubNamedUser
from github.PaginatedList import PaginatedList
from github.GithubException import RateLimitExceededException

class Core():
    """
    Class which contains methods for mutiple modules.

    Attributes
    ----------
    USERS : str
        Pandas table file for user data.
    REPO : str
       Json file for general repository informations.

    """
    
    class Files():
        DATA_DIR = ""
        USERS = "Users.p"

        @staticmethod
        def to_list() -> list:
            return [Core.Files.USERS]

        @staticmethod
        def to_dict() -> dict:
            return {Core.Files.DATA_DIR: Core.Files.to_list()}
    
    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, current_dir:str, request_maximum:int = 40000, log_level:int=logging.INFO) -> None:
        self.log_level = log_level
        self.logger = logging.getLogger("github2pandas")
        self.logger.setLevel(log_level)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.StreamHandler())
        self.logger_no_print = logging.getLogger("github2pandas_no_print")
        self.logger_no_print.setLevel(log_level)
        logging.basicConfig(format='%(levelname)s;%(asctime)s;%(message)s', filename=Path(data_root_dir,"github2pandas.log"))
        self.github_connection = github_connection
        self.repo = repo
        self.data_root_dir = data_root_dir
        if repo is not None:
            self.repo_data_dir = Path(self.data_root_dir,repo.full_name)
            self.repo_data_dir.mkdir(parents=True, exist_ok=True)
            df_users = Core.get_pandas_data_frame(self.repo_data_dir, Core.Files.USERS)
            self.users_ids = {}
            for index, row in df_users.iterrows():
                self.users_ids[row["id"]] = row["anonym_uuid"]
        if current_dir is None or current_dir == "":
            if repo is None:
                self.current_dir = self.data_root_dir
            else:
                self.current_dir = self.repo_data_dir
        else:
            self.current_dir = Path(self.repo_data_dir,current_dir)
        self.request_maximum = request_maximum
    
    def save_api_call(self, function, *args, **kwargs):
        """
        save_api_call(function, *args, **kwargs)

        Call a function or method savely.

        Parameters
        ----------
        function : Any
            A function/method to call savely.
        *args
            Input for the function/method.
        **kwargs
            Optional input for the function/method.

        Returns
        -------
        Any
            Returns the result of the function/method.

        """
        try:
            return function(*args, **kwargs)
        except RateLimitExceededException:
            self.wait_for_reset()
            return self.save_api_call(function,*args, **kwargs) 
    
    def get_save_total_count(self, paginated_list:PaginatedList) -> int:
        """
        get_save_total_count(paginated_list)

        Get the total count of a paginated list savely. Waits until request limit is restored.

        Parameters
        ----------
        paginated_list : PaginatedList
            A paginated list as input. 

        Returns
        -------
        int
            Total count of the paginated list.

        """
        try:
            return paginated_list.totalCount
        except RateLimitExceededException:
            self.wait_for_reset()
            return self.get_save_total_count(paginated_list)
   
    def get_save_api_data(self, paginated_list:PaginatedList, index:int):
        """
        get_save_api_data(paginated_list, index)

        Get one item of the paginated list by index.

        Parameters
        ----------
        paginated_list : PaginatedList
            A paginated list as input. 
        index : int
            Index to get from the paginated list.

        Returns
        -------
        Any
            Data from PaginatedList at index

        """
        try:
            return paginated_list[index]
        except RateLimitExceededException:
            self.wait_for_reset()
            return paginated_list[index]

    def wait_for_reset(self):
        """
        wait_for_reset(self)

        Wait until request limit is refreshed.

        """
        self.logger.debug("Waiting for request limit refresh ...")
        self.github_connection.get_rate_limit()
        reset_timestamp = self.github_connection.rate_limiting_resettime
        seconds_until_reset = reset_timestamp - time()
        sleep_step_width = 1
        sleeping_range = range(math.ceil(seconds_until_reset / sleep_step_width))
        for i in self.progress_bar(sleeping_range, "Sleeping : ", 60):
            time.sleep(sleep_step_width)
        self.github_connection.get_rate_limit()
        requests_remaning, requests_limit = self.github_connection.rate_limiting
        while requests_remaning == 0:
            self.logger.debug("No remaining requests sleep 1s ...")
            time.sleep(1)
            self.github_connection.get_rate_limit()
            requests_remaning, requests_limit = self.github_connection.rate_limiting
    
    def check_for_updates_paginated(self, new_paginated_list:PaginatedList, list_count:int, old_df:pd.DataFrame):
        """
        check_for_updates_paginated(new_paginated_list, list_count, old_df)

        Check if if the new paginiated list has updates.

        Parameters
        ----------
        new_paginated_list : PaginatedList
            new paginated list with updated_at and sorted by updated.
        list_count: int
            Length of the paginated List.
        old_df : pd.DataFrame
            old Dataframe.

        Returns
        -------
        bool
            True if it need to be updated. False the List is uptodate.

        """
        if old_df.empty:
            if list_count == 0:
                return False
            return True
        data = self.get_save_api_data(new_paginated_list,0)
        if "id" in old_df:
            old_item = old_df.loc[old_df["id"] == data.id].iloc[0]
            if old_item["updated_at"] == data.updated_at:
                return False
            return True
        last_update = old_df["updated_at"].max()
        if data.updated_at != last_update:
            return True
        return False

    def extract_reactions(self, extract_function, parent_id:int, parent_name:str):
        """
        extract_issue_reactions(extract_function, parent_id)

        Extracting issue reactions.

        Parameters
        ----------
        extract_function : function
            A function to call issue reactions.
        issue_id : int
            Id from issue as foreign key.

        """
        reactions = self.save_api_call(extract_function)
        reaction_list = []
        for i in range(self.request_maximum):
            try:
                reaction = self.get_save_api_data(reactions, i)
                reaction_data = self.save_api_call(self.extract_reaction_data, reaction, parent_id, parent_name)
                reaction_list.append(reaction_data)
            except IndexError:
                break 
        return reaction_list

    def extract_reaction_data(self, reaction:GitHubReaction, parent_id:int, parent_name:str):
        """
        extract_reaction_data(reaction, parent_id, parent_name)

        Extracting general reaction data.

        Parameters
        ----------
        reaction : Reaction
            Reaction object from pygithub.
        parent_id : int
            Id from parent as foreign key.
        parent_name : str
            Name of the parent.

        Returns
        -------
        ReactionData
            Dictionary with the extracted data.

        Notes
        -----
            Reaction object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Reaction.html

        """
        reaction_data = {} 
        reaction_data["parent_id"] = parent_id
        reaction_data["parent_name"] = parent_name
        reaction_data["content"] = reaction.content
        reaction_data["created_at"] = reaction.created_at
        reaction_data["id"] = reaction.id
        if not reaction._user == GithubObject.NotSet:
            reaction_data["author"] = self.extract_user_data(reaction.user)
        return reaction_data
    
    def extract_user_data(self, user:GitHubNamedUser, node_id_to_anonym_uuid=False) -> Union[str,None]:
        """
        extract_user_data(user, users_ids, data_root_dir, node_id_to_anonym_uuid=False)

        Extracting general user data.

        Parameters
        ----------
        user : GitHubNamedUser
            NamedUser object from pygithub.
        node_id_to_anonym_uuid : bool, default=False
            Node_id will be the anonym_uuid
        
        Returns
        -------
        str
            Anonym uuid of user.

        Notes
        -----
            PyGithub NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html

        """
        if not user:
            return None
        if user.node_id in self.users_ids:
            return self.users_ids[user.node_id]
        users_file = Path(self.repo_data_dir, Core.Files.USERS)
        users_df = pd.DataFrame()
        if users_file.is_file():
            users_df = pd.read_pickle(users_file)
        user_data = {}
        if node_id_to_anonym_uuid:
            user_data["anonym_uuid"] = user.node_id
        else:
            user_data["anonym_uuid"] = human_id.generate_id(seed=user.node_id)
        user_data["id"] = user.node_id
        if hasattr(user, "name"):
            user_data["name"] = user.name
        if hasattr(user, "email"):
            user_data["email"] = user.email
        if hasattr(user, "login"):
            user_data["login"] = user.login
            if user_data["login"] == "invalid-email-address" and not "name" in user_data:
                logging.warning("None User",user)
                return None
        self.users_ids[user.node_id] = user_data["anonym_uuid"]
        users_df = pd.concat([users_df,pd.DataFrame([user_data])], ignore_index=True)
        with open(users_file, "wb") as f:
            pickle.dump(users_df, f)
        return user_data["anonym_uuid"]

    def save_pandas_data_frame(self, file:str, data_frame:pd.DataFrame):
        """
        save_list_to_pandas_table(dir, file, data_list)

        Save a data list to a pandas table.

        Parameters
        ----------
        file : str
            Name of the file.
        data_list : list
            list of data dictionarys

        """
        self.current_dir.mkdir(parents=True, exist_ok=True)
        pd_file = Path(self.current_dir, file)
        with open(pd_file, "wb") as f:
            pickle.dump(data_frame, f)
    
    def extract_users(self, users:PaginatedList):
        """
        extract_assignees(github_assignees)

        Get all assignees as one string. 

        Parameters
        ----------
        github_assignees : list
            List of NamedUser.

        Returns
        -------
        str
            String which contains all assignees and are connected with the char &.

        Notes
        -----
            PyGithub NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html

        """
        user_list = []
        for user in users:
            user_list.append(self.extract_user_data(user))
        return user_list

    def extract_author_data_from_commit(self, commit_sha:str):
        """
        extract_author_data_from_commit(repo, sha, users_ids, data_root_dir)

        Extracting general author data from a commit.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        sha : str
            sha from the commit.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Data root directory for the repository.

        Returns
        -------
        str
            Anonym uuid of user.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        if not commit_sha:
            return None
        commit = self.save_api_call(self.repo.get_commit,commit_sha)
        if not commit:
            return None
        if commit._author == GithubObject.NotSet:
            return None
        try:
            return self.extract_user_data(commit.author)
        except:
            return None

    def extract_committer_data_from_commit(self, commit_sha:str):
        """
        extract_committer_data_from_commit(repo, sha, users_ids, data_root_dir)

        Extracting general committer data from a commit.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        sha : str
            sha from the commit.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Data root directory for the repository.

        Returns
        -------
        str
            Anonym uuid of user.

        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        if not commit_sha:
            return None
        commit = self.save_api_call(self.repo.get_commit,commit_sha)
        if not commit:
            return None
        if commit._committer == GithubObject.NotSet:
            return None
        try:
            return self.extract_user_data(commit.committer)
        except:
            return None

    def extract_labels(self, github_labels:PaginatedList):
        """
        extract_labels(github_labels)

        Get all labels as one string.

        Parameters
        ----------
        github_labels : list
            List of Label.

        Returns
        -------
        str
            String which contains all labels and are connected with the char &.

        Notes
        -----
            PyGithub Label object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Label.html

        """
        label_list = []
        for label in github_labels:
            label_list.append(label.name)
        return label_list

    def extract_with_updated_and_since(self, github_method, label:str, data_extraction_function, *args, initial_data_list:PaginatedList=None,initial_total_count:int=None, state:str=None,**kwargs):
        if initial_data_list is None:
            if state is None:
                data_list = self.save_api_call(github_method, sort="updated", direction="asc")
            else:
                data_list = self.save_api_call(github_method, state=state, sort="updated", direction="asc")
        else:
            data_list = initial_data_list
        if initial_total_count is None:
            total_count = self.get_save_total_count(data_list)
        else:
            total_count = initial_total_count
        last_id = 0
        extract_data = True
        while True:
            if total_count >= self.request_maximum:
                self.logger.info(f"{label} >= request_maximum ==> mutiple {label} progress bars")
                total_count = self.request_maximum
            for i in self.progress_bar(range(total_count), f"{label}: "):
                data = self.get_save_api_data(data_list, i)
                if extract_data:
                    data_extraction_function(data, *args, **kwargs)
                elif data.id == last_id:
                    extract_data = True
                else:
                    self.logger.error(f"Skip {label} with ID: {data.id}")
            if total_count == self.request_maximum:
                last_id = data.id
                extract_data = False
                if state is None:
                    data_list = self.save_api_call(github_method, since=data.updated_at, sort="updated", direction="asc")
                else:
                    data_list = self.save_api_call(github_method, state=state, since=data.updated_at, sort="updated", direction="asc")
                total_count = self.get_save_total_count(data_list)
            else:
                break
         
    def progress_bar(self, iterable:typing.Iterable, prefix:str = "", size:int = 60):
        """
        progress_bar(iterable, prefix="", size=60, file=sys.stdout)

        Prints out a progress bar.

        Parameters
        ----------
        iterable : typing.Iterable
            A iterable as input. 
        prefix : str, default=""
            String infront of the progress bar.
        size : int
            Size of the progress bar.

        """
        count = len(iterable)
        def show(j):
            x = int(size*j/count)
            if self.log_level <= logging.INFO:
                sys.stdout.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
                sys.stdout.flush()     
            self.logger_no_print.info("%s[%s%s] %i/%i" % (prefix, "#"*x, "."*(size-x), j, count))
        show(0)
        for i, item in enumerate(iterable):
            yield item
            show(i+1)
        if self.log_level <= logging.INFO:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def copy_valid_params(self, base_dict:dict ,input_params:dict):
        params = base_dict
        for param in input_params:
            if param in params:
                params[param] = input_params[param]
        return params

    def file_error_handling(self, func, path:str, exc_info:str):
        """
        handleError(func, path, exc_info)

        Error handler function which will try to change file permission and call the calling function again.

        Parameters
        ----------
        func : Function
            Calling function.
        path : str
            Path of the file which causes the Error.
        exc_info : str
            Execution information.
        
        """
        
        self.logger.debug('Handling Error for file ' + path)
        self.logger.debug("Catched Error Message:", exc_info=exc_info)
        Core._file_error_handling(func, path, exc_info)

    def apply_datetime_format(self, pd_table:pd.DataFrame, source_column:str, destination_column:str = None):
        """
        apply_datetime_format(pd_table, source_column, destination_column=None)

        Provide equal date formate for all timestamps

        Parameters
        ----------
        pd_table : pandas Dataframe
            List of NamedUser
        source_column : str
            Source column name.
        destination_column : str, default=None
            Destination column name. Saves to Source if None.

        Returns
        -------
        str
            String which contains all assignees.
        
        """
        if not destination_column:
            destination_column = source_column
        pd_table[destination_column] = pd.to_datetime(pd_table[source_column], format="%Y-%m-%d %H:%M:%S")

        return pd_table

    # Debug only
    def print_calls(self, string:str):
        self.github_connection.get_rate_limit()
        requests_remaning, requests_limit = self.github_connection.rate_limiting
        self.logger.debug(f"{string}: {requests_remaning}")

    @staticmethod
    def _file_error_handling(func, path:str, exc_info:str):
        """
        handleError(func, path, exc_info)

        Error handler function which will try to change file permission and call the calling function again.

        Parameters
        ----------
        func : Function
            Calling function.
        path : str
            Path of the file which causes the Error.
        exc_info : str
            Execution information.
        
        """
        # Check if file access issue
        if not os.access(path, os.W_OK):
            # Try to change the permision of file
            os.chmod(path, stat.S_IWUSR)
            # call the calling function again
            func(path)

    @staticmethod
    def get_pandas_data_frame(data_dir:Path, filename:str) -> pd.DataFrame:
        pd_file = Path(data_dir, filename)
        if pd_file.is_file():
            return pd.read_pickle(pd_file)
        else:
            return pd.DataFrame()

 