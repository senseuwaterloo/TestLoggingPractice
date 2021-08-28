import glob
import re
import csv


def get_test_log_lines(text_file_path: str, subject_name: str):
    file_result = []
    with open(text_file_path) as f:
        not_test_log_line_num = 0
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if is_log_line(line):
                general_test_file_name = text_file_path.split("/")[-1]
                general_test_file_name = general_test_file_name.replace(".txt", "")
                if is_test_log_line(line, subject_name, general_test_file_name):
                    file_result.append((subject_name, text_file_path, str(line_num), line))
                    print((subject_name, text_file_path, str(line_num), line))
                else:
                    not_test_log_line_num = not_test_log_line_num + 1

    if len(file_result) > 0 and not_test_log_line_num > 0:
        return file_result
    else:
        return None


def is_test_log_line(candidate_line, subject_name: str, general_test_file_name):
    # Activemq
    activemq_pattern = r']\s-\s\w+\s+\w+\s+-'
    # Fop
    fop_pattern = r'AM\s[a-zA-Z0-9.$]+\s|PM\s[a-zA-Z0-9.$]+\s'
    # Karaf
    karaf_pattern = r'AM\s[a-zA-Z0-9.$]+\s|PM\s[a-zA-Z0-9.$]+\s|\}[a-zA-Z\s0-9.($]+java'
    # Hadoop
    hadoop_pattern = r',\d{3}\s+\w+\s+\w+.[a-zA-Z0-9.]+\s+[a-zA-Z.():0-9]+|]\s+\w+.[a-zA-Z0-9.]+\s+[a-zA-Z.():0-9]+'
    # Hbase
    hbase_pattern = r']\s+[a-zA-Z.]+\(\d+\)|]\s+[a-zA-Z.]+:|]\s+[a-zA-Z.()0-9$]+:|\][a-zA-Z.\s(0-9:]+\)'
    # Hive
    hive_pattern = r']\s+\w+.[a-zA-Z.0-9]+:'
    # openmeetings
    openmeetings_pattern = r'\]\s+\w+\s+\w+.[a-zA-Z0-9.]+\s-'
    # pig
    pig_pattern = r'\]\s+\w+\s+\w+.[a-zA-Z0-9.$]+\s+-'
    # struts
    struts_pattern = r']\s\w+.[a-zA-Z0-9.$]+\s+[a-zA-Z.():0-9]+|PM\s[a-zA-Z0-9.$]+\s'
    # tomcat
    tomcat_pattern = r']\s+\w+.[a-zA-Z.0-9]+\s|AM\s[a-zA-Z0-9.$]+\s'
    # zookeeper
    zookeeper_pattern = r'\[[a-zA-Z0-9:$-]+@\d+\]|\$\w+@\d+|\:\w+@\d+'

    if subject_name == "activemq-master":
        matches = re.findall(activemq_pattern, candidate_line)
    elif subject_name == "xmlgraphics-fop-trunk":
        matches = re.findall(fop_pattern, candidate_line)
    elif subject_name == "karaf-master":
        matches = re.findall(karaf_pattern, candidate_line)
    elif subject_name == "hadoop-trunk":
        matches = re.findall(hadoop_pattern, candidate_line)
    elif subject_name == "hbase-master":
        matches = re.findall(hbase_pattern, candidate_line)
    elif subject_name == "hive-master":
        matches = re.findall(hive_pattern, candidate_line)
    elif subject_name == "openmeetings-master":
        matches = re.findall(openmeetings_pattern, candidate_line)
    elif subject_name == "pig-trunk":
        matches = re.findall(pig_pattern, candidate_line)
    elif subject_name == "struts-master":
        matches = re.findall(struts_pattern, candidate_line)
    elif subject_name == "tomcat-master":
        matches = re.findall(tomcat_pattern, candidate_line)
    else:
        # print(candidate_line)
        matches = re.findall(zookeeper_pattern, candidate_line)

    # print(subject_name)
    # print(matches)

    if len(matches) > 0:
        for each_match in matches:
            if subject_name == "pig-trunk":
                test_name = general_test_file_name.split(".")[-1]
            elif subject_name == "tomcat-master":
                test_name = general_test_file_name.split(".")[-2]
            else:
                test_name = general_test_file_name.split(".")[-1]
                test_name = test_name.split("-")[0]

            if test_name in each_match:
                return True

    return False


def is_log_line(candidate_line):
    # Activemq hadoop hbase pig struts zookeeper
    first_time_pattern = r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}'
    # Fop Karaf
    second_time_pattern = r'^Mar\s\d{2},\s\d{4}\s\d+:\d{2}:\d{2}\s\w{2}'
    # Hive
    third_time_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2},\d{3}'
    # Openmeetings
    fourth_time_pattern = r'^\d{2}:\d{2}:\d{2}.\d{3}'
    # Tomcat
    fifth_time_pattern = r'^\d{2}-Mar-\d{4}\s\d{2}:\d{2}:\d{2}.\d{3}'
    match_result = re.compile("(%s|%s|%s|%s|%s)" % (first_time_pattern, second_time_pattern, third_time_pattern,
                                                    fourth_time_pattern, fifth_time_pattern)).match(candidate_line)

    if match_result:
        return True


def get_txt_in_surefire(subject_path: str):
    all_txt_files = [f for f in glob.glob(subject_path + "/" + "**/*.txt", recursive=True)]
    surefire_txt_files = [f for f in all_txt_files if "surefire-reports" in f]
    return surefire_txt_files


def get_pig_txt(subject_path: str):
    output_files = [f for f in glob.glob(subject_path + "/build/test/logs" + "**/*.txt", recursive=True)]
    return output_files


def get_tomcat_txt(subject_path: str):
    output_files = [f for f in glob.glob(subject_path + "/output/build/logs" + "**/*.txt", recursive=True)]
    return output_files


if __name__ == "__main__":
    folder = '/Users/holen/DegreeProject/mstracker-RQ3'
    valid_subjects = ["activemq-master", "xmlgraphics-fop-trunk", "hadoop-trunk", "hbase-master", "hive-master",
                      "karaf-master", "openmeetings-master", "pig-trunk", "struts-master", "tomcat-master",
                      "zookeeper-master"]
    final_result = []
    # test_subjects = ["zookeeper-master"]
    for item in valid_subjects:
        valid_subject_path = folder + "/" + item
        if item == "pig-trunk":
            log_txt_files = get_pig_txt(valid_subject_path)
        elif item == "tomcat-master":
            log_txt_files = get_tomcat_txt(valid_subject_path)
        else:
            log_txt_files = get_txt_in_surefire(valid_subject_path)

        for file in log_txt_files:
            result = get_test_log_lines(file, item)
            if result is not None:
                final_result.extend(result)

    print(len(final_result))
    # util test included 1595574
    # only in the test indicated in the test name: 691310

    file = open('../docs/test_logs_v3.csv', 'w', newline='')
    with file:
        # identifying header
        header = ['subject', 'file_path', 'line_number', 'content']
        writer = csv.writer(file)
        # writing data row-wise into the csv file
        writer.writerow(header)
        writer.writerows(final_result)

