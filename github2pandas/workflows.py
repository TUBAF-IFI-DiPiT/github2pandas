import requests
import zipfile
import io
import pandas as pd
from pathlib import Path
from .utility import Utility

class Workflows(object):
    """
    Class to aggregate Workflows

    Attributes
    ----------
    WORKFLOWS_DIR : str
        workflow dir where all files are saved in.
    WORKFLOWS : str
        Pandas table file for workflow data.
    WORKFLOWS_RUNS : str
        Pandas table file for run data.

    Methods
    -------
    extract_workflow_data(workflow)
        Extracting general workflow data.
    extract_workflow_run_data(workflow_run)
        Extracting general workflow run data.
    generate_workflow_pandas_tables(repo, data_root_dir, check_for_updates=True)
        Extracting the complete workflow list and run history from a repository.
    download_workflow_log_files(repo, github_token, workflow_run_id, data_root_dir)
        Receive workflow log files from GitHub.
    get_workflows(data_root_dir, filename=WORKFLOWS)
        Get a generated pandas tables.
    
    """

    WORKFLOWS_DIR = "Workflows"
    WORKFLOWS = "pdWorkflows.p"
    WORKFLOWS_RUNS =  "pdWorkflowsRuns.p"

    @staticmethod
    def extract_workflow_data(workflow):
        """
        extract_workflow_data(workflow)

        Extracting general workflow data.

        Parameters
        ----------
        workflow : Workflow
            Workflow object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
           PyGithub Workflow object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Workflow.html

        """
        workflow_data = {}
        workflow_data["id"] = workflow.id
        workflow_data['name'] = workflow.name
        workflow_data['created_at'] = workflow.created_at
        workflow_data['updated_at'] = workflow.updated_at
        workflow_data["state"] = workflow.state
        return workflow_data
    
    @staticmethod
    def extract_workflow_run_data(workflow_run):
        """
        extract_workflow_run_data(workflow_run)

        Extracting general workflow run data.

        Parameters
        ----------
        workflow_run : WorkflowRun
            WorkflowRun object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            PyGithub WorkflowRun object structure: https://pygithub.readthedocs.io/en/latest/github_objects/WorkflowRun.html

        """
        workflow_run_data = dict()
        workflow_run_data["workflow_id"] = workflow_run.workflow_id
        workflow_run_data['id'] = workflow_run.id
        workflow_run_data['commit_sha'] = workflow_run.head_sha
        workflow_run_data['pull_requests'] = [pr.id for pr in workflow_run.pull_requests]
        workflow_run_data['state'] = workflow_run.status
        workflow_run_data['event'] = workflow_run.event
        workflow_run_data['conclusion'] = workflow_run.conclusion
        workflow_run_data['created_at'] = workflow_run.created_at
        workflow_run_data['updated_at'] = workflow_run.updated_at
        return workflow_run_data

    @staticmethod
    def generate_workflow_pandas_tables(repo, data_root_dir, check_for_updates=True):
        """
        generate_workflow_pandas_tables(repo, data_root_dir, check_for_updates=True)

        Extracting the complete workflow list and run history from a repository.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.
        data_root_dir : str
            Data root directory for the repository.
        check_for_updates : bool, default=True
            Check first if there are any new workflows or workflow_runs information.
            
        Notes
        -----
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html
        
        """

        workflow_dir = Path(data_root_dir, Workflows.WORKFLOWS_DIR)
        workflow_dir.mkdir(parents=True, exist_ok=True)
        users_ids = Utility.get_users_ids(data_root_dir)

        workflows = repo.get_workflows()
        workflow_runs = repo.get_workflow_runs()

        if check_for_updates:
            old_workflows = Workflows.get_workflows(data_root_dir)
            check_workflows = Utility.check_for_updates_paginated(workflows, old_workflows)
            old_workflow_runs = Workflows.get_workflows(data_root_dir,Workflows.WORKFLOWS_RUNS)
            check_workflow_runs = Utility.check_for_updates_paginated(workflow_runs, old_workflow_runs)
            if not check_workflows and not check_workflow_runs:
                return
        
        workflow_list = []
        for workflow in workflows:
            workflow_data = Workflows.extract_workflow_data(workflow)
            workflow_list.append(workflow_data)
        Utility.save_list_to_pandas_table(workflow_dir, Workflows.WORKFLOWS, workflow_list)

        workflow_run_list = []
        for workflow_run in workflow_runs:
            workflow_run_data = Workflows.extract_workflow_run_data(workflow_run)
            workflow_run_data['author'] = Utility.extract_committer_data_from_commit(repo, workflow_run_data['commit_sha'], users_ids, data_root_dir)
            workflow_run_list.append(workflow_run_data)
        Utility.save_list_to_pandas_table(workflow_dir, Workflows.WORKFLOWS_RUNS, workflow_run_list)

    @staticmethod
    def download_workflow_log_files(repo, github_token, workflow_run_id, data_root_dir):
        """
        download_workflow_log_files(repo, github_token, workflow_run_id, data_root_dir)

        Receive workflow log files from GitHub.

        Parameters
        ----------
        repo : Repository
            Repository object from pygithub.       
        github_token : str
            Authentication token for GitHub access.
        workflow_run_id : int
            Workflow Run Id to download one specific workflow run.  
        data_root_dir : str
            Data root directory for the repository.

        Returns
        -------
        int
            Number of downloaded files.

        Notes
        -------
            Download api https://docs.github.com/en/rest/reference/actions#list-jobs-for-a-workflow-run
            Generation of python code based on https://curl.trillworks.com/
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html
            PyGithub WorkflowRun object structure: https://pygithub.readthedocs.io/en/latest/github_objects/WorkflowRun.html

        """
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        query_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/actions/runs/{workflow_run_id}/logs"
        response = requests.get(query_url, headers=headers,
                                auth=('username', github_token))
        if 'zip' in response.headers['Content-Type']:
            zip_obj = zipfile.ZipFile(io.BytesIO(response.content))
            data_dir = Path(data_root_dir, Workflows.WORKFLOWS_DIR, str(workflow_run_id))
            zip_obj.extractall(data_dir)
            return len(zip_obj.namelist())
        else:
            return None

    @staticmethod
    def get_workflows(data_root_dir, filename=WORKFLOWS):
        """
        get_workflows(data_root_dir, filename=WORKFLOWS)

        Get a generated pandas tables.

        Parameters
        ----------
        data_root_dir : str
            Data root directory for the repository.
        filename : str, default=WORKFLOWS
            Pandas table file for workflows or workflows runs data.

        Returns
        -------
        DataFrame
            Pandas DataFrame which can include the desired data.

        """
        workflow_dir = Path(data_root_dir, Workflows.WORKFLOWS_DIR)
        pd_workflows_file = Path(workflow_dir, filename)
        if pd_workflows_file.is_file():
            return pd.read_pickle(pd_workflows_file)
        else:
            return pd.DataFrame()
