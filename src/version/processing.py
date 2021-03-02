import sys
import os
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.version.aggregation import get_commit_raw_pandas_table
from src.utility import apply_python_date_format, manage_author_dublicates

def identify_commits_in_branches(pd_commits_raw):
  pd_commits_raw["in_dev_branches"] = pd_commits_raw.branches.apply(lambda x: True if len(set(x.split(","))- set(["master"])) > 0 else False)
  return pd_commits_raw

# For fast local testing. Can be removed when module is done.
if __name__ == "__main__":
    git_repo_name = "xAPI_for_GitHubData"
    default_repo_folder = Path("repos", git_repo_name)
    default_data_folder = Path("data", git_repo_name)

    dublicate_names = [
        ('SebastianZug', 'Sebastian Zug')
    ]
    dublicate_emails = [
        ('zug@pop-os.localdomain', 'Sebastian.Zug@informatik.tu-freiberg.de')
    ]
 
    result = (
      get_commit_raw_pandas_table(default_data_folder)
      .pipe(apply_python_date_format)
      .pipe(manage_author_dublicates, dublicate_names, dublicate_emails)
      .pipe(identify_commits_in_branches)
    )

    print(result.head(3))