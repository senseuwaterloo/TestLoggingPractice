import re
from pathlib import Path

import pandas as pd

# calculate log number

repo_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_repository.csv")
commit_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_commit.csv")
log_csv = pd.read_csv("/Users/holen/Desktop/ms_db_data/ms_log.csv")

log_call_df = log_csv[log_csv["call_type"] == "LOG_CALL"]
print_call_df = log_csv[log_csv["call_type"] == "PRINT_CALL"]
logging_call_df = pd.concat([log_call_df, print_call_df], axis=0)

repo_id_list = repo_csv["id"].to_list()

total_production_nol = 0
total_typical_production_nol = 0
total_production_soe = 0
total_test_nol = 0
total_typical_test_nol = 0
total_test_soe = 0

total_test_file = 0
total_production_file = 0

pre_path = "/Users/holen/DegreeProject/VCS/mstracker_total/"

for repo_id in repo_id_list:

    each_repo_df = repo_csv[repo_csv["id"] == repo_id]
    repo_name_list = each_repo_df["project_name"].values
    repo_name = repo_name_list[0]

    repo_p = Path(pre_path + "/" + str(repo_name))
    java_file_list = list(repo_p.glob('**/*.java'))
    str_java_file_list = [str(i) for i in java_file_list]
    r = re.compile("^[Mm]ock|[Mm]ock$|.*[Tt]est.*")
    test_file_list = list(filter(r.match, str_java_file_list))
    test_file_num = len(test_file_list)
    production_file_num = len(java_file_list) - test_file_num

    total_test_file = total_test_file + test_file_num
    total_production_file = total_production_file + production_file_num

    test_log_call_num = each_repo_df["test_log_caller_loc"].values[0]
    test_print_call_num = each_repo_df["test_print_caller_loc"].values[0]
    test_total_log_call = test_log_call_num + test_print_call_num

    test_typical_log_per_file = test_log_call_num / test_file_num
    test_soe_per_file = test_print_call_num / test_file_num

    production_log_call_num = each_repo_df["production_log_caller_loc"].values[0]
    production_print_call_num = each_repo_df["production_print_caller_loc"].values[0]
    production_total_log_call = production_log_call_num + production_print_call_num

    production_typical_log_per_file = production_log_call_num / production_file_num
    production_soe_per_file = production_print_call_num / production_file_num

    total_production_nol = total_production_nol + production_total_log_call
    total_typical_production_nol = total_typical_production_nol + production_log_call_num
    total_production_soe = total_production_soe + production_print_call_num
    total_test_nol = total_test_nol + test_total_log_call
    total_typical_test_nol = total_typical_test_nol + test_log_call_num
    total_test_soe = total_test_soe + test_print_call_num





    print("{}:".format(repo_name))
    print("test log call num: {}".format(test_log_call_num))
    print("test print call num: {}".format(test_print_call_num))
    print("total test log num: {}".format(test_total_log_call))
    print("production log call num: {}".format(production_log_call_num))
    print("production print call num: {}".format(production_print_call_num))
    print("total production log num: {}".format(production_total_log_call))
    print("test_typical_log_per_file: {}".format(test_typical_log_per_file))
    print("test_soe_per_file: {}".format(test_soe_per_file))
    print("production_typical_log_per_file: {}".format(production_typical_log_per_file))
    print("production_soe_per_file: {}".format(production_soe_per_file))


print("Total:")
print(total_production_nol)
print(total_typical_production_nol)
print(total_production_soe)
print(total_test_nol)
print(total_typical_test_nol)
print(total_test_soe)
print(total_typical_production_nol/total_production_file)
print(total_production_soe/total_production_file)
print(total_typical_test_nol/total_test_file)
print(total_test_soe/total_test_file)

