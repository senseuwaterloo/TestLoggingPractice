import git
from datetime import datetime
from Utils import BashUtil

import Models.Config

EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def get_project_repository(project_path: str):
    repository = git.Repo(project_path)
    assert not repository.bare
    return repository


def get_single_commit_diff(head_commit):
    parent_commit = head_commit.parents[0]
    diff = parent_commit.diff(head_commit)
    return diff


def get_commit_sha_pair(head_commit):
    parent_commit = head_commit.parents[0]
    head_commit_sha = head_commit.hexsha
    parent_commit_sha = parent_commit.hexsha
    return head_commit_sha, parent_commit_sha


def get_all_commits(path: str):
    git_repo = get_project_repository(path)
    g = git_repo.git
    result = g.log('--oneline', '--pretty=%H').split('\n')
    return result


def get_updated_commits(path: str):
    git_repo = get_project_repository(path)
    g = git_repo.git
    last_commit_date = get_last_commit_date(path)
    print("last commit date: " + str(last_commit_date))
    refresh_and_pull_git_repo(path)
    latest_commit_date = get_last_commit_date(path)
    print("latest commit date: " + str(latest_commit_date))
    if last_commit_date < latest_commit_date:
        updated_commits = \
            g.log('--oneline', '--pretty=%H', '--date=local', '--after={}'.format(last_commit_date)).split('\n')
    else:
        updated_commits = []
    return updated_commits


def get_diff_between_commits(parent_commit, head_commit):
    return parent_commit.diff(head_commit, create_patch=False)


def get_diff_of_initial_commit(git_repo, initial_commit):
    return git_repo.tree(EMPTY_TREE_SHA).diff(initial_commit, create_patch=False)


def get_first_commit_date(path: str):
    output = BashUtil.run("git log --reverse --pretty='format: %ai' | head -n 1", cwd=path)
    datetime_str = output.strip()
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S %z')


def get_last_commit_date(path: str):
    output = BashUtil.run("git log --pretty='format: %ai' | head -n 1", cwd=path)
    datetime_str = output.strip()
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S %z')


# tr -d ' ': delete the blank space in the result
def get_files_num(path: str):
    file_num = BashUtil.run("git ls-files | wc -l | tr -d ' '", cwd=path)
    return int(file_num)


def get_commits_num(path: str):
    commit_num = BashUtil.run("git log --oneline $commit | wc -l | tr -d ' '", cwd=path)
    return int(commit_num)


def get_authors_num(path: str):
    output = BashUtil.run("git log --format='%aN' | sort -u | wc -l | tr -d ' '", cwd=path)
    return int(output)


def refresh_and_pull_git_repo(path: str):
    git_repo = get_project_repository(path)
    reset(git_repo)
    git_repo.git.pull()


def reset(git_repo):
    g = git_repo.git
    g.reset('--hard')


def clone_git_repos(repo_url_list: list):
    for item in repo_url_list:
        print(item)
        temp_app_name = item.split('/')[-1]
        app_name = temp_app_name.split('.')[0]
        local_repo_path = Models.Config.MSTRACKER_PROJECT_PATH + app_name
        BashUtil.run("git clone {} '{}'".format(item, local_repo_path))
