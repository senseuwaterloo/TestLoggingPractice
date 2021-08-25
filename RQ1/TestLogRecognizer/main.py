from models.repo import Repo
from recognizer import repo_recognizer
from utils import db_util


def project_detector():
    all_repos = db_util.get_all_repos().order_by(Repo.repo_id)
    for repo in all_repos:
        print(repo.repo_name)
        repo_recognizer.detect_project(repo)


if __name__ == "__main__":
    project_detector()
