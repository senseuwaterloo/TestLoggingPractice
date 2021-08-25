import platform

MSTRACKER_PROJECT_PATH = "/Users/holen/DegreeProject/VCS/mstracker_update/"
LEVENSHTEIN_RATIO_THRESHOLD = 0.5

# Detect type
DETECT_UPDATE = 'detect_update'
DETECT_ALL = 'detect_all'

# Database
DB_NAME = 'added_log_20210118'
DB_USER = 'holen'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_PORT = 5432

QUERY_ADDED_LOG = " \copy (select commit.repo_fk, commit.commit_id, commit.author_name, commit.author_email, commit.authored_date, commit.message, log.file_path, log.embed_method, log.change_type, log.content, log.content_update_from from log join commit on commit.id = log.commit_fk where author_email not like '%noreply.github.com%' and commit.authored_date > '2020-07-21' and log.change_type like 'ADD%') to /Users/holen/Desktop/added_log.csv csv header;"


def get_repo_local_path_with_project_name(project_name):
    return MSTRACKER_PROJECT_PATH + project_name


def get_cloc_command():
    # Execute on local computer
    if platform.system() == 'Darwin':
        cloc_command = "cloc"
    # Execute on omen or xishi
    else:
        cloc_command = "/home/users/hzhang/project/library/cloc-1.84/cloc"

    return cloc_command
