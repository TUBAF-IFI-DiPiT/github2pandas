#!/usr/bin/python
 
import unittest
import os
from pathlib import Path

from github2pandas.workflows.aggregation import AggWorkflow as AggWF
from github2pandas.utility import Utility

class Test_Workflow(unittest.TestCase):

    git_repo_name = "xAPI_for_GitHubData"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    default_data_folder = Path("data", git_repo_name)
    github_token = os.environ['TOKEN']

    def test_workflow_aggregation_public_repository(self):
        """
        Test workflow aggregation
        """
        repo = Utility.get_repo(self.git_repo_owner, self.git_repo_name, self.github_token)
        AggWF.generate_workflow_pandas_tables(repo=repo, data_root_dir=self.default_data_folder)
        pd_workflow = AggWF.get_raw_workflow(data_root_dir=self.default_data_folder)
        self.assertTrue( not pd_workflow.empty, "Pandas edits data frame empty")

if "__main__" == __name__:
    unittest.main()