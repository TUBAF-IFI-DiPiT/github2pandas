from asyncio.log import logger
import os
import stat
import typing
import sys
from pathlib import Path
from typing import Any, Union
import pickle
import github
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
    A base class for other classes, contains methods for mutiple modules.

    Attributes
    ----------
    USERS : str
        Name of pandas table file for user data.

    github_connection : Github
        Github object from pygithub.
    repo : GitHubRepository
        Repository object from pygithub.
    repo_data_root_dir : Path
        Data root directory for the repository.
    repo_data_dir : Path
        data directory for the repository.   
    current_dir : Path 
        current data directory.
    request_maximum : int, default=40000
        Maximum amount of returned informations for a general api call.    
    
    log_level : int
        Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET)    
    logger : logging.Logger
        Referenz to a logger object

    users_ids : dict
        Dictionary of User Ids as Keys and anonym Ids as Value.

    Methods
    -------
    __init__(self, github_connection, repo, repo_data_root_dir, current_dir, request_maximum, log_level)
        Initializes core object with general informations.
    save_api_call(function, *args, **kwargs)
        Calls a function or method savely.
    get_save_total_count(paginated_list)
        Gets the total count of a paginated list savely. Waits until request limit is restored.
    get_save_api_data(paginated_list, index)
        Gets one item of the paginated list by index.
    wait_for_reset()
        Waits until request limit is refreshed.
    check_for_updates_paginated(new_paginated_list, list_count, old_df)
        Checks if the new_paginated_list has updates.
    extract_reactions(extract_function, parent_id, parent_name)
        Extracts reactions for element with parent_id by calling of extract_function.
    extract_reaction_data(reaction, parent_id, parent_name)
        Extracts general reaction data.
    extract_user_data(user, node_id_to_anonym_uuid=False)
        Extracts general user data.
    save_pandas_data_frame(file, data_frame)
        Saves the data_frame to a given file.
    extract_users(users)
        Extracts user data based on parameter users and returns a list of anonym user UUIDs. 
    extract_author_data_from_commit(commit_sha)
        Extracts general author data from a commit.
    extract_committer_data_from_commit(commit_sha)
        Extracts general committer data from a commit.
    extract_labels(github_labels)
        Gets all label names as a list.
    extract_with_updated_and_since(github_method, label, data_extraction_function, *args, initial_data_list=None,initial_total_count=None, state=None,**kwargs)
        Extracts and updates data, calls the method git_method and the function data_extraction_function.
    progress_bar(iterable, prefix="", size=60, file=sys.stdout)
        Prints out a progress bar.
    copy_valid_params(base_dict ,input_params)
        Appends base_dict with the elements of input_param, returns the new dictionary.
    file_error_handling(function, path, exc_info)
        Tries to change file permission and call the calling function again.
    apply_datetime_format(pd_table, source_column, destination_column=None)
        Provides equal date formate for all destination_column timestamps.
    _file_error_handling(function, path)
        Tries to change file permission and call the calling function again.
    get_pandas_data_frame(data_dir, filename)
        Returns a pandas data frame stored in file.

    """
    class Params():
        """
        A base class that holds methods for Params classes.

        Methods
        -------
        set_all_true(self, subclasses)
            Sets all parameters to true.
        set_all_false(self, subclasses)
            Sets all parameters to false.
        reset(self)
            Resets all parameters.
        has_true(self)
            Check if there are any true parameters.
        has_false(self)
            Check if there are any false parameters.

        """
        def set_all_true(self, subclasses: bool = True):
            """
            set_all_true(self, subclasses)

            Sets all parameters to true.

            Parameters
            ----------
            subclasses : int, default=True
                Defines if all subparameter classes are set to true.

            Returns
            -------
            Params
                Returns Params class object.

            """
            def func(obj):
                for var, value in vars(obj).items():
                    if isinstance(value,bool):
                        if value == False:
                            obj.__setattr__(var,True)
                    else:
                        if value.__class__.__name__ == "Params" and subclasses:
                            subobj = getattr(obj,var)
                            func(subobj)
            func(self)
            return self

        def set_all_false(self, subclasses: bool = True):
            """
            set_all_false(self, subclasses)

            Sets all parameters to false.

            Parameters
            ----------
            subclasses : int, default=True
                Defines if all subparameter classes are set to false.

            Returns
            -------
            Params
                Returns Params class object.

            """
            def func(obj):
                for var, value in vars(obj).items():
                    if isinstance(value,bool):
                        if value == True:
                            obj.__setattr__(var,False)
                    else:
                        if value.__class__.__name__ == "Params" and subclasses:
                            subobj = getattr(obj,var)
                            func(subobj)
            func(self)
            return self

        def reset(self):
            """
            reset(self)

            Resets all parameters.

            Returns
            -------
            Params
                Returns Params class object.

            """
            self.__init__()
            return self
    
        def has_true(self):
            """
            has_true(self)

            Check if there are any true parameters.

            Returns
            -------
            bool
                Returns true if there are any true parameters.

            """
            for value in vars(self).values():
                if value == True:
                    return True
            return False

        def has_false(self):
            """
            has_false(self)

            Check if there are any false parameters.

            Returns
            -------
            bool
                Returns true if there are any false parameters.

            """
            for value in vars(self).values():
                if value == False:
                    return True
            return False

    class Files():
        """
        A base class that holds methods for Files classes.

        Attributes
        ----------
        DATA_DIR : str
            Base folder name.

        Methods
        -------
        to_list()
            Returns a list of all filenames.
        to_dict()
            Returns a dict with the folder as key and the list of all filenames as value.
        
        """
        DATA_DIR = ""

        @classmethod
        def to_list(cls) -> list:
            """
            to_list(cls)

            Returns a list of all filenames.
            
            Returns
            -------
            list
                List of all filenames.

            """
            filenames = []
            for var, value in vars(cls).items():
                if isinstance(value,str) and var != "DATA_DIR" and not var.startswith("__"):
                    filenames.append(value)
            return filenames

        @classmethod
        def to_dict(cls) -> dict:
            """
            to_dict(cls)
            
            Returns a dict with the folder as key and the list of all filenames as value.
            
            Returns
            -------
            dict
                Dictionary with the folder as key and the list of all filenames as value.

            """
            return {cls.DATA_DIR: cls.to_list()}
    
    class UserFiles(Files):
        """
        A file class that holds the user filename.

        Attributes
        ----------
        USERS : str
            Filename of the users pandas table.

        """
        USERS = "Users.p"

    
    def __init__(self, github_connection:Github, repo:GitHubRepository, repo_data_root_dir:Path, current_dir:str, request_maximum:int = 40000, log_level:int=logging.INFO) -> None:
        """
        __init__(self, github_connection, repo, repo_data_root_dir, current_dir, request_maximum, log_level)

        Initializes core object with general informations.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.
        repo : GitHubRepository
            Repository object from pygithub.
        repo_data_root_dir : Path
            Data root directory for the repository.
        current_dir : Path 
            current data directory.
        request_maximum : int, default=40000
            Maximum amount of returned informations for a general api call.        
        log_level : int
            Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET), default value is enumaration value logging.INFO    
    
        """
        self.log_level = log_level
        self.logger = logging.getLogger("github2pandas")
        self.logger.setLevel(log_level)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.StreamHandler())
        self.logger_no_print = logging.getLogger("github2pandas_no_print")
        self.logger_no_print.setLevel(log_level)
        logging.basicConfig(format='%(levelname)s;%(asctime)s;%(message)s', filename=Path(repo_data_root_dir,"github2pandas.log"))
        self.github_connection = github_connection
        self.repo = repo
        self.repo_data_root_dir = repo_data_root_dir
        if repo is not None:
            self.repo_data_dir = Path(self.repo_data_root_dir,repo.full_name)
            self.repo_data_dir.mkdir(parents=True, exist_ok=True)
            df_users = Core.get_pandas_data_frame(self.repo_data_dir, Core.UserFiles.USERS)
            self.users_ids = {}
            for index, row in df_users.iterrows():
                self.users_ids[row["id"]] = row["anonym_uuid"]
        if current_dir is None or current_dir == "":
            if repo is None:
                self.current_dir = self.repo_data_root_dir
            else:
                self.current_dir = self.repo_data_dir
        else:
            self.current_dir = Path(self.repo_data_dir,current_dir)
        self.request_maximum = request_maximum
    
    def save_api_call(self, function, *args, **kwargs) -> Any: 
        """
        save_api_call(function, *args, **kwargs)

        Calls a function or method savely.

        Parameters
        ----------
        function
            A function/method to call savely.
        *args
            Input for the function/method.
        **kwargs
            Optional input for the function/method.

        Returns
        -------
        Any
            Returns the result of the called function/method.

        """
        try:
            return function(*args, **kwargs)
        except RateLimitExceededException:
            self.wait_for_reset()
            return self.save_api_call(function,*args, **kwargs) 
        except github.GithubException as e:
            if e.data["message"] == "Not Found":
                return None
            else:
                raise e
    
    def get_save_total_count(self, paginated_list:PaginatedList) -> int:
        """
        get_save_total_count(paginated_list)

        Gets the total count of a paginated list savely. Waits until request limit is restored.

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
        except github.GithubException as e:
            if e.data["message"] == "Git Repository is empty.":
                return 0
            else:
                raise e
   
    def get_save_api_data(self, paginated_list:PaginatedList, index:int) -> Any:
        """
        get_save_api_data(paginated_list, index)

        Gets one item of the paginated list by index.

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

    def wait_for_reset(self) -> None:
        """
        wait_for_reset()

        Waits until request limit is refreshed.

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
    
    def check_for_updates_paginated(self, new_paginated_list:PaginatedList, list_count:int, old_df:pd.DataFrame) -> bool:
        """
        check_for_updates_paginated(new_paginated_list, list_count, old_df)

        Checks if the new_paginated_list has updates.

        Parameters
        ----------
        new_paginated_list : PaginatedList
            paginated list with updated_at and sorted by updated.
        list_count: int
            Length of the paginated List.
        old_df : pd.DataFrame
            old Dataframe.

        Returns
        -------
        bool
            True if it need to be updated, False if the List is uptodate.

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

    def extract_reactions(self, extract_function, parent_id:int, parent_name:str) -> list:
        """
        extract_reactions(extract_function, parent_id, parent_name)

        Extracts reactions for element with parent_id by calling of extract_function.

        Parameters
        ----------
        extract_function
            A function to call reactions.
        parent_id : int
            Id from reaction parent element as foreign key.
        parent_name:str
            Name of reaction parent element

        Returns:
        list
            Returns a list of reactions

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

    def extract_reaction_data(self, reaction:GitHubReaction, parent_id:int, parent_name:str) -> dict:
        """
        extract_reaction_data(reaction, parent_id, parent_name)

        Extracts general reaction data.

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
        dict
            reaction_data dictionary with the extracted data.

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
        extract_user_data(user, node_id_to_anonym_uuid=False)

        Extracts general user data.

        Parameters
        ----------
        user : GitHubNamedUser
            NamedUser object from pygithub.
        node_id_to_anonym_uuid : bool
            Node_id will be the anonym_uuid if True, otherwise anonym_uuid is to generate, default=False
        
        Returns
        -------
        Union[str,None]
            Anonym uuid of user as a string or None if the user is a None value.

        Notes
        -----
            PyGithub NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html

        """
        if not user:
            return None
        if user.node_id in self.users_ids:
            return self.users_ids[user.node_id]
        users_file = Path(self.repo_data_dir, Core.UserFiles.USERS)
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

    def save_pandas_data_frame(self, file:str, data_frame:pd.DataFrame) -> None:
        """
        save_pandas_data_frame(file, data_frame)

        Saves the data_frame to a given file.

        Parameters
        ----------
        file : str
            Name of the file.
        data_frame : pd.DataFrame
            DataFrame to save.

        """
        self.current_dir.mkdir(parents=True, exist_ok=True)
        pd_file = Path(self.current_dir, file)
        with open(pd_file, "wb") as f:
            pickle.dump(data_frame, f)
    
    def extract_users(self, users:PaginatedList) -> list:
        """
        extract_users(users)

        Extracts user data based on parameter users and returns a list of anonym user UUIDs. 

        Parameters
        ----------
        users:PaginatedList
            List of NamedUser (GitHubNamedUser).

        Returns
        -------
        list
            contains anonym user UUIDs.

        Notes
        -----
            PyGithub NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html

        """
        user_list = []
        for user in users:
            user_list.append(self.extract_user_data(user))
        return user_list

    def extract_author_data_from_commit(self, commit_sha:str) -> Union[str,None]:
        """
        extract_author_data_from_commit(commit_sha)

        Extracts general author data from a commit.

        Parameters
        ----------
        commit_sha : str
            sha from the commit.

        Returns
        -------
        Union[str,None]
            Returns anonym uuid as a string of user or the value None.

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

    def extract_committer_data_from_commit(self, commit_sha:str) -> Union[str,None]:
        """
        extract_committer_data_from_commit(commit_sha)

        Extracts general committer data from a commit.

        Parameters
        ----------
        commit_sha : str
            sha from the commit.

        Returns
        -------
        Union[str,None]
            Returns anonym uuid as a string of user or the value None.

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

    def extract_labels(self, github_labels:PaginatedList) -> list:
        """
        extract_labels(github_labels)

        Gets all label names as a list.

        Parameters
        ----------
        github_labels : list
            List of Label.

        Returns
        -------
        list
            List which contains all label names.

        Notes
        -----
            PyGithub Label object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Label.html

        """
        label_list = []
        for label in github_labels:
            label_list.append(label.name)
        return label_list

    def extract_with_updated_and_since(self, github_method, label:str, data_extraction_function, *args, initial_data_list:PaginatedList=None,initial_total_count:int=None, state:str=None,**kwargs) -> None:
        """
        extract_with_updated_and_since(github_method, label, data_extraction_function, *args, initial_data_list=None,initial_total_count=None, state=None,**kwargs)

        Extracts and updates data, calls the method git_method and the function data_extraction_function.

        Parameters
        ----------
        github_method
            A github method to call
        label
            label of data type to extract
        data_extraction_function
            An extraction function to call
        *args
            Input for the data_extraction_function
        initial_data_list
            List of initial data
        initial_total_count
            Initial count of requests
        state
            corresponds to the github state of data, allows extracting with state consideration
        **kwargs
            Optional input for data_extraction_function
        """
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
         
    def progress_bar(self, iterable:typing.Iterable, prefix:str = "", size:int = 60) -> None:
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
        if count > 0:
            show(0)
        for i, item in enumerate(iterable):
            yield item
            show(i+1)
        if self.log_level <= logging.INFO:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def copy_valid_params(self, base_dict:dict ,input_params:dict) -> dict:
        """
        copy_valid_params(base_dict ,input_params)

        Appends base_dict with the elements of input_param, returns the new dictionary.

        Parameters
        ----------
        base_dict : dict
            A base dictionary
        input_params : dict
            Dictionary with additial input parameters

        Returns
        -------
        dict
            The appended dictionary
        """
        params = base_dict
        for param in input_params:
            if param in params:
                params[param] = input_params[param]
        return params

    def apply_datetime_format(self, pd_table:pd.DataFrame, source_column:str, destination_column:str = None) -> pd.DataFrame:
        """
        apply_datetime_format(pd_table, source_column, destination_column=None)

        Provides equal date formate for all destination_column timestamps.

        Parameters
        ----------
        pd_table : pd.DataFrame
            DataFrame to change 
        source_column : str
            Source column name.
        destination_column : str, default=None
            Destination column name. Saves to Source if destination_column is None.

        Returns
        -------
        pd.DataFrame
            DataFrame with changed timestamps.
        
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
    def file_error_handling(function, path:str, exc_info=None) -> None:
        """
        file_error_handling(function, path, exc_info)

        Is an error handler function which will try to change file permission and call the calling function again.

        Parameters
        ----------
        function : Function
            Calling function.
        path : str
            Path of the file which causes the Error.
    
        
        """
        # Check if file access issue
        if not os.access(path, os.W_OK):
            # Try to change the permision of file
            os.chmod(path, stat.S_IWUSR)
            # call the calling function again
            function(path)

    @staticmethod
    def get_pandas_data_frame(data_dir:Path, filename:str) -> pd.DataFrame:
        """
        get_pandas_data_frame(data_dir, filename)

        Returns a pandas data frame stored in file, if necessary creates one.

        Parameters
        ----------
        data_dir:Path
            Path to pandas file.
        filename:str
            Filename.

        Returns
        -------
        pd.DataFrame
            Returns pandas data frame stored in file if file exist, otherwise a new data frame object.

        """        
        pd_file = Path(data_dir, filename)
        if pd_file.is_file():
            return pd.read_pickle(pd_file)
        else:
            return pd.DataFrame()

 