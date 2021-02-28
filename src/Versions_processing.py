import sys
import os
import pandas as pd
from pathlib import Path

from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Versions_aggregation import getCommitRawPandasTable

# Polishing data
def manageAuthorDublicates(pdCommitsRaw, 
                           dublicate_names = [],
                           dublicate_emails = []):
    """
    Polishing the pandas commit table:
        - Insert a space into author_names without space between first
          name and surname.
        - Make email addresses constant for specific authors

    :param pandas_commits_table: a pandas workflow table from git2net is
    :required, so use getCommitPandasTable() first
    :return: cleaned pandas_commits_table
    """
    # taking care about names without the space
    dublicate_names = dublicate_names

    # taking care about different email adresses
    # we definitely need a better algo for replacing unofficial email
    # addresses, like if email adresses aren't something with tu-freiberg then
    # use one of the other given consistently
    dublicate_emails = dublicate_emails

    for name in dublicate_names:
        pdCommitsRaw['author_name'].replace(name[0], name[1],
                                                    inplace=True)

    for email in dublicate_emails:
        pdCommitsRaw['author_email'].replace(email[0], email[1],
                                                     inplace=True)

    return pdCommitsRaw

def applyPythonDateFormat(pdCommitsRaw):
  print("Adapt date formates")
  pdCommitsRaw['timestamp'] = pd.to_datetime(pdCommitsRaw['author_date'], format="%Y-%m-%d %H:%M:%S")
  return pdCommitsRaw

def identifyCommitsInBranches(pdCommitsRaw):
  pdCommitsRaw["in_dev_branches"] = pdCommitsRaw.branches.apply(lambda x: True if len(set(x.split(","))- set(["master"])) > 0 else False)
  return pdCommitsRaw

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
      getCommitRawPandasTable(default_data_folder)
      .pipe(applyPythonDateFormat)
      .pipe(manageAuthorDublicates, dublicate_names, dublicate_emails)
      .pipe(identifyCommitsInBranches)
    )

    print(result.head(3))