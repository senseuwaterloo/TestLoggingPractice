import logging

from lxml import etree

from Models import Commit
from Models.Log import LogChangeType, Log
from Utils import FileUtil, LocUtil
from Profilers import XmlFileProfiler
from Profilers import LogProfiler
from Profilers import MethodProfiler

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


def diff_profiler(git_repo, commit_diff, head_commit_db: Commit):
    head_commit_sha = head_commit_db.commit_id
    head_commit_git = git_repo.commit(head_commit_sha)
    head_commit_db.committer_name = head_commit_git.committer.name
    head_commit_db.committer_email = head_commit_git.committer.email
    head_commit_db.committed_date = head_commit_git.committed_datetime
    head_commit_db.author_name = head_commit_git.author.name
    head_commit_db.author_email = head_commit_git.author.email
    head_commit_db.authored_date = head_commit_git.authored_datetime
    head_commit_db.message = head_commit_git.message

    repo_added_sloc, repo_deleted_sloc, repo_updated_sloc = 0, 0, 0
    repo_added_test_sloc, repo_deleted_test_sloc, repo_updated_test_sloc = 0, 0, 0
    repo_added_production_sloc, repo_deleted_production_sloc, repo_updated_production_sloc = 0, 0, 0

    repo_added_monitoring_loc, repo_deleted_monitoring_loc, repo_updated_monitoring_loc = 0, 0, 0
    repo_added_test_monitoring_loc, repo_deleted_test_monitoring_loc, repo_updated_test_monitoring_loc = 0, 0, 0
    repo_added_production_monitoring_loc, repo_deleted_production_monitoring_loc, repo_updated_production_monitoring_loc = 0, 0, 0

    repo_added_log_caller_loc, repo_deleted_log_caller_loc, repo_updated_log_caller_loc = 0, 0, 0
    repo_added_test_log_caller_loc, repo_deleted_test_log_caller_loc, repo_updated_test_log_caller_loc = 0, 0, 0
    repo_added_production_log_caller_loc, repo_deleted_production_log_caller_loc, repo_updated_production_log_caller_loc = 0, 0, 0

    repo_added_print_caller_loc, repo_deleted_print_caller_loc, repo_updated_print_caller_loc = 0, 0, 0
    repo_added_test_print_caller_loc, repo_deleted_test_print_caller_loc, repo_updated_test_print_caller_loc = 0, 0, 0
    repo_added_production_print_caller_loc, repo_deleted_production_print_caller_loc, repo_updated_production_print_caller_loc = 0, 0, 0

    repo_added_assert_caller_loc, repo_deleted_assert_caller_loc, repo_updated_assert_caller_loc = 0, 0, 0
    repo_added_test_assert_caller_loc, repo_deleted_test_assert_caller_loc, repo_updated_test_assert_caller_loc = 0, 0, 0
    repo_added_production_assert_caller_loc, repo_deleted_production_assert_caller_loc, repo_updated_production_assert_caller_loc = 0, 0, 0

    for file_diff in commit_diff:

        if file_diff.change_type == 'A':
            file_sloc, test_file_sloc, production_file_sloc, \
                file_monitoring_loc, test_file_monitoring_loc, production_file_monitoring_loc, \
                file_log_caller_loc, test_file_log_caller_loc, production_file_log_caller_loc, \
                file_print_caller_loc, test_file_print_caller_loc, production_file_print_caller_loc, \
                file_assert_caller_loc, test_file_assert_caller_loc, production_file_assert_caller_loc\
                = handle_added_file(file_diff, head_commit_db)
            repo_added_sloc += file_sloc
            repo_added_test_sloc += test_file_sloc
            repo_added_production_sloc += production_file_sloc
            repo_added_monitoring_loc += file_monitoring_loc
            repo_added_test_monitoring_loc += test_file_monitoring_loc
            repo_added_production_monitoring_loc += production_file_monitoring_loc
            repo_added_log_caller_loc += file_log_caller_loc
            repo_added_test_log_caller_loc += test_file_log_caller_loc
            repo_added_production_log_caller_loc += production_file_log_caller_loc
            repo_added_print_caller_loc += file_print_caller_loc
            repo_added_test_print_caller_loc += test_file_print_caller_loc
            repo_added_production_print_caller_loc += production_file_print_caller_loc
            repo_added_assert_caller_loc += file_assert_caller_loc
            repo_added_test_assert_caller_loc += test_file_assert_caller_loc
            repo_added_production_assert_caller_loc += production_file_assert_caller_loc

        elif file_diff.change_type == 'D':
            file_sloc, test_file_sloc, production_file_sloc, \
                file_monitoring_loc, test_file_monitoring_loc, production_file_monitoring_loc, \
                file_log_caller_loc, test_file_log_caller_loc, production_file_log_caller_loc, \
                file_print_caller_loc, test_file_print_caller_loc, production_file_print_caller_loc, \
                file_assert_caller_loc, test_file_assert_caller_loc, production_file_assert_caller_loc \
                = handle_deleted_file(file_diff, head_commit_db)
            repo_deleted_sloc += file_sloc
            repo_deleted_test_sloc += test_file_sloc
            repo_deleted_production_sloc += production_file_sloc
            repo_deleted_monitoring_loc += file_monitoring_loc
            repo_deleted_test_monitoring_loc += test_file_monitoring_loc
            repo_deleted_production_monitoring_loc += production_file_monitoring_loc
            repo_deleted_log_caller_loc += file_log_caller_loc
            repo_deleted_test_log_caller_loc += test_file_log_caller_loc
            repo_deleted_production_log_caller_loc += production_file_log_caller_loc
            repo_deleted_print_caller_loc += file_print_caller_loc
            repo_deleted_test_print_caller_loc += test_file_print_caller_loc
            repo_deleted_production_print_caller_loc += production_file_print_caller_loc
            repo_deleted_assert_caller_loc += file_assert_caller_loc
            repo_deleted_test_assert_caller_loc += test_file_assert_caller_loc
            repo_deleted_production_assert_caller_loc += production_file_assert_caller_loc
            '''or (file_diff.change_type.startswith('R') and file_diff.a_blob != file_diff.b_blob)'''
        elif file_diff.change_type == 'M' or \
                (file_diff.change_type.startswith('R') and file_diff.a_blob != file_diff.b_blob):
            file_added_sloc, file_deleted_sloc, file_updated_sloc, \
                file_added_monitoring_loc, file_deleted_monitoring_loc, file_updated_monitoring_loc, \
                file_added_log_loc, file_deleted_log_loc, file_updated_log_loc, \
                file_added_print_loc, file_deleted_print_loc, file_updated_print_loc, \
                file_added_assert_loc, file_deleted_assert_loc, file_updated_assert_loc\
                = handle_updated_file(file_diff, head_commit_db)

            repo_added_sloc += file_added_sloc
            repo_deleted_sloc += file_deleted_sloc
            repo_updated_sloc += file_updated_sloc

            repo_added_monitoring_loc += file_added_monitoring_loc
            repo_deleted_monitoring_loc += file_deleted_monitoring_loc
            repo_updated_monitoring_loc += file_updated_monitoring_loc

            repo_added_log_caller_loc += file_added_log_loc
            repo_deleted_log_caller_loc += file_deleted_log_loc
            repo_updated_log_caller_loc += file_updated_log_loc

            repo_added_print_caller_loc += file_added_print_loc
            repo_deleted_print_caller_loc += file_deleted_print_loc
            repo_updated_print_caller_loc += file_updated_print_loc

            repo_added_assert_caller_loc += file_added_assert_loc
            repo_deleted_assert_caller_loc += file_deleted_assert_loc
            repo_updated_assert_caller_loc += file_updated_assert_loc

            if FileUtil.is_test_file(file_diff.a_path) or FileUtil.is_test_file(file_diff.b_path):
                repo_added_test_sloc += file_added_sloc
                repo_deleted_test_sloc += file_deleted_sloc
                repo_updated_test_sloc += file_updated_sloc

                repo_added_test_monitoring_loc += file_added_monitoring_loc
                repo_deleted_test_monitoring_loc += file_deleted_monitoring_loc
                repo_updated_test_monitoring_loc += file_updated_monitoring_loc

                repo_added_test_log_caller_loc += file_added_log_loc
                repo_deleted_test_log_caller_loc += file_deleted_log_loc
                repo_updated_test_log_caller_loc += file_updated_log_loc

                repo_added_test_print_caller_loc += file_added_print_loc
                repo_deleted_test_print_caller_loc += file_deleted_print_loc
                repo_updated_test_print_caller_loc += file_updated_print_loc

                repo_added_test_assert_caller_loc += file_added_assert_loc
                repo_deleted_test_assert_caller_loc += file_deleted_assert_loc
                repo_updated_test_assert_caller_loc += file_updated_assert_loc

            else:
                repo_added_production_sloc += file_added_sloc
                repo_deleted_production_sloc += file_deleted_sloc
                repo_updated_production_sloc += file_updated_sloc

                repo_added_production_monitoring_loc += file_added_monitoring_loc
                repo_deleted_production_monitoring_loc += file_deleted_monitoring_loc
                repo_updated_production_monitoring_loc += file_updated_monitoring_loc

                repo_added_production_log_caller_loc += file_added_log_loc
                repo_deleted_production_log_caller_loc += file_deleted_log_loc
                repo_updated_production_log_caller_loc += file_updated_log_loc

                repo_added_production_print_caller_loc += file_added_print_loc
                repo_deleted_production_print_caller_loc += file_deleted_print_loc
                repo_updated_production_print_caller_loc += file_updated_print_loc

                repo_added_production_assert_caller_loc += file_added_assert_loc
                repo_deleted_production_assert_caller_loc += file_deleted_assert_loc
                repo_updated_production_assert_caller_loc += file_updated_assert_loc


    # code_churn, sloc_delta = calculate_churn_and_delta(repo_added_sloc, repo_deleted_sloc, repo_updated_sloc)
    # logging_code_churn, logging_loc_delta = \
    #     calculate_churn_and_delta(repo_added_monitoring_loc, repo_deleted_monitoring_loc, repo_updated_monitoring_loc)
    # test_code_churn, test_sloc_delta = \
    #     calculate_churn_and_delta(repo_added_test_sloc, repo_deleted_test_sloc, repo_updated_test_sloc)
    # test_logging_code_churn, test_logging_loc_delta = \
    #     calculate_churn_and_delta(repo_added_test_monitoring_loc, repo_deleted_test_monitoring_loc,
    #                               repo_updated_test_monitoring_loc)
    # production_code_churn, production_sloc_delta = \
    #     calculate_churn_and_delta(repo_added_production_sloc, repo_deleted_production_sloc,
    #                               repo_updated_production_sloc)
    # production_logging_code_churn, production_logging_loc_delta = \
    #     calculate_churn_and_delta(repo_added_production_monitoring_loc, repo_deleted_production_monitoring_loc,
    #                               repo_updated_production_monitoring_loc)

    head_commit_db.added_sloc, head_commit_db.deleted_sloc, head_commit_db.updated_sloc = \
        repo_added_sloc, repo_deleted_sloc, repo_updated_sloc
    head_commit_db.added_test_sloc, head_commit_db.deleted_test_sloc, head_commit_db.updated_test_sloc = \
        repo_added_test_sloc, repo_deleted_test_sloc, repo_updated_test_sloc
    head_commit_db.added_production_sloc, head_commit_db.deleted_production_sloc, head_commit_db.updated_production_sloc\
        = repo_added_production_sloc, repo_deleted_production_sloc, repo_updated_production_sloc

    head_commit_db.added_monitoring_loc, head_commit_db.deleted_monitoring_loc, \
        head_commit_db.updated_monitoring_loc = repo_added_monitoring_loc, repo_deleted_monitoring_loc, \
        repo_updated_monitoring_loc
    head_commit_db.added_test_monitoring_loc, head_commit_db.deleted_test_monitoring_loc, \
        head_commit_db.updated_test_monitoring_loc = repo_added_test_monitoring_loc, \
        repo_deleted_test_monitoring_loc, repo_updated_test_monitoring_loc
    head_commit_db.added_production_monitoring_loc, head_commit_db.deleted_production_monitoring_loc, \
        head_commit_db.updated_production_monitoring_loc = repo_added_production_monitoring_loc, \
        repo_deleted_production_monitoring_loc, repo_updated_production_monitoring_loc

    head_commit_db.added_log_caller_loc, head_commit_db.deleted_log_caller_loc, head_commit_db.updated_log_caller_loc\
        = repo_added_log_caller_loc, repo_deleted_log_caller_loc, repo_updated_log_caller_loc
    head_commit_db.added_test_log_caller_loc, head_commit_db.deleted_test_log_caller_loc, \
        head_commit_db.updated_test_log_caller_loc = repo_added_test_log_caller_loc, \
        repo_deleted_test_log_caller_loc, repo_updated_test_log_caller_loc
    head_commit_db.added_production_log_caller_loc, head_commit_db.deleted_production_log_caller_loc, \
        head_commit_db.updated_production_log_caller_loc = repo_added_production_log_caller_loc, \
        repo_deleted_production_log_caller_loc, repo_updated_production_log_caller_loc

    head_commit_db.added_print_caller_loc, head_commit_db.deleted_print_caller_loc, \
        head_commit_db.updated_print_caller_loc = repo_added_print_caller_loc, repo_deleted_print_caller_loc, \
        repo_updated_print_caller_loc
    head_commit_db.added_test_print_caller_loc, head_commit_db.deleted_test_print_caller_loc, \
        head_commit_db.updated_test_print_caller_loc = \
        repo_added_test_print_caller_loc, repo_deleted_test_print_caller_loc, repo_updated_test_print_caller_loc
    head_commit_db.added_production_print_caller_loc, head_commit_db.deleted_production_print_caller_loc, \
        head_commit_db.updated_production_print_caller_loc = \
        repo_added_production_print_caller_loc, repo_deleted_production_print_caller_loc, \
        repo_updated_production_print_caller_loc

    head_commit_db.added_assert_caller_loc, head_commit_db.deleted_assert_caller_loc, \
        head_commit_db.updated_assert_caller_loc = repo_added_assert_caller_loc, \
        repo_deleted_assert_caller_loc, repo_updated_assert_caller_loc

    head_commit_db.added_test_assert_caller_loc, head_commit_db.deleted_test_assert_caller_loc, \
        head_commit_db.updated_test_assert_caller_loc = \
        repo_added_test_assert_caller_loc, repo_deleted_test_assert_caller_loc, repo_updated_test_assert_caller_loc

    head_commit_db.added_production_assert_caller_loc, head_commit_db.deleted_production_assert_caller_loc, \
        head_commit_db.updated_production_assert_caller_loc = repo_added_production_assert_caller_loc, \
        repo_deleted_production_assert_caller_loc, repo_updated_production_assert_caller_loc



    # head_commit_db.code_churn = code_churn
    # head_commit_db.logging_code_churn = logging_code_churn
    # head_commit_db.test_code_churn = test_code_churn
    # head_commit_db.test_logging_code_churn = test_logging_code_churn
    # head_commit_db.production_code_churn = production_code_churn
    # head_commit_db.production_logging_code_churn = production_logging_code_churn
    head_commit_db.save()

    return repo_added_sloc - repo_deleted_sloc, repo_added_test_sloc - repo_deleted_test_sloc, \
        repo_added_production_sloc - repo_deleted_production_sloc, repo_added_monitoring_loc - repo_deleted_monitoring_loc, \
        repo_added_test_monitoring_loc - repo_deleted_test_monitoring_loc, repo_added_production_monitoring_loc - repo_deleted_production_monitoring_loc, \
        repo_added_log_caller_loc - repo_deleted_log_caller_loc, repo_added_test_log_caller_loc - repo_deleted_test_log_caller_loc, \
        repo_added_production_log_caller_loc - repo_deleted_production_log_caller_loc, repo_added_print_caller_loc - repo_deleted_print_caller_loc, \
        repo_added_test_print_caller_loc - repo_deleted_test_print_caller_loc, repo_added_production_print_caller_loc - repo_deleted_production_print_caller_loc, \
        repo_added_assert_caller_loc - repo_deleted_assert_caller_loc, repo_added_test_assert_caller_loc - repo_deleted_test_assert_caller_loc, \
        repo_added_production_assert_caller_loc - repo_deleted_production_assert_caller_loc


def handle_added_file(file_diff, head_commit_db: Commit):
    return handle_added_or_deleted_file(file_diff.b_path, file_diff.b_blob,
                                        LogChangeType.ADDED_WITH_FILE, head_commit_db)


def handle_deleted_file(file_diff, head_commit_db: Commit):
    return handle_added_or_deleted_file(file_diff.a_path, file_diff.a_blob,
                                        LogChangeType.DELETED_WITH_FILE, head_commit_db)


def handle_updated_file(file_diff, head_commit_db: Commit):
    file_added_sloc, file_deleted_sloc, file_updated_sloc = 0, 0, 0
    file_added_monitoring_loc, file_deleted_monitoring_loc, file_updated_monitoring_loc = 0, 0, 0
    file_added_log_loc, file_deleted_log_loc, file_updated_log_loc = 0, 0, 0
    file_added_print_loc, file_deleted_print_loc, file_updated_print_loc = 0, 0, 0
    file_added_assert_loc, file_deleted_assert_loc, file_updated_assert_loc = 0, 0, 0

    if FileUtil.is_java_file(file_diff.a_path) and FileUtil.is_java_file(file_diff.b_path):
        java_a_file = XmlFileProfiler.generate_java_file_of_blob(file_diff.a_blob)
        java_b_file = XmlFileProfiler.generate_java_file_of_blob(file_diff.b_blob)
        loc_diff = LocUtil.get_java_loc_diff(java_a_file, java_b_file)
        FileUtil.delete_if_exists(java_a_file)
        FileUtil.delete_if_exists(java_b_file)

        file_added_sloc = loc_diff['added'].code_num
        file_deleted_sloc = loc_diff['removed'].code_num
        file_updated_sloc = loc_diff['modified'].code_num

        methods_parent = XmlFileProfiler.get_methods_of_java_blob(file_diff.a_blob)
        methods_head = XmlFileProfiler.get_methods_of_java_blob(file_diff.b_blob)
        file_added_monitoring_loc, file_deleted_monitoring_loc, file_updated_monitoring_loc, \
            file_added_log_loc, file_deleted_log_loc, file_updated_log_loc, \
            file_added_print_loc, file_deleted_print_loc, file_updated_print_loc, \
            file_added_assert_loc, file_deleted_assert_loc, file_updated_assert_loc = \
            MethodProfiler.compare_all_methods(methods_parent, methods_head, file_diff, head_commit_db)

        logger.debug(
            'updated file: {}, added_sloc: {}, deleted_sloc: {}, updated_sloc: {}, added_lolc: {}, deleted_lolc: {}, updated_lolc: {}'.format(
                file_diff.b_path, file_added_sloc, file_deleted_sloc, file_updated_sloc, file_added_monitoring_loc,
                file_deleted_monitoring_loc, file_updated_monitoring_loc
            ))

    return file_added_sloc, file_deleted_sloc, file_updated_sloc, \
        file_added_monitoring_loc, file_deleted_monitoring_loc, file_updated_monitoring_loc, \
        file_added_log_loc, file_deleted_log_loc, file_updated_log_loc, \
        file_added_print_loc, file_deleted_print_loc, file_updated_print_loc, \
        file_added_assert_loc, file_deleted_assert_loc, file_updated_assert_loc


def handle_added_or_deleted_file(file_path, file_blob, change_type, head_commit_db: Commit):
    file_sloc, test_file_sloc, production_file_sloc = 0, 0, 0
    file_monitoring_loc, test_file_monitoring_loc, production_file_monitoring_loc = 0, 0, 0
    file_log_caller_loc, test_file_log_caller_loc, production_file_log_caller_loc = 0, 0, 0
    file_print_caller_loc, test_file_print_caller_loc, production_file_print_caller_loc = 0, 0, 0
    file_assert_caller_loc, test_file_assert_caller_loc, production_file_assert_caller_loc = 0, 0, 0

    if FileUtil.is_java_file(file_path):
        java_file = XmlFileProfiler.generate_java_file_of_blob(file_blob)
        file_sloc = LocUtil.get_java_sloc(java_file)
        file_monitoring_loc, file_assert_caller_loc, file_print_caller_loc, file_log_caller_loc \
            = LocUtil.get_logging_loc_of_file(java_file)
        if FileUtil.is_test_file(file_path):
            test_file_sloc = file_sloc
            test_file_monitoring_loc = file_monitoring_loc
            test_file_assert_caller_loc = file_assert_caller_loc
            test_file_print_caller_loc = file_print_caller_loc
            test_file_log_caller_loc = file_log_caller_loc
        else:
            production_file_sloc = file_sloc
            production_file_monitoring_loc = file_monitoring_loc
            production_file_assert_caller_loc = file_assert_caller_loc
            production_file_print_caller_loc = file_print_caller_loc
            production_file_log_caller_loc = file_log_caller_loc

        FileUtil.delete_if_exists(java_file)

        if not head_commit_db.is_merge_commit:
            methods = XmlFileProfiler.get_methods_of_java_blob(file_blob)
            for method in methods:
                method_str = b'<root>' + etree.tostring(method) + b'</root>'
                save_logs_of_method_xml_str_if_needed(change_type, file_path, head_commit_db, method_str)

        if change_type == LogChangeType.ADDED_WITH_FILE:
            logger.debug('added file: {},  sloc: {}, logging_loc: {}'.format(file_path, file_sloc, file_monitoring_loc))
        elif change_type == LogChangeType.DELETED_WITH_FILE:
            logger.debug('deleted file: {},  sloc: {}, logging_loc: {}'.format(file_path, file_sloc, file_monitoring_loc))

    return file_sloc, test_file_sloc, production_file_sloc, \
        file_monitoring_loc, test_file_monitoring_loc, production_file_monitoring_loc, \
        file_log_caller_loc, test_file_log_caller_loc, production_file_log_caller_loc, \
        file_print_caller_loc, test_file_print_caller_loc, production_file_print_caller_loc, \
        file_assert_caller_loc, test_file_assert_caller_loc, production_file_assert_caller_loc


def save_logs_of_method_xml_str_if_needed(change_type, file_path, head_commit_db, method_str):
    method = etree.fromstring(method_str, etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
    # get method name and parameters
    method_name = XmlFileProfiler.get_method_full_signature(method)
    total_calls, assert_calls, print_calls, log_calls = XmlFileProfiler.get_logging_calls_xml_of_method(method)
    if not head_commit_db.is_merge_commit:
        for call_xml in total_calls:
            save_logs_of_logging_call_xml(call_xml, change_type, file_path, head_commit_db, method_name)

    return len(total_calls), len(assert_calls), len(print_calls), len(log_calls)


def save_logs_of_logging_call_xml(call_xml, change_type, file_path, head_commit_db, method_name):
    call_text = XmlFileProfiler.transform_xml_str_to_code(etree.tostring(call_xml).decode('utf-8'))
    call_name = XmlFileProfiler.get_method_call_name(call_xml)
    call_type = XmlFileProfiler.get_log_call_type(call_xml)
    if '.' in call_name:
        verbosity = call_name.split('.')[-1]
    else:
        verbosity = call_name

    argument_type = LogProfiler.get_logging_argument_type(call_xml)
    _, verbosity_type = LogProfiler.get_log_content_component(call_text)

    log = Log.create(commit=head_commit_db, file_path=file_path, embed_method=method_name, change_type=change_type,
                     content=call_text, verbosity=verbosity, verbosity_type=verbosity_type, argument_type=argument_type,
                     call_type=call_type)
    log.is_test_log = LogProfiler.is_test_log(log)
    log.save()


# def calculate_churn_and_delta(added_loc, deleted_loc, updated_loc):
#     loc_churn = added_loc + deleted_loc + (updated_loc * 2)
#     loc_delta = added_loc - deleted_loc
#     return loc_churn, loc_delta
