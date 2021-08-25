import pandas as pd

repo_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_repository.csv")
commit_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_commit.csv")
log_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_log.csv")

log_call_df = log_csv[log_csv["call_type"] == "LOG_CALL"]
print_call_df = log_csv[log_csv["call_type"] == "PRINT_CALL"]
log_df_without_assert = pd.concat([log_call_df, print_call_df], axis=0)
#
# update_df = df_without_assert[df_without_assert["change_type"] == "UPDATED"]
# print(len(update_df))
# added_df = df_without_assert[df_without_assert["change_type"].str.contains("ADDED")]
# print(len(added_df))
# deleted_df = df_without_assert[df_without_assert["change_type"].str.contains("DELETED")]
# print(len(deleted_df))

repo_id_list = commit_csv["repo_fk"].to_list()
repo_id_list = list(dict.fromkeys(repo_id_list))
print(repo_id_list)

id_range_dict = {}

for repo_id in repo_id_list:
    tmp_df = commit_csv[commit_csv["repo_fk"] == repo_id]
    df_index_list = tmp_df["id"].to_list()
    min_id = min(df_index_list)
    max_id = max(df_index_list)
    id_range_dict[repo_id] = (min_id, max_id)

print(id_range_dict)


total_test_update = 0
total_test_add = 0
total_test_delete = 0

total_production_update = 0
total_production_add = 0
total_production_delete = 0

for each_key in id_range_dict.keys():
    tmp_repo_df = repo_csv[repo_csv["id"] == each_key]
    repo_name_list = tmp_repo_df["project_name"].values
    repo_name = repo_name_list[0]
    # repo_name = tmp_repo_df["project_name"].at[0, "project_name"]

    min_value = id_range_dict[each_key][0]
    max_value = id_range_dict[each_key][1]
    each_project_df = log_df_without_assert[(log_df_without_assert["commit_fk"]>=min_value)
                                            & (log_df_without_assert["commit_fk"]<=max_value)]

    test_project_df = each_project_df[each_project_df["is_test_log"] == "t"]
    production_project_df = each_project_df[each_project_df["is_test_log"] == "f"]

    test_update_df = test_project_df[test_project_df["change_type"] == "UPDATED"]
    test_added_df = test_project_df[test_project_df["change_type"].str.contains("ADDED")]
    test_delete_df = test_project_df[test_project_df["change_type"].str.contains("DELETED")]

    production_update_df = production_project_df[production_project_df["change_type"] == "UPDATED"]
    production_added_df = production_project_df[production_project_df["change_type"].str.contains("ADDED")]
    production_delete_df = production_project_df[production_project_df["change_type"].str.contains("DELETED")]

    test_update_percent = len(test_update_df)/(len(test_update_df) + len(test_added_df) + len(test_delete_df))
    test_added_percent = len(test_added_df) / (len(test_update_df) + len(test_added_df) + len(test_delete_df))
    test_deleted_percent = len(test_delete_df) / (len(test_update_df) + len(test_added_df) + len(test_delete_df))

    production_update_percent = len(production_update_df) / (len(production_update_df) + len(production_added_df) + len(production_delete_df))
    production_added_percent = len(production_added_df) / (len(production_update_df) + len(production_added_df) + len(production_delete_df))
    production_deleted_percent = len(production_delete_df) / (len(production_update_df) + len(production_added_df) + len(production_delete_df))

    str_test_update_percent = str(("%.2f" % (test_update_percent*100)))+"\\%"
    str_test_added_percent = str(("%.2f" % (test_added_percent*100))) + "\\%"
    str_test_deleted_percent = str(("%.2f" % (test_deleted_percent*100))) + "\\%"

    str_production_update_percent = str(("%.2f" % (production_update_percent*100))) + "\\%"
    str_production_added_percent = str(("%.2f" % (production_added_percent*100))) + "\\%"
    str_production_deleted_percent = str(("%.2f" % (production_deleted_percent*100))) + "\\%"


    each_project_update_df = each_project_df[each_project_df["change_type"] == "UPDATED"]
    each_project_added_df = each_project_df[each_project_df["change_type"].str.contains("ADDED")]
    each_project_delete_df = each_project_df[each_project_df["change_type"].str.contains("DELETED")]


    total_test_update = total_test_update + len(test_update_df)
    total_test_add = total_test_add + len(test_added_df)
    total_test_delete = total_test_delete + len(test_delete_df)

    total_production_update = total_production_update + len(production_update_df)
    total_production_add = total_production_add + len(production_added_df)
    total_production_delete = total_production_delete + len(production_delete_df)

    # print("repo name: {}".format(str(repo_name)))
    # # print(each_key)
    # print("test update: {}".format(len(test_update_df)))
    # print("test added: {}".format(len(test_added_df)))
    # print("test deleted: {}".format(len(test_delete_df)))
    #
    # print("production update: {}".format(len(production_update_df)))
    # print("production added: {}".format(len(production_added_df)))
    # print("production deleted: {}".format(len(production_delete_df)))
    #
    # print("total update: {}".format(len(each_project_update_df)))
    # print("total added: {}".format(len(each_project_added_df)))
    # print("total deleted: {}".format(len(each_project_delete_df)))

    print("{} & {}({}) & {}({}) & {}({}) & {}({}) & {}({}) & {}({})".format(repo_name,
                                                            len(production_update_df),str_production_update_percent,
                                                            len(production_added_df),str_production_added_percent,
                                                            len(production_delete_df),str_production_deleted_percent,
                                                            len(test_update_df),str_test_update_percent,
                                                            len(test_added_df),str_test_added_percent,
                                                            len(test_delete_df),str_test_deleted_percent))


print(total_test_update)
print(total_test_add)
print(total_test_delete)
print(total_production_update)
print(total_production_add)
print(total_production_delete)














