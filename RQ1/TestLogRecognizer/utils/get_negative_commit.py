import pandas as pd

repo_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_repository.csv")
commit_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_commit.csv")
log_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_log.csv")

repo_id_list = repo_csv["id"].to_list()

for repo_id in repo_id_list:
    each_repo_df = commit_csv[commit_csv["repo_fk"] == repo_id]
    each_repo_df = each_repo_df[each_repo_df["is_merge_commit"] == "f"]

    tmp_repo_df = repo_csv[repo_csv["id"] == repo_id]
    repo_name_list = tmp_repo_df["project_name"].values
    repo_name = repo_name_list[0]
    commit_id_list = each_repo_df["id"].to_list()
    print(repo_name)
    tmp_list = []
    for each_commit in commit_id_list:
        # print(len(commit_id_list))
        each_commit_df = each_repo_df[each_repo_df["id"] == each_commit]

        # print(each_commit_df["commit_id"])

        test_sloc = each_commit_df["test_sloc"].values[0]
        production_sloc = each_commit_df["production_sloc"].values[0]


        test_log_loc = each_commit_df["test_log_caller_loc"].values[0]
        test_print_loc = each_commit_df["test_print_caller_loc"].values[0]
        test_ms_loc = test_log_loc + test_print_loc

        production_log_loc = each_commit_df["production_log_caller_loc"].values[0]
        production_print_loc = each_commit_df["production_print_caller_loc"].values[0]
        production_ms_loc = production_log_loc + production_print_loc

        if test_sloc < 0 or production_sloc < 0 or test_log_loc < 0 or test_print_loc < 0 or production_log_loc < 0 or production_print_loc < 0:
            tmp_list.append(each_commit_df["commit_id"].values[0])

    print(len(tmp_list))
    if len(tmp_list) > 0:
        print(tmp_list[0])