# Transform GitHub Activities to Pandas Dataframes

## General information

This package is being developed by the participating partners (TU Bergakademie Freiberg, OVGU Magdeburg and HU Berlin) as part of the DiP-iT project [Website](http://dip-it.ovgu.de/).

The package implements Python functions for 
+ aggregating and preprocessing GitHub activities (Commits, Actions, Issues, Pull-Requests) and 
+ generating project progress summaries according to different metrics (ratio of changed lines, ratio of aggregated Levenshtein distances e.g.).

`github2pandas` stores the collected information in a collection of pandas DataFrames starting from a user defined root folder. The structure beyond that (file names, folder names) is defined as a member variable in the corresponding classes and can be overwritten. The default configuration results in the following file structure.

```
data                                     <- Root directory given as parameter
├── My_Github_Repository_0               <- Repository name
│   ├── Repo.json                        <- Json file containing user and repo name
│   ├── Issues
│   │   ├── pdIssuesComments.p
│   │   ├── pdIssuesEvents.p
│   │   ├── pdIssues.p
│   │   └── pdIssuesReactions.p
│   ├── PullRequests
│   │   ├── pdPullRequestsComments.p
│   │   ├── pdPullRequestsEvents.p
│   │   ├── pdPullRequests.p
│   │   ├── pdPullRequestsReactions.p
│   │   └── pdPullRequestsReviews.p
│   ├── Users.p
│   ├── Versions
│   │   ├── pdCommits.p
│   │   ├── pdEdits.p
│   │   ├── pdBranches.p
│   │   ├── repo                         <- Repository clone
│   │   │   ├── ..
│   │   └── Versions.db
│   └── Workflows
│       └── pdWorkflows.p
├── My_Github_Repository_1
...
```
The internal structure and relations of the data frames are included in the project's [wiki](https://github.com/TUBAF-IFI-DiPiT/github2pandas/wiki).

## Installation

Due to the early stage of development the `github2pandas` package is not yet available as a pip package. Installations should be done accordingly as follows:

1. Generate local clone of the package
    ```
    git clone https://github.com/TUBAF-IFI-DiPiT/github2pandas.git
    ```
2. Include the specific folder to your python path 
    ```
    pipenv install --dev
    ```

## Application examples 

GitHub token is required for use, which is used for authentication. The [website](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) describes how you can generate this for your GitHub account. Customise the username and project name and explore any public or private repository you have access to with your account!

| Aspect              | Example                                                                                                                        | Executable notebook | 
|:------------------- |:------------------------------------------------------------------------------------------------------------------------------ |:------------------- |
| Overview Example    | [Overview_Example.ipynb](https://github.com/TUBAF-IFI-DiPiT/github2pandas/blob/main/notebooks/Overview_Example.ipynb)          | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TUBAF-IFI-DiPiT/github2pandas/HEAD?filepath=%2Fnotebooks)  |
| Commits & Edits     | [Version_Example.ipynb](https://github.com/TUBAF-IFI-DiPiT/github2pandas/blob/main/notebooks/Version_Example.ipynb)            |                     |
| Workflows / Actions | [Workflow_Example.ipynb](https://github.com/TUBAF-IFI-DiPiT/github2pandas/blob/main/notebooks/Workflow_Example.ipynb)          |                     |
| Issues              | [Issue_Example.ipynb](https://github.com/TUBAF-IFI-DiPiT/github2pandas/blob/main/notebooks/Issues_Example.ipynb)               |                     |
| Pull-Requests       | [Pull_Requests_Example.ipynb](https://github.com/TUBAF-IFI-DiPiT/github2pandas/blob/main/notebooks/Pull_Requests_Example.ipynb)|                     | 

The documentation of the module is available at [https://github2pandas.readthedocs.io/](https://github2pandas.readthedocs.io/). 

# For Contributors

Naming conventions: https://namingconvention.org/python/

## Working with pipenv


| Process                                     | Command                                                 |
| ------------------------------------------- | ------------------------------------------------------- |
| Installation                                | `pipenv install --dev`                                  |
| Run specific script                         | `pipenv run python file.py`                             |
| Run all Tests                               | `pipenv run python -m unittest`                         |
| Run all tests in a specific folder          | `pipenv run python -m unittest discover -s 'tests'`     |
| Run all tests with specific filename        | `pipenv run python -m unittest discover -p 'test_*.py'` |
| Start Jupyter server in virtual environment | `pipenv run jupyter notebook`                           | 

## Generating documentation

1. Run following command in main folder

```
pipenv run  sphinx-apidoc -o ./docu/source/ ./github2pandas
```

2. Generate html documentation 

```
cd docu
make html
```
