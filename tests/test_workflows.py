import logging
import unittest
import os
from pathlib import Path
import datetime
import shutil
# github2pandas imports
from github2pandas.core import Core
from github2pandas.github2pandas import GitHub2Pandas
from github2pandas.workflows import Workflows

class TestWorkflows(unittest.TestCase):
    """
    Test case for Workflows class.
    """
    github_token = os.environ['TOKEN']
    git_repo_name = "github2pandas"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    data_root_dir = Path("test_data")
    log_level = logging.DEBUG

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        if self.data_root_dir.exists() and self.data_root_dir.is_dir():
            shutil.rmtree(self.data_root_dir, onerror=Core._file_error_handling)
        self.data_root_dir.mkdir(parents=True, exist_ok=True)

    def test_generate_pandas_tables(self):
        github2pandas = GitHub2Pandas(self.github_token,self.data_root_dir, log_level=self.log_level)
        repo = github2pandas.get_repo(self.git_repo_owner, self.git_repo_name)

        workflows = Workflows(github2pandas.github_connection, repo, self.data_root_dir, log_level=self.log_level)
        workflows.print_calls("Start workflows")
        workflows.generate_pandas_tables()
        workflows.print_calls("End workflows")
        
    def test_get_data_frames(self):
        data_dir = Path(self.data_root_dir,self.git_repo_owner,self.git_repo_name,Workflows.Files.DATA_DIR)
        workflows = Core.get_pandas_data_frame(data_dir, Workflows.Files.WORKFLOWS)
        runs = Core.get_pandas_data_frame(data_dir, Workflows.Files.RUNS)
        pass

    # def test_download_workflow_log_files(self):
    #     self.skipTest("Skip Test Fr Workflow")
    #     for workflow_run in self.repo.get_workflow_runs():
    #         file_number = Workflows.download_workflow_log_files(self.repo,self.github_token, workflow_run.id, self.default_data_folder)
    #         self.assertIsNotNone(file_number)
    #         break
    #     file_number = Workflows.download_workflow_log_files(self.repo,self.github_token, -1, self.default_data_folder)
    #     self.assertIsNone(file_number)
    
    # def test_extract_workflow_data(self):
    #     class Workflow:
    #         id = 0
    #         name = "test_extract_workflow_data"
    #         created_at = datetime.datetime.now()
    #         updated_at = datetime.datetime.now()
    #         state = "test_extract_workflow_data"
    #     workflows = Workflows(self.github_connection, self.repo, self.default_data_folder)
    #     worflow_data = workflows.extract_workflow_data(Workflow())
    #     self.assertIsNotNone(worflow_data)

    # def test_extract_workflow_run_data(self):
    #     class WorkflowRun:
    #         workflow_id = 0
    #         id = 0
    #         head_sha = "test_extract_workflow_data"
    #         pull_requests = []
    #         created_at = datetime.datetime.now()
    #         updated_at = datetime.datetime.now()
    #         status = "test_extract_workflow_data"
    #         event = "test_extract_workflow_data"
    #         conclusion = "test_extract_workflow_data"
    #     workflows = Workflows(self.github_connection, self.repo, self.default_data_folder)
    #     worflow_run_data = workflows.extract_run_data(WorkflowRun())
    #     self.assertIsNotNone(worflow_run_data)

if "__main__" == __name__:
    unittest.main()