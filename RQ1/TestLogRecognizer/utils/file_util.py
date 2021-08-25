import os
import re
import uuid
from pathlib import Path
from utils import shell_util
import pandas as pd


def is_java_file(file_path: str):
    if file_path.endswith('.java'):
        return True
    else:
        return False


def is_test_file(file_path: str):
    result = False
    if is_java_file(file_path):
        file_name = os.path.basename(file_path)
        pattern = '^[Mm]ock|[Mm]ock$|.*[Tt]est.*'
        match = re.search(pattern, file_name)
        # print(match)
        if match is not None:
            result = True

    return result


def get_all_java_files(repo_path: str) -> [Path]:
    repo_p = Path(repo_path)
    try:
        java_file_list = list(repo_p.glob('**/*.java'))
    except:
        java_file_list = shell_util.run_command('find {} -name "*.java"'.format(repo_path)).split()
    return java_file_list


def generate_random_file_name_with_extension(file_extension: str) -> str:
    return "{}.{}".format(generate_hex_uuid_4(), file_extension)


def generate_hex_uuid_4() -> str:
    """Generate UUID (version 4) in hexadecimal representation.
    :return: hexadecimal representation of version 4 UUID.
    """
    return str(uuid.uuid4().hex)


def delete_if_exists(file_path: str):
    path = Path(file_path)
    if path.exists():
        path.unlink()


def get_project_repo_url(csv_path: str):
    df = pd.read_csv(csv_path)
    repo_url_list = df['repo_url'].to_list()
    return repo_url_list


def get_repo_id(csv_path: str, project_url: str):
    df = pd.read_csv(csv_path)
    df = df[df["repo_url"] == project_url]
    repo_id_list = df['repo_id'].to_list()
    return repo_id_list[0]
