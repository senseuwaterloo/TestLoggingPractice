import pandas as pd
from scipy.stats import mannwhitneyu
from utils import cliffsDelta

repo_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_repository.csv")
commit_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_commit.csv")
log_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_log.csv")

log_call_df = log_csv[log_csv["call_type"] == "LOG_CALL"]
print_call_df = log_csv[log_csv["call_type"] == "PRINT_CALL"]
monitoring_call_df = pd.concat([log_call_df, print_call_df], axis=0)

repo_id_list = repo_csv["id"].to_list()
# repo_id_list = list(dict.fromkeys(repo_id_list))

total_commit_num = 0
total_removed_sloc_commit = 0
total_removed_loc_commit = 0
total_code_churn_rate = 0
total_test_code_churn_rate = 0
total_production_code_churn_rate = 0
total_ms_churn_rate = 0
total_test_ms_churn_rate = 0
total_production_ms_churn_rate = 0

total_test_churn_rate = []
total_production_churn_rate = []


for repo_id in repo_id_list:
    test_churn_rate_list = []
    production_churn_rate_list = []

    each_repo_df = commit_csv[commit_csv["repo_fk"] == repo_id]
    each_repo_df = each_repo_df[each_repo_df["is_merge_commit"] == "f"]

    tmp_repo_df = repo_csv[repo_csv["id"] == repo_id]
    repo_name_list = tmp_repo_df["project_name"].values
    repo_name = repo_name_list[0]
    commit_id_list = each_repo_df["id"].to_list()

    print(repo_name)

    repo_code_churn_rate = 0
    repo_test_code_churn_rate = 0
    repo_production_code_churn_rate = 0
    repo_ms_churn_rate = 0
    repo_test_ms_churn_rate = 0
    repo_production_ms_churn_rate = 0

    total_commit_num = total_commit_num + len(commit_id_list)

    # print(len(commit_id_list))
    removed_sloc_commit = 0
    removed_loc_commit = 0

    for each_commit in commit_id_list:
        # print(len(commit_id_list))
        each_commit_df = each_repo_df[each_repo_df["id"] == each_commit]

        # print(each_commit_df["commit_id"])

        test_sloc = each_commit_df["test_sloc"].values[0]
        production_sloc = each_commit_df["production_sloc"].values[0]

        log_loc = each_commit_df["log_caller_loc"].values[0]
        print_loc = each_commit_df["print_caller_loc"].values[0]
        ms_loc = log_loc + print_loc

        test_log_loc = each_commit_df["test_log_caller_loc"].values[0]
        test_print_loc = each_commit_df["test_print_caller_loc"].values[0]
        test_ms_loc = test_log_loc + test_print_loc

        production_log_loc = each_commit_df["production_log_caller_loc"].values[0]
        production_print_loc = each_commit_df["production_print_caller_loc"].values[0]
        production_ms_loc = production_log_loc + production_print_loc

        # print(test_sloc + production_sloc)
        # print(production_ms_loc)

        added_test_sloc = each_commit_df["added_test_sloc"].values[0]
        deleted_test_sloc = each_commit_df["deleted_test_sloc"].values[0]
        updated_test_sloc = each_commit_df["updated_test_sloc"].values[0]


        added_production_sloc = each_commit_df["added_production_sloc"].values[0]
        deleted_production_sloc = each_commit_df["deleted_production_sloc"].values[0]
        updated_production_sloc = each_commit_df["updated_production_sloc"].values[0]

        # print(added_test_sloc)
        # print(deleted_test_sloc)
        # print(updated_test_sloc)
        # print(added_test_sloc + added_production_sloc)

        added_log_loc = each_commit_df["added_log_caller_loc"].values[0]
        deleted_log_loc = each_commit_df["deleted_log_caller_loc"].values[0]
        updated_log_loc = each_commit_df["updated_log_caller_loc"].values[0]

        added_print_loc = each_commit_df["added_print_caller_loc"].values[0]
        deleted_print_loc = each_commit_df["deleted_print_caller_loc"].values[0]
        updated_print_loc = each_commit_df["updated_print_caller_loc"].values[0]

        added_test_log_loc = each_commit_df["added_test_log_caller_loc"].values[0]
        deleted_test_log_loc = each_commit_df["deleted_test_log_caller_loc"].values[0]
        updated_test_log_loc = each_commit_df["updated_test_log_caller_loc"].values[0]

        added_test_print_loc = each_commit_df["added_test_print_caller_loc"].values[0]
        deleted_test_print_loc = each_commit_df["deleted_test_print_caller_loc"].values[0]
        updated_test_print_loc = each_commit_df["updated_test_print_caller_loc"].values[0]

        added_production_log_loc = each_commit_df["added_production_log_caller_loc"].values[0]
        deleted_production_log_loc = each_commit_df["deleted_production_log_caller_loc"].values[0]
        updated_production_log_loc = each_commit_df["updated_production_log_caller_loc"].values[0]

        added_production_print_loc = each_commit_df["added_production_print_caller_loc"].values[0]
        deleted_production_print_loc = each_commit_df["deleted_production_print_caller_loc"].values[0]
        updated_production_print_loc = each_commit_df["updated_production_print_caller_loc"].values[0]

        if test_sloc > 0 and production_sloc > 0:
            code_churn_rate = \
                (added_test_sloc + deleted_test_sloc + 2*updated_test_sloc + added_production_sloc + deleted_production_sloc + 2*updated_production_sloc)/(test_sloc + production_sloc)
            test_code_churn_rate = (added_test_sloc + deleted_test_sloc + 2 * updated_test_sloc) / test_sloc
            production_code_churn_rate = \
                (added_production_sloc + deleted_production_sloc + 2 * updated_production_sloc) / production_sloc
        else:
            code_churn_rate = 0
            test_code_churn_rate = 0
            production_code_churn_rate = 0

            removed_sloc_commit = removed_sloc_commit + 1

        # print("code churn rate: {}".format(code_churn_rate))

        test_loc_churn = added_test_log_loc + deleted_test_log_loc + 2 * updated_test_log_loc + added_test_print_loc + deleted_test_print_loc + 2 * updated_test_print_loc
        production_loc_churn = added_production_log_loc + deleted_production_log_loc + 2 * updated_production_log_loc + added_production_print_loc + deleted_production_print_loc + 2 * updated_production_print_loc

        if test_ms_loc > 0 and production_ms_loc > 0:
            ms_churn_rate = (test_loc_churn + production_loc_churn)/(test_ms_loc + production_ms_loc)
            test_ms_churn_rate = test_loc_churn / test_ms_loc
            production_ms_churn_rate = production_loc_churn / production_ms_loc
        else:
            ms_churn_rate = 0
            test_ms_churn_rate = 0
            production_ms_churn_rate = 0

            removed_loc_commit = removed_loc_commit + 1

        repo_code_churn_rate = repo_code_churn_rate + code_churn_rate
        repo_test_code_churn_rate = repo_test_code_churn_rate + test_code_churn_rate
        repo_production_code_churn_rate = repo_production_code_churn_rate + production_code_churn_rate

        repo_ms_churn_rate = repo_ms_churn_rate + ms_churn_rate
        repo_test_ms_churn_rate = repo_test_ms_churn_rate + test_ms_churn_rate
        repo_production_ms_churn_rate = repo_production_ms_churn_rate + production_ms_churn_rate

        test_churn_rate_list.append(test_ms_churn_rate)
        production_churn_rate_list.append(production_ms_churn_rate)

        total_test_churn_rate.append(test_ms_churn_rate)
        total_production_churn_rate.append(production_ms_churn_rate)


        # print("repo_code_churn_rate: {}".format(repo_code_churn_rate))
    # - removed_sloc_commit - removed_loc_commit
    avg_repo_code_churn_rate = repo_code_churn_rate/(len(commit_id_list) - removed_sloc_commit)
    avg_repo_test_code_churn_rate = repo_test_code_churn_rate/(len(commit_id_list) - removed_sloc_commit)
    avg_repo_production_code_churn_rate = repo_production_code_churn_rate/(len(commit_id_list) - removed_sloc_commit)
    avg_repo_ms_churn_rate = repo_ms_churn_rate/(len(commit_id_list) - removed_loc_commit)
    avg_repo_test_ms_churn_rate = repo_test_ms_churn_rate/(len(commit_id_list) - removed_loc_commit)
    avg_repo_production_ms_churn_rate = repo_production_ms_churn_rate/(len(commit_id_list) - removed_loc_commit)

    print(repo_name)
    print("code churn rate: {}".format(avg_repo_code_churn_rate))
    print("test code churn rate: {}".format(avg_repo_test_code_churn_rate))
    print("production code churn rate: {}".format(avg_repo_production_code_churn_rate))
    print("ms churn rate: {}".format(avg_repo_ms_churn_rate))
    print("test ms churn rate: {}".format(avg_repo_test_ms_churn_rate))
    print("production ms churn rate: {}".format(avg_repo_production_ms_churn_rate))

    total_code_churn_rate = total_code_churn_rate + repo_code_churn_rate
    total_test_code_churn_rate = total_test_code_churn_rate + repo_test_code_churn_rate
    total_production_code_churn_rate = total_production_code_churn_rate + repo_production_code_churn_rate
    total_ms_churn_rate = total_ms_churn_rate + repo_ms_churn_rate
    total_test_ms_churn_rate = total_test_ms_churn_rate + repo_test_ms_churn_rate
    total_production_ms_churn_rate = total_production_ms_churn_rate + repo_production_ms_churn_rate

    total_removed_sloc_commit = total_removed_sloc_commit + removed_sloc_commit
    total_removed_loc_commit = total_removed_loc_commit + removed_loc_commit

#  - total_removed_sloc_commit  - total_removed_loc_commit
total_avg_code_churn_rate = total_code_churn_rate/(total_commit_num - total_removed_sloc_commit)
total_avg_test_code_churn_rate = total_test_code_churn_rate/(total_commit_num - total_removed_sloc_commit)
total_avg_production_code_churn_rate = total_production_code_churn_rate/(total_commit_num - total_removed_sloc_commit)
total_avg_ms_churn_rate = total_ms_churn_rate/(total_commit_num - total_removed_loc_commit)
total_avg_test_ms_churn_rate = total_test_ms_churn_rate/(total_commit_num - total_removed_loc_commit)
total_avg_production_ms_churn_rate = total_production_ms_churn_rate/(total_commit_num - total_removed_loc_commit)

print("Total:")
print("code churn rate: {}".format(total_avg_code_churn_rate))
print("test code churn rate: {}".format(total_avg_test_code_churn_rate))
print("production code churn rate: {}".format(total_avg_production_code_churn_rate))
print("ms churn rate: {}".format(total_avg_ms_churn_rate))
print("test ms churn rate: {}".format(total_avg_test_ms_churn_rate))
print("production ms churn rate: {}".format(total_avg_production_ms_churn_rate))

# stat, p = pearsonr(test_churn_rate_list, production_churn_rate_list)
# print('Statistics=%.3f, p=%.10f' % (stat, p))







