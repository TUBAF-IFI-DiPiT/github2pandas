import requests
import zipfile
import io
import pandas as pd
from pathlib import Path
import pickle

from .. import utility

class AggWorkflow(object):
    WORKFLOW = "pdWorkflows.p"
    WORKFLOW_DIR = "Workflows"

    @staticmethod
    def generate_workflow_history(repo_name, github_token, data_dir, 
                                  workflow_folder = None,
                                  workflow_filename = None):
        if not workflow_folder:
            workflow_folder = AggWorkflow.WORKFLOW_DIR
        if not workflow_filename:
            workflow_filename = AggWorkflow.WORKFLOW

        valid = False
        repo = utility.get_repo(repo_name, github_token)
        if repo:
            workflow_data = []
            workflow_runs = repo.get_workflow_runs()
            sample = {}
            for index, run in enumerate(workflow_runs):
                sample['workflow_run_id'] = run.id
                workflow = repo.get_workflow(str(run.workflow_id))
                sample['workflow_id'] = workflow.id
                sample['workflow_name'] = workflow.name
                sample['commit_message'] = run.head_commit.message
                sample['commit_author'] = run.head_commit.author.name
                sample['commit_sha'] = run.head_sha
                sample['commit_branch'] = run.head_branch
                sample['state'] = run.status
                sample['conclusion'] = run.conclusion
                workflow_data.append(sample.copy())
            pd_wfh = pd.DataFrame(workflow_data)
            if not pd_wfh.empty:
                Path(data_dir, workflow_folder).mkdir(parents=True, exist_ok=True)
                pd_wfh_file = Path(data_dir, workflow_folder).joinpath(workflow_filename)
                with open(pd_wfh_file, "wb") as f:
                    pickle.dump(pd_wfh, f)
                valid = True
        return valid


    @staticmethod
    def request_log_files(owner, repo_name, github_token, workflow_id, data_dir,
                          workflow_folder = None):
        if not workflow_folder:
            workflow_folder = AggWorkflow.WORKFLOW_DIR
        # Motivated from https://curl.trillworks.com/
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        query_url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/runs/{workflow_id}/logs"
        response = requests.get(query_url, headers=headers,
                                auth=('username', github_token))
        print(query_url)
        print(response.headers['Content-Type'])
        if 'zip' in response.headers['Content-Type']:
            zipObj = zipfile.ZipFile(io.BytesIO(response.content))
            data_dir_ = Path(data_dir, workflow_folder, workflow_id)
            zipObj.extractall(data_dir_)
            return len(zipObj.namelist())
        else:
            return None

    @staticmethod
    def get_workflow_pandas_table(data_dir, 
                                  workflow_folder = None,
                                  workflow_filename = None):
        if not workflow_folder:
            workflow_folder = AggWorkflow.WORKFLOW_DIR
        if not workflow_filename:
            workflow_filename = AggWorkflow.WORKFLOW
        pd_wfh_file = Path(data_dir, workflow_folder).joinpath(workflow_filename)
        if pd_wfh_file.is_file():
            return pd.read_pickle(pd_wfh_file)
        else: 
            return None