import os
from pathlib import Path
from typing import Iterable
import numpy
import pandas as pd
import github
import pickle
from human_id import generate_id
import json
import uuid
import time
import sys
import math

from github.MainClass import Github
from github.Reaction import Reaction as GitHubReaction
from github.Repository import Repository as GitHubRepository
from github.PaginatedList import PaginatedList
from github.GithubException import RateLimitExceededException

from pandas.core.frame import DataFrame

from github2pandas.utility import progress_bar

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
    USERS = "Users.p"
    REPO = "Repo.json"
    
    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, current_dir:Path, request_maximum:int = 40000) -> None:
        self.github_connection = github_connection
        self.repo = repo
        self.data_root_dir = data_root_dir
        self.current_dir = current_dir
        df_users = Core.get_users(self.data_root_dir)
        self.users_ids = {}
        for index, row in df_users.iterrows():
            self.users_ids[row["id"]] = row["anonym_uuid"]
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
    
    def get_save_total_count(self, paginated_list:PaginatedList):
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
        print("Waiting for request limit refresh ...")
        self.github_connection.get_rate_limit()
        reset_timestamp = self.github_connection.rate_limiting_resettime
        seconds_until_reset = reset_timestamp - time.time()
        sleep_step_width = 1
        sleeping_range = range(math.ceil(seconds_until_reset / sleep_step_width))
        for i in progress_bar(sleeping_range, "Sleeping : ", 60):
            time.sleep(sleep_step_width)
        self.github_connection.get_rate_limit()
        requests_remaning, requests_limit = self.github_connection.rate_limiting
        while requests_remaning == 0:
            print("No remaining requests sleep 1s ...")
            time.sleep(1)
            self.github_connection.get_rate_limit()
            requests_remaning, requests_limit = self.github_connection.rate_limiting
    
    def check_for_updates_paginated(self, new_paginated_list, list_count, old_df):
        """
        check_for_updates_paginated(new_paginated_list, list_count, old_df)

        Check if if the new paginiated list has updates.

        Parameters
        ----------
        new_paginated_list : PaginatedList
            new paginated list with updated_at and sorted by updated.
        list_count: int
            Length of the paginated List.
        old_df : DataFrame
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
        if not reaction._user == github.GithubObject.NotSet:
            reaction_data["author"] = self.extract_user_data(reaction.user)
        return reaction_data
    
    def extract_user_data(self, user, node_id_to_anonym_uuid=False):
        """
        extract_user_data(user, users_ids, data_root_dir, node_id_to_anonym_uuid=False)

        Extracting general user data.

        Parameters
        ----------
        user : NamedUser
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
        users_file = Path(self.data_root_dir, self.USERS)
        users_df = pd.DataFrame()
        if users_file.is_file():
            users_df = pd.read_pickle(users_file)
        user_data = {}
        if node_id_to_anonym_uuid:
            user_data["anonym_uuid"] = user.node_id
        else:
            user_data["anonym_uuid"] = generate_id(seed=user.node_id)
        user_data["id"] = user.node_id
        if "name" in user_data:
            user_data["name"] = user.name
        if "email" in user_data:
            user_data["email"] = user.email
        if "login" in user_data:
            user_data["login"] = user.login
        if "login" in user_data:
            if user_data["login"] == "invalid-email-address" and not "name" in user_data:
                return None
        self.users_ids[user.node_id] = user_data["anonym_uuid"]
        users_df = users_df.append(user_data, ignore_index=True)
        with open(users_file, "wb") as f:
            pickle.dump(users_df, f)
        return user_data["anonym_uuid"]

    def save_pandas_data_frame(self, file:str, data_frame:DataFrame):
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

    # Debug only:

    def print_calls(self, string:str):
        self.github_connection.get_rate_limit()
        requests_remaning, requests_limit = self.github_connection.rate_limiting
        print(f"{string}: {requests_remaning}")

    @staticmethod
    def get_users(data_root_dir:Path):
        """
        get_users(data_root_dir)

        Get the generated users pandas table.

        Parameters
        ----------
        data_root_dir : Path
            Data root directory for the repository.

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the users data

        """
        users_file = Path(data_root_dir, Core.USERS)
        if users_file.is_file():
            return pd.read_pickle(users_file)
        else:
            return pd.DataFrame()

 