from lxml import etree

from conf import config
from models.log import LogVerbosityType, Log
from models.repo import Repo
import models.file
from utils import git_util, loc_util, file_util, xml_util


def detect_project(repo: Repo):
    path = config.get_repo_local_path_with_project_name(repo.repo_name)

    local_last_commit_date = git_util.get_last_commit_date(path)
    if repo.last_commit_date is None or local_last_commit_date > repo.last_commit_date:
        repo.files_num = git_util.get_files_num(path)
        repo.commits_num = git_util.get_commits_num(path)
        repo.last_commit_date = local_last_commit_date
        repo.first_commit_date = git_util.get_first_commit_date(path)
        repo.authors_num = git_util.get_authors_num(path)
        repo.sloc = loc_util.get_java_sloc(path)
        repo.test_sloc = loc_util.get_test_java_sloc(path)
        repo.production_sloc = loc_util.get_production_java_sloc(path)
        repo.monitoring_loc, repo.assert_caller_loc, repo.print_caller_loc, repo.log_caller_loc, \
        repo.test_monitoring_loc, repo.test_assert_caller_loc, repo.test_print_caller_loc, \
        repo.test_log_caller_loc, repo.production_monitoring_loc, repo.production_assert_caller_loc, \
        repo.production_print_caller_loc, repo.production_log_caller_loc, repo.total_trace_level_num, \
        repo.total_debug_level_num, repo.total_info_level_num, repo.total_warn_level_num, \
        repo.total_error_level_num, repo.test_trace_level_num, repo.test_debug_level_num, \
        repo.test_info_level_num, repo.test_warn_level_num, repo.test_error_level_num, \
        repo.production_trace_level_num, repo.production_debug_level_num, repo.production_info_level_num, \
        repo.production_warn_level_num, repo.production_error_level_num = loc_util.get_logging_loc_of_repo(path)
        repo.save()

    java_file_list = file_util.get_all_java_files(path)
    for each_java_file_path in java_file_list:
        each_java_file = str(each_java_file_path)
        file_sloc = loc_util.get_java_sloc(each_java_file)
        file_monitoring_loc, file_assert_caller_loc, file_print_caller_loc, file_log_caller_loc, \
        file_trace_level_num, file_debug_level_num, file_info_level_num, file_warn_level_num, file_error_level_num = loc_util.get_logging_loc_of_file(each_java_file)
        is_test_file = file_util.is_test_file(each_java_file)

        file_obj = models.file.File.create(repo=repo, file_path=each_java_file, sloc=file_sloc, monitoring_loc=file_monitoring_loc,
                                           assert_caller_loc=file_assert_caller_loc, print_caller_loc=file_print_caller_loc,
                                           log_caller_loc=file_log_caller_loc, trace_level_num=file_trace_level_num,
                                           debug_level_num=file_debug_level_num, info_level_num=file_info_level_num,
                                           warn_level_num=file_warn_level_num, error_level_num=file_error_level_num,
                                           is_test_file=is_test_file)
        file_obj.save()

        total_logging_call, _, _, _, _, _, _, _, _ = xml_util.get_logging_calls_xml_of_file(each_java_file)
        if len(total_logging_call) != 0:
            for logging_call in total_logging_call:
                call_text = xml_util.transform_xml_str_to_code(etree.tostring(logging_call).decode('utf-8'))
                argument_type = xml_util.get_logging_argument_type(logging_call)
                _, verbosity_type = get_log_content_component(call_text)
                argument_number = xml_util.get_logging_argument_number(logging_call)

                log_obj = Log.create(file=file_obj, file_path=each_java_file, content=call_text,
                                     verbosity_type=verbosity_type, argument_type=argument_type,
                                     variable_number= argument_number)
                log_obj.save()


def get_log_content_component(content: str):
    caller_method = content.split('(')[0]
    caller_method = ''.join(caller_method.split())
    if '.' in caller_method:
        verbosity = caller_method.split('.')[-1]
        caller_object = caller_method.rsplit('.', 1)[0]
    else:
        caller_object = caller_method
        verbosity = caller_method
    verbosity_type = get_verbosity_type(caller_object, verbosity)
    arguments_str = content[len(caller_method) + 1: -1]
    # arguments = arguments_str.split(',')
    return caller_object, verbosity_type


def get_verbosity_type(caller: str, verbosity: str):
    if caller == 'System.err':
        return LogVerbosityType.ERROR
    if caller == 'System.out':
        return LogVerbosityType.INFO

    verbosity_type = None
    if verbosity is not None:
        lowercase_verbosity = verbosity.lower()
        if lowercase_verbosity in ['v', 'verbose', 'logv', 'logverbose', 'verboselog', 'log_v', 'trace']:
            verbosity_type = LogVerbosityType.TRACE
        elif lowercase_verbosity in ['d', 'debug', 'fine', 'logd', 'logdebug', 'debuglog', 'log_d']:
            verbosity_type = LogVerbosityType.DEBUG
        elif lowercase_verbosity in ['i', 'info', 'log', 'logi', 'logln', 'loginfo', 'infolog', 'log_i',
                                     'print', 'printf', 'println', 'printlog', 'logmessage', 'logcommon',
                                     'logAuditEvent', 'logDnsLookup']:
            verbosity_type = LogVerbosityType.INFO
        elif lowercase_verbosity in ['w', 'warn', 'warning', 'logw', 'logwarning', 'logwarn', 'warnlog',
                                     'warninglog', 'log_w']:
            verbosity_type = LogVerbosityType.WARN
        elif lowercase_verbosity in ['e', 'error', 'severe', 'fatal', 'wtf', 'loge', 'logerror', 'logsevere',
                                     'logfatal',
                                     'logwtf', 'logexception', 'errlog', 'errorlog', 'severelog', 'fatallog', 'log_e']:
            verbosity_type = LogVerbosityType.ERROR

    return verbosity_type
