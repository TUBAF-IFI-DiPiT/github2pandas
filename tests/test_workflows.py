import unittest
import os
from pathlib import Path
import warnings
import datetime
import shutil

from github2pandas.workflows import Workflows
from github2pandas.utility import Utility

class TestWorkflows(unittest.TestCase):
    """
    Test case for Workflows class.
    """
    
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"

    default_data_folder = Path("test_data", git_repo_name)
    repo = Utility.get_repo(git_repo_owner, git_repo_name, github_token, default_data_folder)

    def test_generate_workflow_pandas_tables(self):
        Workflows.generate_workflow_pandas_tables(self.repo, self.default_data_folder, check_for_updates=False)
        Workflows.generate_workflow_pandas_tables(self.repo, self.default_data_folder)
        
    def test_get_workflows(self):
        pd_workflows_file = Workflows.get_workflows(self.default_data_folder)
        pd_workflows_runs = Workflows.get_workflows(self.default_data_folder, Workflows.WORKFLOWS_RUNS)

    def test_download_workflow_log_files(self):
        self.skipTest("Skip Test Fr Workflow")
        for workflow_run in self.repo.get_workflow_runs():
            file_number = Workflows.download_workflow_log_files(self.repo,self.github_token, workflow_run.id, self.default_data_folder)
            self.assertIsNotNone(file_number)
            break
        file_number = Workflows.download_workflow_log_files(self.repo,self.github_token, -1, self.default_data_folder)
        self.assertIsNone(file_number)
    
    def test_extract_workflow_data(self):
        class Workflow:
            id = 0
            name = "test_extract_workflow_data"
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            state = "test_extract_workflow_data"
        worflow_data = Workflows.extract_workflow_data(Workflow())
        self.assertIsNotNone(worflow_data)

    def test_extract_workflow_run_data(self):
        class WorkflowRun:
            workflow_id = 0
            id = 0
            head_sha = "test_extract_workflow_data"
            pull_requests = []
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            status = "test_extract_workflow_data"
            event = "test_extract_workflow_data"
            conclusion = "test_extract_workflow_data"
        worflow_run_data = Workflows.extract_workflow_run_data(WorkflowRun())
        self.assertIsNotNone(worflow_run_data)

    def setUp(self):
        self.default_data_folder.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("test_data")

if "__main__" == __name__:
    unittest.main()