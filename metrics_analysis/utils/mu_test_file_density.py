import pandas as pd
from scipy.stats import pearsonr
from scipy.stats import mannwhitneyu, wilcoxon
from utils import cliffsDelta
# from scipy.stats import spearmanr
# used to mann u test the log densities at file level


file_csv = pd.read_csv("path_to_file.csv")
all_subject_list = file_csv["repo_fk"].to_list()
unique_subject_list = list(dict.fromkeys(all_subject_list))

total_test_file_density = []
total_production_file_density = []

for subject in unique_subject_list:
    print(subject)
    each_repo_df = file_csv[file_csv["repo_fk"] == subject]
    test_file_df = each_repo_df[each_repo_df["is_test_file"] == True]
    test_file_density_list = []
    test_file_loc_list = []
    for index, row in test_file_df.iterrows():
        try:
            each_density = row['logging_loc'] / row['sloc']
        except ZeroDivisionError:
            each_density = 0

        test_file_density_list.append(each_density)
        test_file_loc_list.append(row['logging_loc'])
        total_test_file_density.append(each_density)


    production_file_df = each_repo_df[each_repo_df["is_test_file"] == False]
    production_file_density_list = []
    production_file_loc_list = []
    for index, row in production_file_df.iterrows():
        try:
            each_density = row['logging_loc'] / row['sloc']
        except ZeroDivisionError:
            each_density = 0

        production_file_density_list.append(each_density)
        production_file_loc_list.append(row['logging_loc'])
        total_production_file_density.append(each_density)

    # stat, p = pearsonr(test_file_density_list, production_file_density_list)
    # print('Statistics=%.3f, p=%.10f' % (stat, p))

    stat, p = mannwhitneyu(test_file_density_list, production_file_density_list)
    print('Statistics=%.3f, p=%.10f' % (stat, p))

    if p <= 0.05:
        d, res = cliffsDelta.cliffsDelta(test_file_density_list, production_file_density_list)
        print(d)
        print(res)

stat, p = mannwhitneyu(total_test_file_density, total_production_file_density)
print('total' + 'Statistics=%.3f, p=%.10f' % (stat, p))

if p <= 0.05:
    d, res = cliffsDelta.cliffsDelta(total_test_file_density, total_production_file_density)
    print(d)
    print(res)
