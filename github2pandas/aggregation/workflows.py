import requests
import zipfile
import io
import pandas as pd
from pathlib import Path
from .utility import Utility

class AggWorkflow(object):
    """
    Class to aggregate Pull Requests

    Attributes
    ----------
    WORKFLOW_DIR : str
        workflow dir where all files are saved in.
    WORKFLOW : str
        Pandas table file for workflow data.

    Methods
    -------
    extract_workflow_data(workflow, run, data_root_dir)
        Extracting workflow data from run 
    generate_workflow_pandas_tables(repo, data_root_dir)
        Extracting the complete workflow data set from a repository
    download_workflow_log_files(owner, repo_name, github_token, workflow_id, data_root_dir)
        Provide workflow logs as download
    get_raw_workflow(data_root_dir)
        Get the generated pandas table.
    """

    WORKFLOW = "pdWorkflows.p"
    WORKFLOW_DIR = "Workflows"

    @staticmethod
    def extract_workflow_data(workflow, run):
        """
        extract_workflow_data(workflow, repo_dir):

        Extracting general workflow data.

        Parameters
        ----------
        workflow: Workflow
            Workflow object from pygithub.
        workflow_run: int
            Run object from pygithub.

        Returns
        -------
        dict
            Dictionary with the extracted data.

        Notes
        -----
            PullRequestReview object structure: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequestReview.html

        """
        workflow_data = dict()
        workflow_data["workflow_id"] = workflow.id
        workflow_data['workflow_name'] = workflow.name
        workflow_data['workflow_run_id'] = run.id
        workflow_data['commit_message'] = run.head_commit.message
        workflow_data['commit_author'] = run.head_commit.author.name
        workflow_data['commit_sha'] = run.head_sha
        workflow_data['commit_branch'] = run.head_branch
        workflow_data['state'] = run.status
        workflow_data['conclusion'] = run.conclusion
        return workflow_data

    @staticmethod
    def generate_workflow_pandas_tables(repo, data_root_dir):
        """
        def generate_workflow_pandas_tables(repo, data_root_dir)

        Extracting the complete workflow history from a repository

        Parameters
        ----------
        data_root_dir: str
            Repo dir of the project.
        repo: Repository
            Repository object from pygithub.

        Returns
        -------
        bool
            Code runs without errors 
        
        Notes
        -----
            Repository object structure: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html

        """
        workflow_dir = Path(data_root_dir, AggWorkflow.WORKFLOW_DIR)
        workflow_list = list()
        workflow_runs = repo.get_workflow_runs()
        for index, run in enumerate(workflow_runs):
            workflow = repo.get_workflow(str(run.workflow_id))
            workflow_sample = AggWorkflow.extract_workflow_data(workflow, run)
            workflow_sample['author'] = Utility.extract_committer_data_from_commit(repo, workflow_sample['commit_sha'], data_root_dir)
            workflow_list.append(workflow_sample)
  
        workflow_dir = Path(data_root_dir, AggWorkflow.WORKFLOW_DIR)
        workflow_dir.mkdir(parents=True, exist_ok=True)
        Utility.save_list_to_pandas_table(workflow_dir, AggWorkflow.WORKFLOW, workflow_list)
        return True

    @staticmethod
    def download_workflow_log_files(repo, github_token, workflow, data_root_dir):
        """
        download_workflow_log_files(repo, workflow_id, data_root_dir)

        Receive workflow log files from GitHub

        Parameters
        ----------
        repo: Repository
            Repository object from pygithub.       
        github_token: str
            Authentication token for GitHub access
        workflow: Workflow
            Workflow object from pygithub.  
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
        query_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/actions/runs/{workflow.id}/logs"
        response = requests.get(query_url, headers=headers,
                                auth=('username', github_token))
        print(query_url)
        if 'zip' in response.headers['Content-Type']:
            zipObj = zipfile.ZipFile(io.BytesIO(response.content))
            data_dir_ = Path(data_root_dir, AggWorkflow.WORKFLOW_DIR, str(workflow.id))
            zipObj.extractall(data_dir_)
            return len(zipObj.namelist())
        else:
            return None

    @staticmethod
    def get_raw_workflow(data_root_dir):
        """
        get_raw_workflow(repo_dir)

        Get the generated pandas table.

        Parameters
        ----------
        data_dir: str
            Path to the data folder of the repository.

        Returns
        -------
        DataFrame
            Pandas DataFrame which includes the workflow data
        """
        pd_wfh_file = Path(data_root_dir, AggWorkflow.WORKFLOW_DIR).joinpath(AggWorkflow.WORKFLOW)
        if pd_wfh_file.is_file():
            return pd.read_pickle(pd_wfh_file)
        else: 
            return pd.DataFrame()