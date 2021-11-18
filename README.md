# Transform GitHub Activities to Pandas Dataframes

## General information

This package is being developed by the participating partners (TU Bergakademie Freiberg, OVGU Magdeburg and HU Berlin) as part of the DiP-iT project [Website](http://dip-it.ovgu.de/).

The package implements Python functions for 
+ aggregating and preprocessing GitHub activities (Commits, Actions, Issues, Pull-Requests) and 
+ generating project progress summaries according to different metrics (ratio of changed lines, ratio of aggregated Levenshtein distances e.g.).

`github2pandas` stores the collected information in a collection of pandas DataFrames starting from a user defined root folder. The structure beyond that (file names, folder names) is defined as a member variable in the corresponding classes and can be overwritten. The default configuration results in the following file structure.

```
|-- My_Github_Repository_0               <- Repository name
|   |- Repo.json                         <- Json file containing user and repo name
|   |- Repository
|   |   |- Repository.p  
|   |- Issues
|   |   |- pdIssuesComments.p
|   |   |- pdIssuesEvents.p
|   |   |- pdIssues.p
|   |   |- pdIssuesReactions.p
|   |- PullRequests
|   |   |- pdPullRequestsComments.p
|   |   |- pdPullRequestsCommits.p
|   |   |- pdPullRequestsEvents.p
|   |   |- pdPullRequests.p
|   |   |- pdPullRequestsReactions.p
|   |   |- pdPullRequestsReviews.p
|   |- Users.p
|   |- Versions
|   |   |- pdCommits.p
|   |   |- pdEdits.p
|   |   |- pdBranches.p
|   |   |- pVersions.db
|   |   |- repo                         <- Repository clone
|   |   |   |- ..
|   |- Workflows
|       |- pdWorkflows.p
|-- My_Github_Repository_1
...
```
The internal structure and relations of the data frames are included in the project's [wiki](https://github.com/TUBAF-IFI-DiPiT/github2pandas/wiki).

## Installation

`github2pandas` is available on [pypi](https://pypi.org/project/github2pandas/). Use pip to install the package.

### global

On Linux:

```
sudo pip3 install github2pandas 
sudo pip install github2pandas
```

On Windows as admin or for one user:

```
pip install github2pandas
pip install --user github2pandas 
```

### in virtual environment:

```
pipenv install github2pandas
```

## Usage  

GitHub token is required for use, which is used for authentication. The [website](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) describes how you can generate this for your GitHub account. Customise the username and project name and explore any public or private repository you have access to with your account!

Access token is to define in `.env` oder `.py (.ipynb)` file. The default value of python.envFile setting is `${workspaceFolder}/.env`

```
TOKEN="example_token"
```

An short example of a python script:

```
import os

from github2pandas.issues import Issues
from github2pandas.utility import Utility
from pathlib import Path

git_repo_name = "github2pandas"
git_repo_owner = "TUBAF-IFI-DiPiT"
    
default_data_folder = Path("data", git_repo_name)
github_token = os.environ['TOKEN']

repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)
Issues.generate_issue_pandas_tables(repo, default_data_folder)
issues = Issues.get_issues(default_data_folder,Issues.ISSUES)

# List the last 14 issue entries
issues.head(14)
```

## Notebook examples

The corresponding [github2pandas_notebooks](https://github.com/TUBAF-IFI-DiPiT/github2pandas_notebooks/blob/main/README.md) repository illustrates the usage with examplary investigations.

The documentation of the module is available at [https://github2pandas.readthedocs.io/](https://github2pandas.readthedocs.io/).

## Working with pipenv

| Process                                     | Command                                                 |
| ------------------------------------------- | ------------------------------------------------------- |
| Installation                                | `pipenv install --dev`                                  |
| Run specific script                         | `pipenv run python file.py`                             |
| Run all Tests                               | `pipenv run python -m unittest`                         |
| Run all tests in a specific folder          | `pipenv run python -m unittest discover -s 'tests'`     |
| Run all tests with specific filename        | `pipenv run python -m unittest discover -p 'test_*.py'` |
| Start Jupyter server in virtual environment | `pipenv run jupyter notebook`                           | 

# For Contributors

Naming conventions: https://namingconvention.org/python/
