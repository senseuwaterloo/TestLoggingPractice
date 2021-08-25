from SQL import Database


if __name__ == "__main__":
    csv_path = 'Data/studied_projects.csv'
    Database.create_tables()
    Database.save_repos_to_db(csv_path)
