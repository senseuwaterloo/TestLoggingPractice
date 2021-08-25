# Database
import platform

DB_NAME = 'testlog_rq1_variable_num_update'
DB_USER = 'holen'
DB_PASSWORD = ''
DB_HOST = '127.0.0.1'
DB_PORT = 5432


PROJECT_PATH = "/Users/holen/DegreeProject/VCS/mstracker_total/"


def get_repo_local_path_with_project_name(project_name):
    return PROJECT_PATH + '/' + project_name


def get_cloc_command():
    # Execute on local computer
    if platform.system() == 'Darwin':
        cloc_command = "cloc"
    # Execute on omen or xishi
    else:
        cloc_command = "/home/users/hzhang/project/library/cloc-1.84/cloc"

    return cloc_command
