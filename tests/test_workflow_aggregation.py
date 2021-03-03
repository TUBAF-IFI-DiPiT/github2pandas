#!/usr/bin/python
 
import unittest
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflows.aggregation import generateWorkflowHistory

class Test_Workflow(unittest.TestCase):

    git_repo_name = "xAPI_for_GitHubData"
    default_data_folder = Path("data", git_repo_name)

    def test_workflow_aggregation_public_repository(self):
        """
        Test workflow aggregation
        """
        github_token = os.environ['TOKEN']

        result = generateWorkflowHistory(repo_name=self.git_repo_name,
                                         github_token=github_token,
                                         data_dir=self.default_data_folder)
        self.assertTrue( result, "Workflow generation throws exception")

if "__main__" == __name__:
    unittest.main()