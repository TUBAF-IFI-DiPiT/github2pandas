# Extract GitHub Activities

This package is being developed by the participating partners (TU Bergakademie Freiberg, OVGU Magdeburg and HU Berlin) as part of the DiP-iT project.
The package implements Python functions for aggregation and preprocessing of GitHub activities. These are structured in files as follows.


| Aspect              | Example                                                                                                                        | Executable notebook | Documentation | 
|:------------------- |:------------------------------------------------------------------------------------------------------------------------------ |:------------------- | ------------- |
| Commits & Edits     |                                                                                                                                |                     |               |
| Workflows / Actions | [Commits_aggregation.py](https://github.com/TUBAF-IFI-DiPiT/Extract_Git_Activities/blob/main/notebooks/Workflow_Example.ipynb) | [CoLab](invalid)    |               |
| Issues              |                                                                                                                                |                     |               |
| Discussions         |                                                                                                                                |                     |               |

Due to the early stage of development the DiP-iT package is not yet available as a pip package. Installations should be done accordingly as follows:

1. Generate local clone of the package
    ```
    git clone https://github.com/TUBAF-IFI-DiPiT/Extract_Git_Activities.git
    ```
2. Include the specific folder to your python path 
    ```
    pipenv install --dev
    ```

# For Developer

Naming conventions: https://namingconvention.org/python/

## Working with pipenv


| Process                                     | Command                                                 |
| ------------------------------------------- | ------------------------------------------------------- |
| Installation                                | `pipenv install --dev`                                  |
| Run specific script                         | `pipenv run python file.py`                             |
| Run all Tests                               | `pipenv run python -m unittest`                         |
| Run all tests in a specific folder          | `pipenv run python -m unittest discover -s 'tests'`      |
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
## Data aggregation structur

- Extract_Git_Activities
   - Issues
      - pdIssues.p
      - pdIssuesComments.p
      - pdIssuesEvents.p
      - pdIssuesReactions.p
   - PullRequests
      - pdPullRequests.p
      - pdPullRequestsComments.p
      - pdPullRequestsEvents.p
      - pdPullRequestsReactions.p
      - pdPullRequestsReviews.p
   - Users.p
   - Versions
      - pdCommits.p
      - pdEdits.p
      - repo
         - left out ...
      - Versions.db
   - Workflows
      - pdWorkflows.p