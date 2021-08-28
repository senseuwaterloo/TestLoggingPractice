import os
import pandas as pd
import re
from scipy.stats import mannwhitneyu

from utils import cliffsDelta

log_csv = pd.read_csv('path_to_log_variable_update.csv')
# verbosity_list = ["INFO", "WARN", "TRACE", "ERROR", "DEBUG"]
info_log_df = log_csv[log_csv["verbosity_type"] == "INFO"]
warn_log_df = log_csv[log_csv["verbosity_type"] == "WARN"]
trace_log_df = log_csv[log_csv["verbosity_type"] == "TRACE"]
error_log_df = log_csv[log_csv["verbosity_type"] == "ERROR"]
debug_log_df = log_csv[log_csv["verbosity_type"] == "DEBUG"]
logging_loc_df = pd.concat([info_log_df, warn_log_df, trace_log_df, error_log_df, debug_log_df], axis=0)

studied_projects = ["hadoop", "hbase", "hive", "openmeetings", "tomcat", "ant", "xmlgraphics-fop", "jmeter",
                    "creadur-rat", "maven", "activemq", "empire-db", "karaf", "log4j", "lucene-solr", "mahout", "mina",
                    "pig", "pivot", "struts", "zookeeper"]
pattern = '^[Mm]ock|[Mm]ock$|.*[Tt]est.*'

total_test_variable_number = []
total_production_variable_number = []
total_test_text_length = []
total_production_text_length = []

for project in studied_projects:
    print(project)
    each_project_df = logging_loc_df[logging_loc_df['file_path'].str.contains("/Users/holen/DegreeProject/VCS/mstracker_total/" + project + "/")]
    test_variable_num_list = []
    production_variable_num_list = []
    test_text_length_list = []
    production_text_length_list = []
    # test_argument_type_list = []
    # production_argument_type_list = []
    for index, row in each_project_df.iterrows():

        file_path = logging_loc_df.at[index, "file_path"]
        file_name = os.path.basename(file_path)
        match = re.search(pattern, file_name)

        var_num = row["variable_number"]
        text_length = row["text_length"]
        argument_type = row["argument_type"]

        if match is not None:
            test_variable_num_list.append(var_num)
            test_text_length_list.append(text_length)
            total_test_variable_number.append(var_num)
            total_test_text_length.append(text_length)
        else:
            production_variable_num_list.append(var_num)
            production_text_length_list.append(text_length)
            total_production_variable_number.append(var_num)
            total_production_text_length.append(text_length)

    stat, p = mannwhitneyu(test_variable_num_list, production_variable_num_list)
    print('variable:' + 'Statistics=%.3f, p=%.10f' % (stat, p))
    if p <= 0.05:
        d, res = cliffsDelta.cliffsDelta(production_variable_num_list, test_variable_num_list)
        print(d)
        print(res)

    stat, p = mannwhitneyu(test_text_length_list, production_text_length_list)
    print('text:' + 'Statistics=%.3f, p=%.10f' % (stat, p))
    if p <= 0.05:
        d, res = cliffsDelta.cliffsDelta(production_text_length_list, test_text_length_list)
        print(d)
        print(res)

stat, p = mannwhitneyu(total_test_variable_number, total_production_variable_number)
print('total variable:' + 'Statistics=%.3f, p=%.10f' % (stat, p))
if p <= 0.05:
    d, res = cliffsDelta.cliffsDelta(total_test_variable_number, total_production_variable_number)
    print(d)
    print(res)

stat, p = mannwhitneyu(total_test_text_length, total_production_text_length)
print('total text:' + 'Statistics=%.3f, p=%.10f' % (stat, p))
if p <= 0.05:
    d, res = cliffsDelta.cliffsDelta(total_test_text_length, total_production_text_length)
    print(d)
    print(res)



