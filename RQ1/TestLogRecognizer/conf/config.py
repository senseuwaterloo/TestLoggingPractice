# Database
import platform

DB_NAME = 'DB_NAME'
DB_USER = 'DB_USER'
DB_PASSWORD = ''
DB_HOST = '127.0.0.1'
DB_PORT = 5432


PROJECT_PATH = "indicate_the_location_of _the_analyzed_repo_here"


def get_repo_local_path_with_project_name(project_name):
    return PROJECT_PATH + '/' + project_name


def get_cloc_command():
    # Execute on local computer
    if platform.system() == 'Darwin':
        cloc_command = "cloc"
    # Execute on omen or xishi
    else:
        # need to change based on your configuration of cloc
        cloc_command = "path_to_cloc"

    return cloc_command
