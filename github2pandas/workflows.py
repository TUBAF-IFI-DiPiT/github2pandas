import requests
import zipfile
import io
import pandas as pd
from pathlib import Path
from .utility import Utility

class Workflows(object):
    """
    Class to aggregate Pull Requests

    Attributes
    ----------
    WORKFLOW_DIR : str
        workflow dir where all files are saved in.
    WORKFLOW : str
        Pandas table file for workflow data.
    RUNS : str
        Pandas table file for run data.

    Methods
    -------
    extract_workflow_data(workflow, run, data_root_dir, check_for_updates=True)
        Extracting workflow data from run 
    generate_workflow_pandas_tables(repo, data_root_dir)
        Extracting the complete workflow data set from a repository
    download_workflow_log_files(owner, repo_name, github_token, workflow_id, data_root_dir)
        Provide workflow logs as download
    get_raw_workflow(data_root_dir)
        Get the generated pandas table.
    get_raw_run(data_root_dir)
        Get the generated pandas table.
    """

    WORKFLOW = "pdWorkflows.p"
    RUNS =  "pdRuns.p"
    WORKFLOW_DIR = "Workflows"


    @staticmethod
    def extract_run_data(run):
        """
        extract_run_data(run):

        Extracting general run data.

        Parameters
        ----------
        workflow_run: int
            Run object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            PullRequestReview object structure: https://pygithub.readthedocs.io/en/latest/github_objects/WorkflowRun.html

        """
        run_data = dict()
        run_data["workflow_id"] = run.workflow_id
        run_data['id'] = run.id
        run_data['commit_sha'] = run.head_sha
        run_data['pull_requests'] = [pr.id for pr in run.pull_requests]
        run_data['state'] = run.status
        run_data['event'] = run.event
        run_data['conclusion'] = run.conclusion
        run_data['commit_sha'] = run.head_sha
        run_data['created_at'] = run.created_at
        run_data['updated_at'] = run.updated_at
        return run_data

    @staticmethod
    def extract_workflow_data(workflow):
        """
        extract_workflow_data(workflow, repo_dir):

        Extracting general workflow data.

        Parameters
        ----------
        workflow: Workflow
            Workflow object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
           PullRequestReview object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Workflow.html

        """
        workflow_data = {}
        workflow_data["id"] = workflow.id
        workflow_data['name'] = workflow.name
        workflow_data['created_at'] = workflow.created_at
        workflow_data['updated_at'] = workflow.updated_at
        workflow_data["state"] = workflow.state
        return workflow_data

    @staticmethod
    def generate_workflow_pandas_tables(repo, data_root_dir, check_for_updates=True):
        """
        def generate_workflow_pandas_tables(repo, data_root_dir, check_for_updates=True)

        Extracting the complete workflow list and run history from a repository

        Parameters
        ----------
        data_root_dir: str
            Repo dir of the project.
        repo: Repository
            Repository object from pygithub.
        check_for_updates: bool, default=True
            Check first if there are any new pull requests.

        Returns
        -------
        bool
            Code runs without errors 
        """
        workflow_dir = Path(data_root_dir, Workflows.WORKFLOW_DIR)
        workflow_dir.mkdir(parents=True, exist_ok=True)
        users_ids = Utility.get_users_ids(data_root_dir)

        workflows = repo.get_workflows()
        workflow_runs = repo.get_workflow_runs()

        if check_for_updates:
            old_workflows = Workflows.get_workflows(data_root_dir)
            check_workflows = Utility.check_for_updates_paginated(workflows, old_workflows)
            old_workflow_runs = Workflows.get_workflows(data_root_dir,Workflows.RUNS)
            check_workflow_runs = Utility.check_for_updates_paginated(workflow_runs, old_workflow_runs)
            if not check_workflows and not check_workflow_runs:
                return
        workflow_list = []
        for workflow in workflows:
            workflow_sample = Workflows.extract_workflow_data(workflow)
            workflow_list.append(workflow_sample)
        Utility.save_list_to_pandas_table(workflow_dir, Workflows.WORKFLOW, workflow_list)

        run_list = []
        for run in workflow_runs:
            run_sample = Workflows.extract_run_data(run)
            run_sample['author'] = Utility.extract_committer_data_from_commit(repo, run_sample['commit_sha'], users_ids, data_root_dir)
            run_list.append(run_sample)
        Utility.save_list_to_pandas_table(workflow_dir, Workflows.RUNS, run_list)
        return True

    @staticmethod
    def download_workflow_log_files(repo, github_token, run, data_root_dir):
        """
        download_workflow_log_files(repo, workflow_id, data_root_dir)

        Receive workflow log files from GitHub

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.       
        github_token: str
            Authentication token for GitHub access
        run: Run
            Run object from pygithub.  
        data_dir: str
            Path to the data folder of the repository.

        Returns
        -------
        length: int
            Number of downloaded files

        Notes
        -------
            Download api https://docs.github.com/en/rest/reference/actions#list-jobs-for-a-workflow-run
            Generation of python code based on https://curl.trillworks.com/
        """
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        query_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/actions/runs/{run.id}/logs"
        response = requests.get(query_url, headers=headers,
                                auth=('username', github_token))
        print(query_url)
        if 'zip' in response.headers['Content-Type']:
            zipObj = zipfile.ZipFile(io.BytesIO(response.content))
            data_dir_ = Path(data_root_dir, Workflows.WORKFLOW_DIR, str(run.id))
            zipObj.extractall(data_dir_)
            return len(zipObj.namelist())
        else:
            return None


    @staticmethod
    def get_workflows(data_root_dir, filename=WORKFLOW):
        """
        get_workflow(data_root_dir, filename=WORKFLOWS)

        Get a generated pandas tables.

        Parameters
        ----------
        data_root_dir: str
            Data root directory for the repository.
        filename: str, default=WORKFLOWS
            Pandas table file for workflows or run data.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can include the desired data

        """
        workflow_dir = Path(data_root_dir, Workflows.WORKFLOW_DIR)
        pd_workflows_file = Path(workflow_dir, filename)
        if pd_workflows_file.is_file():
            return pd.read_pickle(pd_workflows_file)
        else:
            return pd.DataFrame()
