import unittest
import sys
import os
from pathlib import Path
import warnings
import pandas as pd
import datetime
import time
import shutil
import pickle
import github
import json

from github2pandas.utility import Utility

class TestUtility(unittest.TestCase):
    """
    Test case for Utility class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    default_data_folder = Path("test_data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    users_ids = Utility.get_users_ids(default_data_folder)


    def test_check_for_updates(self):
        class TestData:
            def __init__(self, id, updated_at):
                self.id = id
                self.updated_at = updated_at
        # both empty
        new_list = []
        old_df = pd.DataFrame()
        update = Utility.check_for_updates(new_list, old_df)
        self.assertFalse(update)
        # new list has item
        new_list.append(TestData(0,str(datetime.datetime.now())))
        update = Utility.check_for_updates(new_list, old_df)
        self.assertTrue(update)
        # both equal
        old_df = old_df.append({"id": new_list[0].id, "updated_at": new_list[0].updated_at}, ignore_index=True)
        update = Utility.check_for_updates(new_list, old_df)
        self.assertFalse(update)
        # new list has 1 more item
        new_list.append(TestData(1,str(datetime.datetime.now())))
        update = Utility.check_for_updates(new_list, old_df)
        self.assertTrue(update)
        # both have the same items but new_list has a different id
        old_df = old_df.append({"id": new_list[1].id, "updated_at": new_list[1].updated_at}, ignore_index=True)
        new_list[0].id = 7
        update = Utility.check_for_updates(new_list, old_df)
        self.assertTrue(update)
        # both have the same items but new_list has a different id & updated_at
        time.sleep(1)
        new_list[0].updated_at = str(datetime.datetime.now())
        update = Utility.check_for_updates(new_list, old_df)
        self.assertTrue(update)
        # both have the same items but new_list has a different updated_at
        new_list[0].id = 0
        update = Utility.check_for_updates(new_list, old_df)
        self.assertTrue(update)

    def test_check_for_updates_paginated(self):
        class TestData:
            def __init__(self, id, updated_at):
                self.id = id
                self.updated_at = updated_at
        class PaginatedList:
            def __init__(self):
                self.new_list = []
            @property
            def totalCount(self):
                return len(self.new_list)
            def __iter__(self):
                yield from self.new_list
        # both empty
        new_paginated_list = PaginatedList()
        old_df = pd.DataFrame()
        update = Utility.check_for_updates_paginated(new_paginated_list, old_df)
        self.assertFalse(update)
        # new list has item
        new_paginated_list.new_list.append(TestData(0, datetime.datetime.now()))
        update = Utility.check_for_updates_paginated(new_paginated_list, old_df)
        self.assertTrue(update)
        # both equal
        old_df = old_df.append({"id": new_paginated_list.new_list[0].id, "updated_at": new_paginated_list.new_list[0].updated_at}, ignore_index=True)
        update = Utility.check_for_updates_paginated(new_paginated_list, old_df)
        self.assertFalse(update)
        # new list has 1 more item
        new_paginated_list.new_list.append(TestData(1, datetime.datetime.now()))
        update = Utility.check_for_updates_paginated(new_paginated_list, old_df)
        self.assertTrue(update)
        # both have the same items but new_list has a different id
        old_df = old_df.append({"id": new_paginated_list.new_list[1].id, "updated_at": new_paginated_list.new_list[1].updated_at}, ignore_index=True)
        new_paginated_list.new_list[0].id = 7
        update = Utility.check_for_updates_paginated(new_paginated_list, old_df)
        self.assertTrue(update)
        # both have the same items but new_list has a different id & updated_at
        new_paginated_list.new_list[0].updated_at = datetime.datetime.now()
        update = Utility.check_for_updates_paginated(new_paginated_list, old_df)
        self.assertTrue(update)
        # both have the same items but new_list has a different updated_at
        new_paginated_list.new_list[0].id = 0
        update = Utility.check_for_updates_paginated(new_paginated_list, old_df)
        self.assertTrue(update)

    def test_save_list_to_pandas_table(self):
        data_list = [{"id":0},{"id":1}]
        file = "file.p"
        Utility.save_list_to_pandas_table(self.default_data_folder, file, data_list)
        pd_file = Path(self.default_data_folder, file)
        self.assertTrue(pd_file.is_file())
        os.remove(pd_file)

    def test_get_repo_informations(self):
        repo_file = Path(self.default_data_folder, Utility.REPO)
        with open(repo_file, 'w') as json_file:
            json.dump({"repo_owner": self.git_repo_owner,"repo_name": self.git_repo_name}, json_file)
        owner, name = Utility.get_repo_informations(self.default_data_folder)
        self.assertIsNotNone(owner)
        self.assertIsNotNone(name)
        owner, name = Utility.get_repo_informations("no folder")
        self.assertIsNone(owner)
        self.assertIsNone(name)

    def test_get_repo(self):
        warnings.simplefilter ("ignore", ResourceWarning)
        repo = Utility.get_repo(self.git_repo_owner, self.git_repo_name, self.github_token, self.default_data_folder)
        self.assertIsNotNone(repo)

    def test_github_token_availability(self):
        self.assertTrue( "TOKEN" in os.environ , "No Token available")
    
    def test_apply_datetime_format(self):
        pd_table = pd.DataFrame([{"time": datetime.datetime.now()},{"time": datetime.datetime.now()}])
        pd_table = Utility.apply_datetime_format(pd_table,"time")
        self.assertTrue(len(pd_table.columns) == 1)
        pd_table = Utility.apply_datetime_format(pd_table,"time", "time2")
        self.assertTrue(len(pd_table.columns) == 2)

    def test_get_users(self):
        users_file = Path(self.default_data_folder, Utility.USERS)
        users_df = pd.DataFrame([{"id":0}])
        with open(users_file, "wb") as f:
            pickle.dump(users_df, f)
        users = Utility.get_users(self.default_data_folder)
        self.assertFalse(users.empty)
        users = Utility.get_users("no folder")
        self.assertTrue(users.empty)

    def test_get_users_ids(self):
        users_file = Path(self.default_data_folder, Utility.USERS)
        users_df = pd.DataFrame([{"id":0, "anonym_uuid":"fun-to-run"}])
        with open(users_file, "wb") as f:
            pickle.dump(users_df, f)
        users = Utility.get_users_ids(self.default_data_folder)
        self.assertTrue(len(users.keys()) == 1)
        users = Utility.get_users_ids("no folder")
        self.assertTrue(len(users.keys()) == 0)

    def test_extract_assignees(self):
        class UserData:
             node_id = "test_extract_assignees"
             name = "test_extract_assignees"
             email = "test_extract_assignees@test.de"
             login = "test_extract_assignees"
        assignees = Utility.extract_assignees([UserData()], self.users_ids, self.default_data_folder)
        self.assertTrue(len(assignees) > 0)
        assignees2 = Utility.extract_assignees([UserData(),UserData()], self.users_ids, self.default_data_folder)
        self.assertTrue(assignees2 == assignees + "&" + assignees)

    def test_extract_labels(self):
        class Label:
            name = "test_extract_labels"
        labels = Utility.extract_labels([Label()])
        self.assertTrue(labels == "test_extract_labels")
        labels = Utility.extract_labels([Label(),Label()])
        self.assertTrue(labels == "test_extract_labels&test_extract_labels")
    
    def test_extract_user_data(self):
        class UserData:
             node_id = "test_extract_user_data"
             name = "test_extract_user_data"
             email = "test_extract_user_data@test.de"
             login = "test_extract_user_data"
        user = Utility.extract_user_data(None, self.users_ids, self.default_data_folder)
        self.assertIsNone(user)
        old_user_id_len = len(self.users_ids.keys())
        user = Utility.extract_user_data(UserData(), self.users_ids, self.default_data_folder)
        self.assertIsNotNone(user)
        self.assertFalse(old_user_id_len == len(self.users_ids.keys()))
        old_user_id_len = len(self.users_ids.keys())
        user = Utility.extract_user_data(UserData(), self.users_ids, self.default_data_folder)
        self.assertIsNotNone(user)
        self.assertTrue(old_user_id_len == len(self.users_ids.keys()))
    
    def test_extract_author_data_from_commit(self):
        for commit in self.repo.get_commits():
            author = Utility.extract_author_data_from_commit(self.repo, commit.sha, self.users_ids, self.default_data_folder)
            self.assertIsNotNone(author)
            break
    
    def test_extract_committer_data_from_commit(self):
        for commit in self.repo.get_commits():
            author = Utility.extract_committer_data_from_commit(self.repo, commit.sha, self.users_ids, self.default_data_folder)
            self.assertIsNotNone(author)
            break
    
    def test_extract_reaction_data(self):
        class User:
             node_id = "test_extract_reaction_data"
             name = "test_extract_reaction_data"
             email = "test_extract_reaction_data@test.de"
             login = "test_extract_reaction_data"
        class Reaction:
            content = "test_extract_reaction_data"
            created_at = datetime.datetime.now()
            id = 0
            _user = User()
            user = User()
        
        reaction_data = Utility.extract_reaction_data(Reaction(),12345,"test",self.users_ids, self.default_data_folder)
        self.assertIsNotNone(reaction_data)
        reaction = Reaction()
        reaction._user = github.GithubObject.NotSet
        reaction_data = Utility.extract_reaction_data(reaction,12345,"test",self.users_ids, self.default_data_folder)
        self.assertIsNotNone(reaction_data)
        self.assertFalse("author" in reaction_data.keys())
    
    def test_extract_event_data(self):
        class Label:
            name = "test_extract_event_data"
        class User:
             node_id = "test_extract_event_data"
             name = "test_extract_event_data"
             email = "test_extract_event_data@test.de"
             login = "test_extract_event_data"
        class Event:
            _actor = User()
            actor = User()
            commit_id = "test_extract_reaction_data"
            event = "test_extract_reaction_data"
            created_at = datetime.datetime.now()
            id = 0
            _label = Label()
            label = Label()
            _assignee = User()
            assignee = User()
            _assigner = User()
            assigner = User()
        event_data = Utility.extract_event_data(Event(),0,"test",self.users_ids, self.default_data_folder)
        self.assertIsNotNone(event_data)
        event = Event()
        event._actor = github.GithubObject.NotSet
        event._label = github.GithubObject.NotSet
        event._assignee = github.GithubObject.NotSet
        event._assigner = github.GithubObject.NotSet
        event_data = Utility.extract_event_data(event,0,"test",self.users_ids, self.default_data_folder)
        self.assertIsNotNone(event_data)
        self.assertFalse("author" in event_data.keys())
        self.assertFalse("label" in event_data.keys())
        self.assertFalse("assignee" in event_data.keys())
        self.assertFalse("assigner" in event_data.keys())

    def test_extract_comment_data(self):
        class User:
             node_id = "test_extract_comment_data"
             name = "test_extract_comment_data"
             email = "test_extract_comment_data@test.de"
             login = "test_extract_comment_data"
        class Comment:
            body = "test_extract_comment_data"
            created_at = datetime.datetime.now()
            id = 0
            _user = User()
            user = User()
        
        comment_data = Utility.extract_comment_data(Comment(),12345,"test",self.users_ids, self.default_data_folder)
        self.assertIsNotNone(comment_data)
        comment = Comment()
        comment._user = github.GithubObject.NotSet
        comment_data = Utility.extract_comment_data(comment,12345,"test",self.users_ids, self.default_data_folder)
        self.assertIsNotNone(comment_data)
        self.assertFalse("author" in comment_data.keys())

    def test_define_unknown_user(self):
        class User:
             node_id = "test_define_unknown_user"
             name = "test_define_unknown_user"
             email = "test_define_unknown_user@test.de"
             login = "test_define_unknown_user"
        user = Utility.extract_user_data(User(), self.users_ids, self.default_data_folder)
        new_user = Utility.define_unknown_user({"test":user},"test",self.default_data_folder)
        class User2:
             node_id = "test_define_unknown_user2"
             name = "test_define_unknown_use2r"
             email = "test_define_unknown_user2@test.de"
             login = "test_define_unknown_user2"
        user2 = Utility.extract_user_data(User2(), self.users_ids, self.default_data_folder)
        new_user = Utility.define_unknown_user({"test2":user2},"test2",self.default_data_folder)
        new_user = Utility.define_unknown_user({"test3":user2},"test3",self.default_data_folder)
        new_user = Utility.define_unknown_user({"test3":user2},"test3",self.default_data_folder)
        print(Utility.get_users(self.default_data_folder))

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")
        self.users_ids = {}

if __name__ == "__main__":
    unittest.main()
