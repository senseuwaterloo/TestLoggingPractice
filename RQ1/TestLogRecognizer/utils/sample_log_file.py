import csv
import os
import shutil
import random
import pandas as pd
from collections import Counter


def sample_one_log_per_file():
    log_csv = pd.read_csv('../docs/test_logs_v3.csv')
    log_files = log_csv['file_path'].to_list()
    unique_file_list = list(Counter(log_files).keys())
    per_sample_for_all_files = []
    for each_file in unique_file_list:
        per_file_df = log_csv[log_csv.file_path == each_file]
        random_one_log = per_file_df.sample()
        per_sample_for_all_files.append(random_one_log)

    sampled_log_lines = random.sample(per_sample_for_all_files, 385)

    with open('../docs/sample_one_log_per_file.csv', 'a') as f:
        for df in sampled_log_lines:
            df.to_csv(f, header=False)
            # f.write("\n")

    # fields = ['subject', 'file_path', 'line_number', 'content']
    # with open('../docs/per_sample_for_all_files.csv', 'w') as f:
    #     # using csv.writer method from CSV package
    #     write = csv.writer(f)
    #     write.writerow(fields)
    #     write.writerows(per_sample_for_all_files)


def sample_log_lines():
    log_csv = pd.read_csv('../docs/test_logs_v3.csv')
    log_files = log_csv['file_path'].to_list()
    unique_list = Counter(log_files).keys()
    print(len(unique_list))

    # util included: total 2205 files, need 327 sample
    # util not included: 904 files

    sample_files = random.sample(unique_list, 327)
    print(sample_files)
    sampled_logs = log_csv[log_csv.file_path.isin(sample_files)]
    # file = open('../docs/sampled_test_logs.csv', 'w', newline='')
    sampled_logs.to_csv('../docs/sampled_test_logs_v2.csv')

    # with file:
    #     # identifying header
    #     header = ['subject', 'file_path', 'line_number', 'content']
    #     writer = csv.writer(file)
    #     # writing data row-wise into the csv file
    #     writer.writerow(header)
    #     writer.writerows(rows)

    sampled_log_csv = pd.read_csv('../docs/sampled_test_logs_v2.csv')
    sampled_file_path = sampled_log_csv['file_path'].to_list()
    unique_sample_list = Counter(sampled_file_path).keys()
    print(len(unique_sample_list))


def copy_sampled_files():
    sampled_log_csv = pd.read_csv('../docs/sample_one_log_per_file.csv')
    subjects = sampled_log_csv['subject'].to_list()
    unique_subjects = Counter(subjects).keys()
    parent_dir = "/Users/holen/Desktop/sample_log_files/"
    for subject in unique_subjects:
        logs_per_subject = sampled_log_csv[sampled_log_csv.subject == subject]
        file_path_list = logs_per_subject['file_path'].to_list()
        unique_file_path_list = Counter(file_path_list).keys()
        dest_path = os.path.join(parent_dir, str(subject))
        # os.mkdir(dest_path)
        for file_path in unique_file_path_list:
            shutil.copy2(file_path, dest_path)


def split_sample_files():
    sampled_log_csv = pd.read_csv('../docs/sample_one_log_per_file.csv')
    sampled_file_path = sampled_log_csv['file_path'].to_list()
    unique_sample_list = Counter(sampled_file_path).keys()
    random_file_path_list = list(unique_sample_list)
    random.shuffle(random_file_path_list)
    final_list = []
    for item in random_file_path_list:
        tmp_path = item.replace("/Users/holen/DegreeProject/mstracker-RQ3/", "")
        tmp_split_list = tmp_path.split("/")
        subject_name = tmp_split_list[0]
        file_name = tmp_split_list[-1]
        per_file_df = sampled_log_csv[sampled_log_csv.file_path == item]
        test_log_line_numbers = per_file_df['line_number'].to_list()
        git_file_path = "https://github.com/senseconcordia/sampleloglines/tree/master/" + str(subject_name) + "/" + file_name
        csv_file_name = file_name.replace(".txt", "")
        test_log_lines = "https://github.com/senseconcordia/sampleloglines/tree/master/test-log/" + str(subject_name) + "/" + csv_file_name + ".csv"
        print((subject_name, git_file_path, test_log_line_numbers))
        final_list.append((subject_name, git_file_path, test_log_lines, test_log_line_numbers))


    fields = ['subject', 'file', 'test_log_line', 'line_number']
    with open('../docs/test_log_line_sample.csv', 'w') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(final_list)


def split_only_test_files():
    sampled_log_csv = pd.read_csv('../docs/sample_one_log_per_file.csv')
    sampled_file_path = sampled_log_csv['file_path'].to_list()
    unique_file_list = list(Counter(sampled_file_path).keys())
    parent_dir = "/Users/holen/Desktop/sample_log_files/test-log/"
    for item in unique_file_list:
        per_file_df = sampled_log_csv[sampled_log_csv.file_path == item]
        number_content_df = per_file_df[['line_number', 'content']]

        tmp_path = item.replace("/Users/holen/DegreeProject/mstracker-RQ3/", "")
        tmp_split_list = tmp_path.split("/")
        subject_name = tmp_split_list[0]
        file_name = tmp_split_list[-1]
        file_name = file_name.replace(".txt", "")
        dest_path = os.path.join(parent_dir, str(subject_name))
        number_content_df.to_csv(dest_path + "/" + file_name + ".csv")




# https://github.com/senseconcordia/samplelogfiles
# https://github.com/senseconcordia/samplelogfiles/tree/master/test-log/


if __name__ == "__main__":
    # sample_log_lines()
    # copy_sampled_files()
    split_sample_files()
    # split_only_test_files()
    # sample_one_log_per_file()




