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

from github.MainClass import Github
from github.PaginatedList import PaginatedList
from github.GithubException import RateLimitExceededException

from pandas.core.frame import DataFrame

class Utility():
    """
    Class which contains methods for mutiple modules.

    Attributes
    ----------
    USERS : str
        Pandas table file for user data.
    REPO : str
       Json file for general repository informations.

    Methods
    -------
        check_for_updates(new_list, old_df)
            Check if id and updated_at are in the old_df.
        check_for_updates_paginated(new_paginated_list, list_count, old_df)
            Check if if the new paginiated list has updates.
        save_list_to_pandas_table(dir, file, data_list)
            Save a data list to a pandas table.
        get_repo_informations(data_root_dir)
            Get a repository data (owner and name).
        get_repos(token, data_root_dir, whitelist_patterns=None, blacklist_patterns=None)
            Get mutiple repositorys by pattern and token.
        get_repo(repo_owner, repo_name, token, data_root_dir)
            Get a repository by owner, name and token.
        apply_datetime_format(pd_table, source_column, destination_column=None)
            Provide equal date formate for all timestamps.
        get_users(data_root_dir)
            Get the generated users pandas table.
        get_users_ids(data_root_dir)
            Get the generated useres as dict whith github ids as keys and anonym uuids as values.
        extract_assignees(github_assignees, users_ids, data_root_dir)
            Get all assignees as one string.
        extract_labels(github_labels)
            Get all labels as one string.
        extract_user_data(user, users_ids, data_root_dir, node_id_to_anonym_uuid=False)
            Extracting general user data.
        extract_author_data_from_commit(repo, sha, users_ids, data_root_dir)
            Extracting general author data from a commit.
        extract_committer_data_from_commit(repo, sha, users_ids, data_root_dir)
            Extracting general committer data from a commit.
        extract_reaction_data(reaction, parent_id, parent_name, users_ids, data_root_dir)
            Extracting general reaction data.
        extract_event_data(event, parent_id, parent_name, users_ids, data_root_dir)
            Extracting general event data from a issue or pull request.
        extract_comment_data(comment, parent_id, parent_name, users_ids, data_root_dir)
            Extracting general comment data from a pull request or issue.
        define_unknown_user(unknown_user_name, uuid, data_root_dir, new_user=False)
            Defines a unknown user. Add unknown user to alias or creates new user
        get_save_total_count(paginated_list, github_connection)
            Get the total count of a paginated list savely. Waits until request limit is restored.
        get_save_api_data(paginated_list, index, github_connection)
            Get one item of the paginated list by index.
        save_api_call(function, github_connection, *args, **kwargs)
            Call a function or method savely.
        progress_bar(iterable, prefix="", size=60, file=sys.stdout)
            Prints our a progress bar.
        wait_for_reset(github_connection)
             Wait until request limit is refreshed.
        get_github_connection(github_token)
            Get the main GitHub connection.
    
    """
    USERS = "Users.p"
    REPO = "Repo.json"
    
    @staticmethod
    def check_for_updates(new_list, old_df):
        """
        check_for_updates(new_list, old_df)

        Check if id and updated_at are in the old_df.

        Parameters
        ----------
        new_list : list
            new list with id and updated_at.
        old_df : DataFrame
            old Dataframe.

        Returns
        -------
        bool
            True if the repo needs to be updated. False the List is uptodate.

        """
        if old_df.empty:
            if len(new_list) == 0:
                return False
            return True
        if not len(new_list) == old_df.count()[0]:
            return True
        for new_class in new_list:
            df = old_df.loc[((old_df.id == new_class.id) & (old_df.updated_at == new_class.updated_at))]
            if df.empty:
                return True
        return False
    
    @staticmethod
    def check_for_updates_paginated(new_paginated_list, list_count, old_df):
        """
        check_for_updates_paginated(new_paginated_list, list_count, old_df)

        Check if if the new paginiated list has updates.

        Parameters
        ----------
        new_paginated_list : PaginatedList
            new paginated list with updated_at and sorted by updated
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
        last_update = old_df["updated_at"].max()
        if new_paginated_list[0].updated_at != last_update:
            return True
        return False
    
    @staticmethod
    def check_for_updates_paginated_old(new_paginated_list, old_df):
        """
        check_for_updates_paginated_old(new_paginated_list, old_df)

        Check if id and updated_at are in the old_df.

        Parameters
        ----------
        new_paginated_list : PaginatedList
            new paginated list with id and updated_at.
        old_df : DataFrame
            old Dataframe.

        Returns
        -------
        bool
            True if it need to be updated. False the List is uptodate.

        """
        import sys
        if old_df.empty:
            # .totalCount crashes in case of a total empty repository
            try:
                count = new_paginated_list.totalCount
            except:
                return False
            if count == 0:
                return False
            return True
        if not new_paginated_list.totalCount == old_df.count()[0]:
            return True
        for new_class in new_paginated_list:
            try:
                df = old_df.loc[((old_df.id == new_class.id) & (old_df.updated_at == new_class.updated_at))]
                if df.empty:
                    return True
            except:
                return False
        return False

    @staticmethod
    def save_list_to_pandas_table(dir, file, data_list):
        """
        save_list_to_pandas_table(dir, file, data_list)

        Save a data list to a pandas table.

        Parameters
        ----------
        dir : str
            Path to the desired save dir.
        file : str
            Name of the file.
        data_list : list
            list of data dictionarys

        """
        Path(dir).mkdir(parents=True, exist_ok=True)
        data_frame_ = pd.DataFrame(data_list)
        pd_file = Path(dir, file)
        with open(pd_file, "wb") as f:
            pickle.dump(data_frame_, f)
    
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
        repo_file = Path(data_root_dir, Utility.REPO)
        if repo_file.is_file():
            with open(repo_file, 'r') as json_file:
                repo_data = json.load(json_file)
                return (repo_data["repo_owner"], repo_data["repo_name"])
        return None, None
    
    @staticmethod
    def get_repos(token, data_root_dir, whitelist_patterns=None, blacklist_patterns=None):
        """
        get_repos(token, data_root_dir, whitelist_patterns=None, blacklist_patterns=None)

        Get mutiple repositorys by mutiple pattern and token.

        Parameters
        ----------
        token : str
            A valid Github Token.
        data_root_dir : str
            Data root directory for the repositorys.
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

        g = github.Github(token)
        relevant_repos = []
        for repo in g.get_user().get_repos():
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
                    repo_dir = Path(data_root_dir, repo.owner.login + "/" + repo.name)
                    repo_dir.mkdir(parents=True, exist_ok=True)
                    repo_file = Path(repo_dir, Utility.REPO)
                    with open(repo_file, 'w') as json_file:
                        json.dump({"repo_owner": repo.owner.login,"repo_name":repo.name}, json_file)
                    relevant_repos.append(repo)
        return relevant_repos

    @staticmethod      
    def get_repo(repo_owner, repo_name, token, data_root_dir:Path):
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
        g = github.Github(token,per_page=100)
        data_root_dir.mkdir(parents=True, exist_ok=True)
        repo_file = Path(data_root_dir, Utility.REPO)
        with open(repo_file, 'w') as json_file:
            json.dump({"repo_owner": repo_owner,"repo_name":repo_name}, json_file)
        return Utility.save_api_call(g.get_repo, token, repo_owner + "/" + repo_name)
    
    @staticmethod
    def apply_datetime_format(pd_table, source_column, destination_column=None):
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
        users_file = Path(data_root_dir, Utility.USERS)
        if users_file.is_file():
            return pd.read_pickle(users_file)
        else:
            return pd.DataFrame()

    @staticmethod
    def get_users_ids(data_root_dir:Path):
        """
        get_users_ids(data_root_dir)

        Get the generated useres as dict whith github ids as keys and anonym uuids as values.

        Parameters
        ----------
        data_root_dir : Path
            Data root directory for the repository.

        Returns
        -------
        dict
            Dict whith github ids as keys and anonym uuids as values.

        """
        df_users = Utility.get_users(data_root_dir)
        users_ids = {}
        for index, row in df_users.iterrows():
            users_ids[row["id"]] = row["anonym_uuid"]
        return users_ids

    @staticmethod
    def extract_assignees(github_assignees, users_ids, data_root_dir):
        """
        extract_assignees(github_assignees, users_ids, data_root_dir)

        Get all assignees as one string. 

        Parameters
        ----------
        github_assignees : list
            List of NamedUser.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Data root directory for the repository.

        Returns
        -------
        str
            String which contains all assignees and are connected with the char &.

        Notes
        -----
            PyGithub NamedUser object structure: https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html

        """
        assignees = ""
        for assignee in github_assignees:
            assignees += Utility.extract_user_data(assignee, users_ids, data_root_dir) + "&"
        if len(assignees) > 0:
            assignees = assignees[:-1]
        return assignees

    @staticmethod
    def extract_labels(github_labels):
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
        labels = ""
        for label in github_labels:
            labels += label.name + "&"
        if len(labels) > 0:
            labels = labels[:-1]
        return labels

    @staticmethod
    def extract_user_data(user, users_ids, data_root_dir, node_id_to_anonym_uuid=False):
        """
        extract_user_data(user, users_ids, data_root_dir, node_id_to_anonym_uuid=False)

        Extracting general user data.

        Parameters
        ----------
        user : NamedUser
            NamedUser object from pygithub.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Repo dir of the project.
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
        if user.node_id in users_ids:
            return users_ids[user.node_id]
        users_file = Path(data_root_dir, Utility.USERS)
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
        users_ids[user.node_id] = user_data["anonym_uuid"]
        users_df = users_df.append(user_data, ignore_index=True)
        with open(users_file, "wb") as f:
            pickle.dump(users_df, f)
        return user_data["anonym_uuid"]
    
    @staticmethod
    def extract_author_data_from_commit(repo, sha, users_ids, data_root_dir):
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
        if not sha:
            return None
        commit = repo.get_commit(sha)
        if not commit:
            return None
        if commit._author == github.GithubObject.NotSet:
            return None
        return Utility.extract_user_data(commit.author, users_ids, data_root_dir)
               
    @staticmethod
    def extract_committer_data_from_commit(repo, sha, users_ids, data_root_dir):
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
        if not sha:
            return None
        commit = repo.get_commit(sha)
        if not commit:
            return None
        if commit._committer == github.GithubObject.NotSet:
            return None
        return Utility.extract_user_data(commit.committer, users_ids, data_root_dir)

    @staticmethod
    def extract_reaction_data(reaction, parent_id, parent_name, users_ids, data_root_dir):
        """
        extract_reaction_data(reaction, parent_id, parent_name, users_ids, data_root_dir)

        Extracting general reaction data.

        Parameters
        ----------
        reaction : Reaction
            Reaction object from pygithub.
        parent_id : int
            Id from parent as foreign key.
        parent_name : str
            Name of the parent.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Repo dir of the project.

        Returns
        -------
        ReactionData
            Dictionary with the extracted data.

        Notes
        -----
            Reaction object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Reaction.html

        """
        reaction_data = {} 
        reaction_data[parent_name + "_id"] = parent_id
        reaction_data["content"] = reaction.content
        reaction_data["created_at"] = reaction.created_at
        reaction_data["id"] = reaction.id
        if not reaction._user == github.GithubObject.NotSet:
            reaction_data["author"] = Utility.extract_user_data(reaction.user, users_ids, data_root_dir)
        return reaction_data
    
    @staticmethod
    def extract_event_data(event, parent_id, parent_name,users_ids, data_root_dir):
        """
        extract_event_data(event, parent_id, parent_name, users_ids, data_root_dir)

        Extracting general event data from a issue or pull request.

        Parameters
        ----------
        even t: IssueEvent
            IssueEvent object from pygithub.
        parent_id : int
            Id from parent as foreign key.
        parent_name : str
            Name of the parent.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Repo dir of the project.

        Returns
        -------
        EventData
            Dictionary with the extracted data.

        Notes
        -----
            IssueEvent object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueEvent.html

        """
        issue_event_data = {}
        issue_event_data[parent_name + "_id"] = parent_id
        if not event._actor == github.GithubObject.NotSet:
            issue_event_data["author"] = Utility.extract_user_data(event.actor, users_ids, data_root_dir)
        if not event._assignee == github.GithubObject.NotSet:
            issue_event_data["assignee"] = Utility.extract_user_data(event.assignee, users_ids, data_root_dir)
        if not event._assigner == github.GithubObject.NotSet:
            issue_event_data["assigner"] = Utility.extract_user_data(event.assigner, users_ids, data_root_dir)
        issue_event_data["commit_sha"] = event.commit_id
        issue_event_data["created_at"] = event.created_at
        # dismissed_review ?
        issue_event_data["event"] = event.event
        issue_event_data["id"] = event.id
        if not event._label == github.GithubObject.NotSet:
            issue_event_data["label"] = event.label.name
        issue_event_data["last_modified"] = event.last_modified
        # lock_reason ?
        # milestone ?
        # node_id ?
        # rename ?
        # requested_reviewer ?
        # review_requesters ?
        return issue_event_data
    
    @staticmethod
    def extract_comment_data(comment, parent_id, parent_name, users_ids, data_root_dir):
        """
        extract_comment_data(comment, parent_id, parent_name, users_ids, data_root_dir)

        Extracting general comment data from a pull request or issue.

        Parameters
        ----------
        comment : github_object 
            PullRequestComment or IssueComment object from pygithub.
        parent_id : int
            Id from parent as foreign key.
        parent_name : str
            Name of the parent.
        users_ids : dict
            Dict of User Ids as Keys and anonym Ids as Value.
        data_root_dir : str
            Repo dir of the project.

        Returns
        -------
        CommentData
            Dictionary with the extracted data.

        Notes
        -----
            PullRequestComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestComment.html
            IssueComment object structure: https://pygithub.readthedocs.io/en/latest/github_objects/IssueComment.html

        """
        comment_data = {}
        comment_data[parent_name + "_id"] = parent_id
        comment_data["body"] = comment.body
        comment_data["created_at"] = comment.created_at
        comment_data["id"] = comment.id
        if not comment._user == github.GithubObject.NotSet:
            comment_data["author"] = Utility.extract_user_data(comment.user, users_ids, data_root_dir)
        return comment_data
    
    @staticmethod
    def define_unknown_user(unknown_user_name, uuid, data_root_dir, new_user=False):
        """
        define_unknown_user(unknown_user_name, uuid, data_root_dir, new_user=False)

        Defines a unknown user. Add unknown user to alias or creates new user

        Parameters
        ----------
        unknown_user_name: str
            Name of unknown user. 
        uuid: str
            Uuid can be the anonym uuid of another user or random uuid for a new user. 
        data_root_dir : str
            Data root directory for the repository.
        new_user : bool, default=False
            A complete new user with anonym_uuid will be generated.

        Returns
        -------
        str
            Uuid of the user.

        """
        users = Utility.get_users(data_root_dir)
        p_user = users.loc[users.anonym_uuid == uuid]
        if not p_user.empty:
            alias = ""
            user = p_user.iloc[0]
            if "alias" in user:
                if pd.isnull(user["alias"]) or (user["alias"] is None):
                    alias = unknown_user_name
                else:
                    all_alias = user["alias"].split(';')
                    if not unknown_user_name in all_alias:
                        alias = user["alias"] + ";" + unknown_user_name
                    else:
                        alias = user["alias"]
            else:
                alias = unknown_user_name
            users.loc[users.anonym_uuid == uuid, 'alias'] = alias
            pd_file = Path(data_root_dir, Utility.USERS)
            with open(pd_file, "wb") as f:
                pickle.dump(users, f)
            return user["anonym_uuid"]
        
        class UserData:
            node_id = uuid
            name = unknown_user_name
            email = numpy.NaN
            login = numpy.NaN
        users_ids = Utility.get_users_ids(data_root_dir)
        if new_user:
            return Utility.extract_user_data(UserData(),users_ids,data_root_dir)
        return Utility.extract_user_data(UserData(),users_ids,data_root_dir, node_id_to_anonym_uuid=True)

    @staticmethod
    def get_github_connection(github_token:str):
        """
        get_github_connection(github_token)

        Get the main GitHub connection.

        Parameters
        ----------
        github_token : str
            A valid GitHub token.

        Returns
        -------
        Github
            Github object from pygithub.

        """
        return Github(github_token)

    @staticmethod
    def wait_for_reset(github_connection):
        """
        wait_for_reset(github_connection)

        Wait until request limit is refreshed.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.

        """
        print("Waiting for request limit refresh ...")
        github_connection.get_rate_limit()
        reset_timestamp = github_connection.rate_limiting_resettime
        seconds_until_reset = reset_timestamp - time.time()
        sleep_step_width = 1
        sleeping_range = range(int(seconds_until_reset / sleep_step_width))
        for i in Utility.progress_bar(sleeping_range, "Sleeping : ", 60):
            time.sleep(sleep_step_width)
        github_connection.get_rate_limit()
        requests_remaning, requests_limit = github_connection.rate_limiting
        while requests_remaning == 0:
            print("No remaining requests sleep 1s ...")
            time.sleep(1)
            github_connection.get_rate_limit()
            requests_remaning, requests_limit = github_connection.rate_limiting

    @staticmethod
    def progress_bar(iterable:Iterable, prefix="", size:int=60, file=sys.stdout):
        """
        progress_bar(iterable, prefix="", size=60, file=sys.stdout)

        Prints our a progress bar.

        Parameters
        ----------
        iterable : Iterable
            A iterable as input. 
        prefix : str, default=""
            String infront of the progress bar.
        size : int
            Size of the progress bar.
        file : Any , default=sys.stdout
            File to print out the progress bar.

        """
        count = len(iterable)
        def show(j):
            x = int(size*j/count)
            file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
            file.flush()        
        show(0)
        for i, item in enumerate(iterable):
            yield item
            show(i+1)
        file.write("\n")
        file.flush()

    @staticmethod
    def save_api_call(function, github_connection:Github, *args, **kwargs):
        """
        save_api_call(function, github_connection, *args, **kwargs)

        Call a function or method savely.

        Parameters
        ----------
        function : Any
            A function/method to call savely.
        github_connection : Github
            Github object from pygithub.
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
            Utility.wait_for_reset(github_connection)
            return function(*args, **kwargs) 
    
    @staticmethod
    def get_save_api_data(paginated_list:PaginatedList, index:int, github_connection:Github):
        """
        get_save_api_data(paginated_list, index, github_connection)

        Get one item of the paginated list by index.

        Parameters
        ----------
        paginated_list : PaginatedList
            A paginated list as input. 
        index : int
            Index to get from the paginated list.
        github_connection : Github
            Github object from pygithub.

        Returns
        -------
        int
            Total count of the paginated list.

        """
        try:
            return paginated_list[index]
        except RateLimitExceededException:
            Utility.wait_for_reset(github_connection)
            return paginated_list[index]
    
    @staticmethod
    def get_save_total_count(paginated_list:PaginatedList, github_connection:Github):
        """
        get_save_total_count(paginated_list, github_connection)

        Get the total count of a paginated list savely. Waits until request limit is restored.

        Parameters
        ----------
        paginated_list : PaginatedList
            A paginated list as input. 
        github_connection : Github
            Github object from pygithub.

        Returns
        -------
        int
            Total count of the paginated list.

        """
        try:
            return paginated_list.totalCount
        except RateLimitExceededException:
            Utility.wait_for_reset(github_connection)
            return paginated_list.totalCount
    
    @staticmethod
    def save_pandas_data_frame(dir_path:Path, file:str, data_frame:DataFrame):
        """
        save_list_to_pandas_table(dir, file, data_list)

        Save a data list to a pandas table.

        Parameters
        ----------
        dir : str
            Path to the desired save dir.
        file : str
            Name of the file.
        data_list : list
            list of data dictionarys

        """
        dir_path.mkdir(parents=True, exist_ok=True)
        pd_file = Path(dir_path, file)
        with open(pd_file, "wb") as f:
            pickle.dump(data_frame, f)

    
    #@staticmethod
    #def get_collaborators(repo, user_ids, data_root_dir):
    #    collaborators = repo.get_collaborators()
    #    for collaborator in collaborators:
    #        Utility.extract_user_data(collaborator,user_ids,data_root_dir)