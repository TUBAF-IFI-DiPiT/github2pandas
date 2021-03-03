import yaml
import pygit2 as git2
import github
import subprocess
import requests
import zipfile
import io
import pandas as pd
from pathlib import Path
import pickle

def generateWorkflowHistory(owner, repo, github_token, data_dir):
    g = github.Github(github_token)
    repo_ref = f"{owner}/{repo}"

    repo = None
    try:
        repo = g.get_repo(repo_ref)
    except:
        print("No repo of named {} found".format(repo_ref))

    workflow_data = []
    if repo:
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

    pd_wfh_file = Path(data_dir, "pdWorkflows" + ".p")
    pickle.dump(pd_wfh, open(pd_wfh_file, "wb"))


def requestLogFiles(owner, repo, github_token, workflow_id, folder='temp'):
    # Motivated from https://curl.trillworks.com/
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    query_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{workflow_id}/logs"
    response = requests.get(query_url, headers=headers,
                            auth=('username', github_token))
    print(response.headers['Content-Type'])
    if 'zip' in response.headers['Content-Type']:
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(f"{folder}/{repo}/{workflow_id}")
        return 1
    else:
        return -1


def getWorkflowPandasTable(data_dir):

    pd_wfh_file = Path(data_dir, "pdWorkflows" + ".p")
    return pd.read_pickle(pd_wfh_file)



if __name__ == "__main__":

    with open("./../secret.yml", "r") as ymlfile:
        sct = yaml.load(ymlfile, Loader=yaml.FullLoader)

    github_token = sct["github"]["token"]

    git_repo_name = "VL_EingebetteteSysteme"
    git_repo_owner = "TUBAF-IfI-LiaScript"
    default_data_folder = Path("data", git_repo_name)

    p = Path(default_data_folder)
    p.mkdir(parents=True, exist_ok=True)

    generateWorkflowHistory(owner=git_repo_owner,
                            repo=git_repo_name,
                            data_dir=default_data_folder,
                            github_token=github_token)

    pd_wfh = getWorkflowPandasTable(default_data_folder)

    print(pd_wfh.iloc[0])

    # print(getWorkflowForCommit(wf, '44564e9296c90b100d0a662583dd7310c1d33108'))

    # r = requestLogFiles(owner = "TUBAF-IfI-LiaScript",
    #                     repo = 'VL_EingebetteteSysteme',
    #                     github_token = github_token,
    #                     workflow_id = 347871334)
