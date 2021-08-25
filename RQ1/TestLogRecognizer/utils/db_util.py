from models.base_model import db
from models.file import File
from models.log import Log
from models.repo import Repo
from utils import file_util


def create_tables():
    db.connect()
    db.create_tables([Repo, File, Log], safe=True)


# def save_repos_to_db():
#     Repository.create(repo_id="1", project_name="hadoop")


def get_all_repos() -> [Repo]:
    return Repo.select()


def save_repos_to_db(csv_path: str):
    repo_url_list = file_util.get_project_repo_url(csv_path)
    # RepoUtil.clone_git_repos(repo_url_list)
    for repo_url in repo_url_list:
        temp_repo_name = repo_url.split('/')[-1]
        repo_name = temp_repo_name.split('.')[0]

        repo = Repo.get_or_none(Repo.repo_name == repo_name)
        repo_id = file_util.get_repo_id(csv_path, repo_url)

        if repo is None:
            Repo.create(repo_id=repo_id, repo_name=repo_name)
