from utils import shell_util
from datetime import datetime


def get_files_num(path: str):
    output = shell_util.run_command("git ls-files | wc -l | tr -d ' '", cwd=path)
    return int(output)


def get_commits_num(path: str):
    output = shell_util.run_command("git log --oneline $commit | wc -l | tr -d ' '", cwd=path)
    return int(output)


def get_repo_age_str(path: str):
    output = shell_util.run_command("git log --reverse --pretty=oneline --format='%ar' | head -n 1 | LC_ALL=C sed 's/ago//' | tr -d ' '", cwd=path)
    return output


def get_last_commit_date(path: str):
    output = shell_util.run_command("git log --pretty='format: %ai' | head -n 1", cwd=path)
    datetime_str = output.strip()
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S %z')


def get_first_commit_date(path: str):
    output = shell_util.run_command("git log --reverse --pretty='format: %ai' | head -n 1", cwd=path)
    datetime_str = output.strip()
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S %z')


def get_authors_num(path: str):
    output = shell_util.run_command("git log --format='%aN' | sort -u | wc -l | tr -d ' '", cwd=path)
    return int(output)
