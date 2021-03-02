#!/usr/bin/python

import os

def clone_repository(git_repo_owner, git_repo_name, git_repo_dir,
                    git_hub_token=None):
    if os.path.exists(git_repo_dir):
        shutil.rmtree(git_repo_dir, onerror=readonly_handler)
    callbacks = None
    if git_hub_token:
        callbacks = git2.RemoteCallbacks(
            git2.UserPass(git_hub_token, 'x-oauth-basic'))
    repo_ref = f"https://github.com/{git_repo_owner}/{git_repo_name}"
    repo = git2.clone_repository(repo_ref, git_repo_dir, callbacks=callbacks)

    existing_branches = list(repo.branches)
    r = git.Repo.init(git_repo_dir)

    for ref in repo.references:
        branch_name = ref.split('/')[-1]
        if branch_name != 'HEAD' and branch_name not in existing_branches:
            print("  ", branch_name, sep=", ", end="")
            try:
                r.git.branch('--track', branch_name,
                             'remotes/origin/'+branch_name)
            except Exception:
                print("An exception occurred")
                print(" ")

    return True

# getting os permissions to remove (write) readonly files
def readonly_handler(func, local_directory, execinfo):
    os.chmod(local_directory, stat.S_IWRITE)
    func(local_directory)


def generate_data_base(git_repo_dir, data_dir, git_repo_name):

    p = Path(data_dir)
    p.mkdir(parents=True, exist_ok=True)
    sqlite_db_file = Path(data_dir, git_repo_name + ".db")
    if os.path.exists(sqlite_db_file):
        os.remove(sqlite_db_file)
    git2net.mine_git_repo(git_repo_dir, sqlite_db_file,
                          no_of_processes=1,
                          max_modifications=1000)

    return True