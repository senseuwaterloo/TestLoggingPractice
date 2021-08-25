import re

from Models.LoCode import LoCode
from Utils import BashUtil
from Profilers import XmlFileProfiler
from Models import Config

CLOC_COMMAND = Config.get_cloc_command()


def get_java_sloc(path: str, commit_id=None):
    return get_java_loc(path, commit_id).code_num


def get_test_java_sloc(path: str, commit_id=None):
    return get_test_java_loc(path, commit_id).code_num


def get_production_java_sloc(path: str, commit_id=None):
    return get_production_java_loc(path, commit_id).code_num


def get_java_loc(path: str, commit_id=None):
    if commit_id is None:
        output = BashUtil.run(CLOC_COMMAND + " --include-lang=Java '{}'".format(path))
    else:
        output = BashUtil.run(CLOC_COMMAND + " --include-lang=Java '{}' {}".format(path, commit_id), cwd=path)

    result = get_loc_object(output)
    return result


def get_test_java_loc(path: str, commit_id=None):
    if commit_id is None:
        # output = BashUtil.run(
        #     "cloc --include-lang=Java --match-d='/(test|JUnit)/' " +
        #     "--match-f='^[Tt]est|^[Mm]ock|[Tt]est$|[Tt]ests$|[Tt]estCase$|[Mm]ock$' '{}'".format(path))
        output = BashUtil.run(
            CLOC_COMMAND + " --include-lang=Java --match-f='^[Mm]ock|[Mm]ock$|.*[Tt]est.*' '{}'".format(path))
    else:
        # output = BashUtil.run(
        #     "cloc --include-lang=Java --match-d='/(test|JUnit)/' " +
        #     "--match-f='^[Tt]est|^[Mm]ock|[Tt]est$|[Tt]ests$|[Tt]estCase$|[Mm]ock$' '{}' '{}'".format(
        #         path, commit_id), cwd=path)
        output = BashUtil.run(
            CLOC_COMMAND + " --include-lang=Java --match-f='^[Mm]ock|[Mm]ock$|.*[Tt]est.*' '{}' '{}'".format(
                path, commit_id), cwd=path)

    result = get_loc_object(output)
    return result


def get_production_java_loc(path: str, commit_id=None):
    if commit_id is None:
        # output = BashUtil.run(
        #     "cloc --include-lang=Java --not-match-d='/(test|JUnit)/' " +
        #     "--not-match-f='^[Tt]est|^[Mm]ock|[Tt]est$|[Tt]ests$|[Tt]estCase$|[Mm]ock$' '{}'".format(path))
        output = BashUtil.run(
            CLOC_COMMAND + " --include-lang=Java --not-match-f='^[Mm]ock|[Mm]ock$|.*[Tt]est.*' '{}'".format(path))
    else:
        # output = BashUtil.run(
        #     "cloc --include-lang=Java --not-match-d='/(test|JUnit)/' " +
        #     "--not-match-f='^[Tt]est|^[Mm]ock|[Tt]est$|[Tt]ests$|[Tt]estCase$|[Mm]ock$' '{}' '{}'".format(
        #         path, commit_id), cwd=path)
        output = BashUtil.run(
            CLOC_COMMAND + " --include-lang=Java --not-match-f='^[Mm]ock|[Mm]ock$|.*[Tt]est.*' '{}' '{}'".format(
                path, commit_id), cwd=path)

    result = get_loc_object(output)
    return result


def get_loc_object(output):
    pattern = '.*Java.*'
    m = re.search(pattern, output)
    result = LoCode()
    if m is not None:
        line = m.group(0)
        result = _convert_cloc_line_to_object(line)

    return result


def _convert_cloc_line_to_object(line) -> LoCode:
    split_line = line.strip().split()
    files_num = int(split_line[1])
    blank_num = int(split_line[2])
    comment_num = int(split_line[3])
    code_num = int(split_line[4])
    return LoCode(files_num, blank_num, comment_num, code_num)


def get_logging_loc_of_repo(path: str):
    total_result, total_assert_result, total_print_result, total_log_result, \
        test_result, test_assert_result, test_print_result, test_log_result, \
        production_result, production_assert_result, production_print_result, \
        production_log_result, total_verbosity_list, test_verbosity_list, production_verbosity_list\
        = XmlFileProfiler.get_logging_calls_xml_of_repo(path)

    return len(total_result), len(total_assert_result), len(total_print_result), len(total_log_result), \
        len(test_result), len(test_assert_result), len(test_print_result), len(test_log_result), \
        len(production_result), len(production_assert_result), len(production_print_result), len(production_log_result),\
        total_verbosity_list[0], total_verbosity_list[1], total_verbosity_list[2], total_verbosity_list[3], total_verbosity_list[4],\
        test_verbosity_list[0], test_verbosity_list[1], test_verbosity_list[2], test_verbosity_list[3], test_verbosity_list[4],\
        production_verbosity_list[0], production_verbosity_list[1], production_verbosity_list[2], production_verbosity_list[3], production_verbosity_list[4]


def get_logging_loc_of_file(path: str):
    total_file_result, assert_file_result, print_file_result, log_file_result \
        = XmlFileProfiler.get_logging_calls_xml_of_file(path)
    return len(total_file_result), len(assert_file_result), len(print_file_result), len(log_file_result)


def get_java_loc_diff(old_path: str, new_path: str):
    output = BashUtil.run(CLOC_COMMAND + " --diff --diff-timeout 99999 '{}' '{}'".format(old_path, new_path))
    pattern = r'.*Java(\s.*){4}'
    m = re.search(pattern, output)
    same = LoCode()
    modified = LoCode()
    added = LoCode()
    removed = LoCode()

    if m is not None:
        lines = m.group(0).split('\n')
        lines.pop(0)
        for line in lines:
            # print(line)
            line_type = line.split()[0]
            loc_detail = _convert_cloc_line_to_object(line)
            if line_type == 'same':
                same = loc_detail
            elif line_type == 'modified':
                modified = loc_detail
            elif line_type == 'added':
                added = loc_detail
            elif line_type == 'removed':
                removed = loc_detail

    return {
        'same': same,
        'modified': modified,
        'added': added,
        'removed': removed
    }
