#!/usr/bin/python
 
import unittest
import os
import sys
from pathlib import Path

from github2pandas.workflows.aggregation import generate_workflow_history,\
                                      get_workflow_pandas_table

class Test_Workflow(unittest.TestCase):

    git_repo_name = "xAPI_for_GitHubData"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    default_data_folder = Path("data", git_repo_name)

    def test_workflow_aggregation_public_repository(self):
        """
        Test workflow aggregation
        """
        github_token = os.environ['TOKEN']

        result = generate_workflow_history(repo_name=self.git_repo_name,
                                           github_token=github_token,
                                           data_dir=self.default_data_folder)
        self.assertTrue( result, "Workflow generation throws exception")

    def test_workflow_result_download(self):
        """
        Test access on pandas file
        """
        pdWorkflow = get_workflow_pandas_table(data_dir=self.default_data_folder)
        self.assertTrue( not pdWorkflow.empty, "Pandas edits data frame empty")


if "__main__" == __name__:
    unittest.main()