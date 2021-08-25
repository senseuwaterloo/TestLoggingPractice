from utils import db_util


if __name__ == "__main__":
    csv_path = 'docs/studied_projects.csv'
    db_util.create_tables()
    db_util.save_repos_to_db(csv_path)
