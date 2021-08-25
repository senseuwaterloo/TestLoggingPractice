from Models import Repository, Config
from Profilers import ProjectProfiler
from SQL import Database


def detect_project(detect_type):
    if detect_type == '1':
        pass_detect_type = Config.DETECT_ALL
    else:
        pass_detect_type = Config.DETECT_UPDATE

    all_repos = Database.get_all_repos().order_by(Repository.repo_id)

    for repo in all_repos:
        # print(repo.project_name)
        ProjectProfiler.project_profiler(repo, pass_detect_type)


if __name__ == "__main__":
    print("Please enter the detect type:")
    print("(1) Detect all commit")
    print("(2) Detect updated commit")
    input_detect_type = input()
    detect_project(input_detect_type)
