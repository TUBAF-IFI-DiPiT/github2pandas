import logging
import requests
from zipfile import ZipFile
from io import BytesIO
from pathlib import Path
from types import NoneType
from typing import Union
from pandas import DataFrame
import pandas as pd
# github imports
from github.MainClass import Github
from github.Repository import Repository as GitHubRepository
from github.Workflow import Workflow as GitHubWorkflow
from github.WorkflowRun import WorkflowRun as GitHubWorkflowRun
# github2pandas imports
from github2pandas.core import Core

class Workflows(Core):
    """
    Class to aggregate Workflows

    Attributes
    ----------
    DATA_DIR : str
        workflow dir where all files are saved in.
    WORKFLOWS : str
        Pandas table file for workflow data.
    WORKFLOWS_RUNS : str
        Pandas table file for run data.
    EXTRACTION_PARAMS : dict
        Holds all extraction parameters with a default setting.
    FILES : dict
        Mappings from data directories to pandas table files.    
    workflows_df : DataFrame
        Pandas DataFrame object with workflows data.
    runs_df : DataFrame
        Pandas DataFrame object with runs data.

    Methods
    -------
    __init__(self, github_connection, repo, data_root_dir, request_maximum)
        Initializes workflows object with general information.
    generate_pandas_tables(self, check_for_updates=False, extraction_params={})
        Extracts the complete workflow list and run history from a repository.
    __extract_workflow_data(workflow)
        Extracts general data of one workflow.
    __extract_run_data(workflow_run)
        Extracts general data of workflow run.
    download_workflow_log_files(repo, github_token, workflow_run_id, data_root_dir)
        Receives workflow log files from GitHub.
    
    """

    DATA_DIR = "Workflows"
    WORKFLOWS = "Workflows.p"
    RUNS =  "Runs.p"
    FILES = [
        WORKFLOWS,
        RUNS
    ]
    EXTRACTION_PARAMS = {
        "workflows": True,
        "runs": True
    }

    def __init__(self, github_connection:Github, repo:GitHubRepository, data_root_dir:Path, request_maximum:int = 40000, log_level:int=logging.INFO) -> NoneType:
        """
        __init__(self, github_connection, repo, data_root_dir, request_maximum, log_level)

        Initializes Workflows object with general information.

        Parameters
        ----------
        github_connection : Github
            Github object from pygithub.
        repo : GitHubRepository
            Repository object from pygithub.
        data_root_dir : Path
            Data root directory for the repository.
        request_maximum : int, default=40000
            Maximum amount of returned informations for a general api call.
        log_level : int
            Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET), default value is enumaration value logging.INFO    


        Notes
        -----
            PyGithub Github object structure: https://pygithub.readthedocs.io/en/latest/github.html
            PyGithub Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        Core.__init__(
            self,
            github_connection,
            repo,
            data_root_dir,
            Workflows.DATA_DIR,
            request_maximum=request_maximum,
            log_level=log_level
        )

    @property
    def workflows_df(self):
        return Core.get_pandas_data_frame(self.current_dir, Workflows.WORKFLOWS)
    @property
    def runs_df(self):
        return Core.get_pandas_data_frame(self.current_dir, Workflows.RUNS)

    def generate_pandas_tables(self, check_for_updates:bool = False, extraction_params:dict = {}) -> NoneType:
        """
        generate_pandas_tables(check_for_updates=False, extraction_params={})

        Extracts the complete workflows from a repository.
        Checks first if there are any new workflows information in dependence of parameter check_for_updates.

        Parameters
        ----------
        check_for_updates : bool, default=True
            Checks first if there are any new workflows information. Does not work when extract_reaction is True.
        extraction_params : dict, default={}
            Can hold extraction parameters. This defines what will be extracted.
            
        """
        params = self.copy_valid_params(self.EXTRACTION_PARAMS,extraction_params)
        if params["workflows"]:
            workflows = self.save_api_call(self.repo.get_workflows)
            total_count = self.get_save_total_count(workflows)
            extract = True
            if check_for_updates:
                if not self.check_for_updates_paginated(workflows, total_count, self.workflows_df):
                    self.logger.info("No new workflow information!")
                    extract = False
            if extract:
                workflow_list = []
                for i in self.progress_bar(range(total_count), "Workflows: "):
                    workflow = self.get_save_api_data(workflows, i)
                    workflow_data = self.__extract_workflow_data(workflow)
                    workflow_list.append(workflow_data)
                workflows_df = DataFrame(workflow_list)
                self.save_pandas_data_frame(Workflows.WORKFLOWS, workflows_df)
        if params["runs"]:
            runs = self.save_api_call(self.repo.get_workflow_runs)
            total_count = self.get_save_total_count(runs)
            extract = True
            if check_for_updates:
                if not self.check_for_updates_paginated(runs, total_count, self.runs_df):
                    self.logger.info("No new workflow run information!")
                    extract = False
            if extract:
                run_list = []
                for i in self.progress_bar(range(total_count), "Workflow Runs: "):
                    run = self.get_save_api_data(runs, i)
                    run_data = self.__extract_run_data(run)
                    run_list.append(run_data)
                runs_df = DataFrame(run_list)
                self.save_pandas_data_frame(Workflows.RUNS, runs_df)

    def __extract_workflow_data(self, workflow:GitHubWorkflow) -> dict:
        """
        __extract_workflow_data(workflow)

        Extracts general data of one workflow.

        Parameters
        ----------
        workflow : GitHubWorkflow
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
    
    def __extract_run_data(self, run:GitHubWorkflowRun) -> dict:
        """
        __extract_run_data(run)

        Extracts general data of one workflow run.

        Parameters
        ----------
        run : GitHubWorkflowRun
            WorkflowRun object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            PyGithub WorkflowRun object structure: https://pygithub.readthedocs.io/en/latest/github_objects/WorkflowRun.html

        """
        run_data = {}
        run_data["workflow_id"] = run.workflow_id
        run_data['id'] = run.id
        run_data['commit_sha'] = run.head_sha
        run_data['pull_requests'] = [pr.id for pr in run.pull_requests]
        run_data['state'] = run.status
        run_data['event'] = run.event
        run_data['conclusion'] = run.conclusion
        run_data['created_at'] = run.created_at
        run_data['updated_at'] = run.updated_at
        return run_data

    @staticmethod
    def download_workflow_log_files(repo, github_token, workflow_run_id, data_root_dir) -> Union[int, None]:
        """
        download_workflow_log_files(repo, github_token, workflow_run_id, data_root_dir)

        Receives workflow log files from GitHub.

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
        Union[int, None]
            Returns the number of downloaded files or the value None.

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
            zip_obj = ZipFile(BytesIO(response.content))
            data_dir = Path(data_root_dir, Workflows.DATA_DIR, str(workflow_run_id))
            zip_obj.extractall(data_dir)
            return len(zip_obj.namelist())
        else:
            return None
