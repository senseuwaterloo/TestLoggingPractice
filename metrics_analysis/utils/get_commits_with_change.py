import pandas as pd

# get commits number with log change

repo_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_repository.csv")
commit_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_commit.csv")

repo_id_list = repo_csv["id"].to_list()

total_test_changed_commits = 0
total_production_changed_commits = 0
total_both_changed_commits = 0
for repo_id in repo_id_list:
    each_repo_df = commit_csv[commit_csv["repo_fk"] == repo_id]
    each_repo_df = each_repo_df[each_repo_df["is_merge_commit"] == "f"]
    commit_id_list = each_repo_df["id"].to_list()

    test_changed_commits = 0
    production_changed_commits = 0
    both_changed_commits = 0
    for each_commit in commit_id_list:
        each_commit_df = each_repo_df[each_repo_df["id"] == each_commit]

        added_test_log_loc = each_commit_df["added_test_log_caller_loc"].values[0]
        deleted_test_log_loc = each_commit_df["deleted_test_log_caller_loc"].values[0]
        updated_test_log_loc = each_commit_df["updated_test_log_caller_loc"].values[0]

        added_test_print_loc = each_commit_df["added_test_print_caller_loc"].values[0]
        deleted_test_print_loc = each_commit_df["deleted_test_print_caller_loc"].values[0]
        updated_test_print_loc = each_commit_df["updated_test_print_caller_loc"].values[0]

        changed_test_loc = added_test_log_loc + deleted_test_log_loc + updated_test_log_loc + added_test_print_loc + deleted_test_print_loc + updated_test_print_loc

        added_production_log_loc = each_commit_df["added_production_log_caller_loc"].values[0]
        deleted_production_log_loc = each_commit_df["deleted_production_log_caller_loc"].values[0]
        updated_production_log_loc = each_commit_df["updated_production_log_caller_loc"].values[0]

        added_production_print_loc = each_commit_df["added_production_print_caller_loc"].values[0]
        deleted_production_print_loc = each_commit_df["deleted_production_print_caller_loc"].values[0]
        updated_production_print_loc = each_commit_df["updated_production_print_caller_loc"].values[0]

        changed_production_loc = added_production_log_loc + deleted_production_log_loc + updated_production_log_loc + added_production_print_loc + deleted_production_print_loc + updated_production_print_loc

        if changed_test_loc > 0:
            test_changed_commits = test_changed_commits + 1
        if changed_production_loc > 0:
            production_changed_commits = production_changed_commits + 1
        if changed_test_loc > 0 and changed_production_loc > 0:
            both_changed_commits = both_changed_commits + 1

    total_test_changed_commits = total_test_changed_commits + test_changed_commits
    total_production_changed_commits = total_production_changed_commits + production_changed_commits
    total_both_changed_commits = total_both_changed_commits + both_changed_commits

print(total_test_changed_commits)
print(total_production_changed_commits)
print(total_both_changed_commits)
