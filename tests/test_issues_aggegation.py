import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utility import clone_repository, generate_data_base, get_repo
from src.issues.aggregation import generate_pandas_tables

if __name__ == "__main__":
    
    # For fast local testing. Can be removed when module is done.
    github_token = os.environ['TOKEN']

    git_repo_name = "Extract_Git_Activities"
    git_repo_owner = "TUBAF-IFI-DiPiT"
    
    if not os.path.exists('repos'):
        os.makedirs('repos')
    default_repo_folder = os.path.join("repos", git_repo_name)
    if not os.path.exists('data'):
        os.makedirs('data')
    default_data_folder = Path("data", git_repo_name)


    
    repo = get_repo(repo_name=git_repo_name, token=github_token)
    generate_pandas_tables(data_dir=default_data_folder,
                       git_repo_name=git_repo_name, repo=repo)

    #result = get_commit_raw_pandas_table(default_data_folder)

    #print(result.columns)
