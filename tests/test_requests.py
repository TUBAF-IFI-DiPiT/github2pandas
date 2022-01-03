import unittest
import os
from pathlib import Path
import github
import datetime
import shutil
import datetime

from github2pandas.utility import Utility
from github2pandas.git_releases import GitReleases

def run():
    
    github_token = os.environ['TOKEN']

    #git_repo_name = "github2pandas"
    #git_repo_owner = "TUBAF-IFI-DiPiT"
    git_repo_name = "fluentui"
    git_repo_owner = "microsoft"

    default_data_folder = Path("test_data", git_repo_name)
    github_connection = Utility.get_github_connection(github_token)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)

    issues = Utility.save_api_call(repo.get_issues, github_connection, state='all')
    print(github_connection.get_rate_limit())
    total_count = Utility.get_save_total_count(issues, github_connection)
    print(total_count)
    print(github_connection.get_rate_limit())
    counter = 0
    while True:
        saved_issues_objects = []
        for i in range(total_count):
            print(i)
            print(github_connection.get_rate_limit())
            issue = Utility.get_save_api_data(issues,i,github_connection)
            saved_issues_objects.append(issue)
            print(issue.id)
            print(github_connection.get_rate_limit())
        for saved_issues_object in saved_issues_objects:
            print(github_connection.get_rate_limit())
            print(saved_issues_object.id)
            print(github_connection.get_rate_limit())
        break
    for issue in issues:
        print(github_connection.get_rate_limit())
        print(issue.id)
        print(github_connection.get_rate_limit())
        print(issues[counter].id)
        print(github_connection.get_rate_limit())
        issue = Utility.get_save_api_data(issues,counter,github_connection)
        print(issue.id)
        print(github_connection.get_rate_limit())
        counter += 1


    return
    comments = Utility.save_api_call(repo.get_issues_comments, github_token)
    print(f"Issues comment {comments.totalCount}")
    print(f"{comments[0].created_at}")
    #last = comments[40000-1].created_at
    #print(f"{last}")
    last = datetime.datetime(year=2020,month=3,day=18,hour=19,minute=52,second=35)
    #comments = Utility.save_api_call(repo.get_issues_comments, github_token, since=last)
    comments = repo.get_issues(since=last, state="all")
    print(f"Issues {comments.totalCount}")

    return
    remaining_requests = Utility.get_remaining_github_requests(Utility.get_github_connection(github_token))
    print(remaining_requests)
    for i in range(remaining_requests-5):
        repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
    remaining_requests = Utility.get_remaining_github_requests(Utility.get_github_connection(github_token))
    print(remaining_requests)
    
        
if __name__ == "__main__":
    run()
