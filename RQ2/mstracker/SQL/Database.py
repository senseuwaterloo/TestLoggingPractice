from Models.BaseModel import db
from Models.Log import Log
from Models.Commit import Commit
from Models.Repository import Repository
from Utils import FileUtil, RepoUtil


def create_tables():
    db.connect()
    db.create_tables([Repository, Commit, Log], safe=True)


# def save_repos_to_db():
#     Repository.create(repo_id="1", project_name="hadoop")


def get_all_repos() -> [Repository]:
    return Repository.select()


def save_repos_to_db(csv_path: str):
    repo_url_list = FileUtil.get_project_repo_url(csv_path)
    # RepoUtil.clone_git_repos(repo_url_list)
    for repo_url in repo_url_list:
        temp_repo_name = repo_url.split('/')[-1]
        repo_name = temp_repo_name.split('.')[0]

        repo = Repository.get_or_none(Repository.project_name == repo_name)
        repo_id = FileUtil.get_repo_id(csv_path, repo_url)

        if repo is None:
            Repository.create(repo_id=repo_id, project_name=repo_name)
        # else:
        #     repo.repo_id = repo_id
        #     repo.save()
