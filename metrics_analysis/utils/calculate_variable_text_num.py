import os
import statistics
from collections import Counter

import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mannwhitneyu


log_csv = pd.read_csv('/Users/holen/Downloads/log_variable_update.csv')
# verbosity_list = ["INFO", "WARN", "TRACE", "ERROR", "DEBUG"]
info_log_df = log_csv[log_csv["verbosity_type"] == "INFO"]
warn_log_df = log_csv[log_csv["verbosity_type"] == "WARN"]
trace_log_df = log_csv[log_csv["verbosity_type"] == "TRACE"]
error_log_df = log_csv[log_csv["verbosity_type"] == "ERROR"]
debug_log_df = log_csv[log_csv["verbosity_type"] == "DEBUG"]
vertical_stack = pd.concat([info_log_df, warn_log_df, trace_log_df, error_log_df, debug_log_df], axis=0)
# print(len(vertical_stack))






pattern = '^[Mm]ock|[Mm]ock$|.*[Tt]est.*'
test_variable_num_list = []
production_variable_num_list = []
test_text_length_list = []
production_text_length_list = []
test_argument_type_list = []
production_argument_type_list = []
for index, row in vertical_stack.iterrows():
    var_num = row["variable_number"]
    text_length = row["text_length"]
    argument_type = row["argument_type"]
    # string_content = str(row["content"])
    # string_inside_bracket = string_content[string_content.find("(")+1:string_content.rfind(")")]
    # # print(string_inside_bracket)
    # splited_str = re.split('\+ |, ', string_inside_bracket)
    # print(string_content)
    # if len(splited_str) == 106:
    #     print(string_content)
    # print(splited_str)
    # vertical_stack.at[index, "variable_number"] = len(splited_str)
    file_path = vertical_stack.at[index, "file_path"]
    file_name = os.path.basename(file_path)
    match = re.search(pattern, file_name)
    if match is not None:
        test_variable_num_list.append(var_num)
        test_text_length_list.append(text_length)
        test_argument_type_list.append(argument_type)
    else:
        production_variable_num_list.append(var_num)
        production_text_length_list.append(text_length)
        production_argument_type_list.append(argument_type)

print("mean test variable number:")
print(statistics.mean(test_variable_num_list))
print("test variable number quantile: ")
test_var_df = pd.DataFrame({'col':test_variable_num_list})
print(test_var_df.quantile([0,0.25,0.5,0.75,1]))

print("mean test text length:")
print(statistics.mean(test_text_length_list))
print("test text length quantile:")
test_text_df = pd.DataFrame({'col':test_text_length_list})
print(test_text_df.quantile([0,0.25,0.5,0.75,1]))

print("mean production variable number:")
print(statistics.mean(production_variable_num_list))
print("production variable number quantile: ")
production_df = pd.DataFrame({'col':production_variable_num_list})
print(production_df.quantile([0,0.25,0.5,0.75,1]))

print("mean production text length:")
print(statistics.mean(production_text_length_list))
print("production text length quantile:")
production_text_df = pd.DataFrame({'col':production_text_length_list})
print(production_text_df.quantile([0,0.25,0.5,0.75,1]))

data = [test_text_length_list, production_text_length_list]
# fig = plt.figure(figsize=(10, 7))
#
# # Creating axes instance
# ax = fig.add_axes(["Test", "Production"])
#
# # Creating plot
# bp = ax.boxplot(data)

# show plot
plt.figure(figsize=(6, 6))
plt.ylim(-100, 1800)
flierprops = dict(marker='s', markeredgecolor='#17202A', markersize=2)
plt.boxplot(data, flierprops=flierprops)
plt.xticks([1, 2], ['Test', 'Production'])
plt.xticks(fontsize=24)
plt.yticks(fontsize=24)
plt.savefig("text_length_boxplot.pdf", dpi=600, bbox_inches='tight')
plt.show()




# #calculate mannwhitneyu correlation
# corr, p_value = mannwhitneyu(test_variable_num_list, production_variable_num_list)
# print('mannwhitneyu correlation: %.3f' % corr)
# print('mannwhitneyu p value: %.3f' % p_value)
#
# test_argument_type_dict = Counter(test_argument_type_list)
# production_argument_type_dict = Counter(production_argument_type_list)
#
# print(len(test_argument_type_list))
# print(test_argument_type_dict)
# print(len(production_argument_type_list))
# print(production_argument_type_dict)

