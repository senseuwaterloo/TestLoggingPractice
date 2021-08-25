# import logging

from Models import Config
from Models.Repository import Repository
from Profilers.DiffProfiler import diff_profiler
from Utils import RepoUtil, LocUtil
from Models.Commit import Commit


def _is_commit_analyzed(commit: Commit):
    # commit_code_churn = commit.added_sloc + commit.deleted_sloc + commit.updated_sloc * 2
    return commit.added_sloc is not None or commit.deleted_sloc is not None or commit.updated_sloc is not None


def update_repo_summary(repo: Repository):
    path = Config.get_repo_local_path_with_project_name(repo.project_name)

    local_last_commit_date = RepoUtil.get_last_commit_date(path)
    if repo.last_commit_date is None or local_last_commit_date > repo.last_commit_date:
        repo.files_num = RepoUtil.get_files_num(path)
        repo.commits_num = RepoUtil.get_commits_num(path)
        repo.last_commit_date = local_last_commit_date
        repo.first_commit_date = RepoUtil.get_first_commit_date(path)
        repo.authors_num = RepoUtil.get_authors_num(path)
        repo.sloc = LocUtil.get_java_sloc(path)
        repo.test_sloc = LocUtil.get_test_java_sloc(path)
        repo.production_sloc = LocUtil.get_production_java_sloc(path)

        repo.monitoring_loc, repo.assert_caller_loc, repo.print_caller_loc, repo.log_caller_loc, \
            repo.test_monitoring_loc, repo.test_assert_caller_loc, repo.test_print_caller_loc, \
            repo.test_log_caller_loc, repo.production_monitoring_loc, repo.production_assert_caller_loc, \
            repo.production_print_caller_loc, repo.production_log_caller_loc, repo.total_trace_level_num,\
            repo.total_debug_level_num, repo.total_info_level_num, repo.total_warn_level_num,\
            repo.total_error_level_num, repo.test_trace_level_num, repo.test_debug_level_num,\
            repo.test_info_level_num, repo.test_warn_level_num, repo.test_error_level_num,\
            repo.production_trace_level_num, repo.production_debug_level_num, repo.production_info_level_num,\
            repo.production_warn_level_num, repo.production_error_level_num = LocUtil.get_logging_loc_of_repo(path)

        # repo.logging_loc, repo.test_logging_loc, repo.production_logging_loc = LocUtil.get_logging_loc_of_repo(path)
        repo.save()


def project_profiler(repo: Repository, detect_type):
    # logging.basicConfig(filename='/Users/holen/DegreeProject/mstracker/Log/ExecutionLog.log', level=logging.DEBUG)
    # logging.info('processing {}'.format(repo.project_name))
    print('processing {}'.format(repo.project_name))
    path = Config.get_repo_local_path_with_project_name(repo.project_name)

    # update_repo_summary(repo)
    if detect_type == Config.DETECT_UPDATE:
        commit_list = RepoUtil.get_updated_commits(path)
        update_repo_summary(repo)
    else:
        update_repo_summary(repo)
        commit_list = RepoUtil.get_all_commits(path)

    git_repo = RepoUtil.get_project_repository(path)

    # f = open("/home/users/hzhang/project/cassandra_commit_log.txt", "a")
    for i in range(0, len(commit_list)):
        # print(commit_list[i])
        head_commit_sha = commit_list[i]
        head_commit = git_repo.commit(head_commit_sha)

        is_merge_commit = False
        # logging.info('current commit: {}'.format(head_commit_sha))
        print('current commit: {}'.format(head_commit_sha))
        if head_commit.parents:
            if len(head_commit.parents) > 1:
                is_merge_commit = True

            # Attempt to get the row matching the given filters. If no matching row is found, create a new row.
            # return tuple of Model instance and boolean indicating if a new object was created.
            head_commit_db = Commit.get_or_create(repo=repo, commit_id=head_commit_sha)[0]
            head_commit_db.is_merge_commit = is_merge_commit
            if i == 0:
                head_commit_db.sloc = repo.sloc
                head_commit_db.test_sloc = repo.test_sloc
                head_commit_db.production_sloc = repo.production_sloc
                head_commit_db.monitoring_loc = repo.monitoring_loc
                head_commit_db.test_monitoring_loc = repo.test_monitoring_loc
                head_commit_db.production_monitoring_loc = repo.production_monitoring_loc
                head_commit_db.log_caller_loc = repo.log_caller_loc
                head_commit_db.test_log_caller_loc = repo.test_log_caller_loc
                head_commit_db.production_log_caller_loc = repo.production_log_caller_loc
                head_commit_db.print_caller_loc = repo.print_caller_loc
                head_commit_db.test_print_caller_loc = repo.test_print_caller_loc
                head_commit_db.production_print_caller_loc = repo.production_print_caller_loc
                head_commit_db.assert_caller_loc = repo.assert_caller_loc
                head_commit_db.test_assert_caller_loc = repo.test_assert_caller_loc
                head_commit_db.production_assert_caller_loc = repo.production_assert_caller_loc

            for parent_commit in head_commit.parents:
                parent_commit_sha = parent_commit.hexsha
                commit_diff = RepoUtil.get_diff_between_commits(parent_commit, head_commit)
                head_commit_db.parent_commit_id = parent_commit_sha
                parent_commit_db = Commit.get_or_create(repo=repo, commit_id=parent_commit_sha)[0]
                if _is_commit_analyzed(head_commit_db) and _is_commit_analyzed(parent_commit_db):
                    continue

                sloc = head_commit_db.sloc
                test_sloc = head_commit_db.test_sloc
                production_sloc = head_commit_db.production_sloc
                monitoring_loc = head_commit_db.monitoring_loc
                test_monitoring_loc = head_commit_db.test_monitoring_loc
                production_monitoring_loc = head_commit_db.production_monitoring_loc
                log_caller_loc = head_commit_db.log_caller_loc
                test_log_caller_loc = head_commit_db.test_log_caller_loc
                production_log_caller_loc = head_commit_db.production_log_caller_loc
                print_caller_loc = head_commit_db.print_caller_loc
                test_print_caller_loc = head_commit_db.test_print_caller_loc
                production_print_caller_loc = head_commit_db.production_print_caller_loc
                assert_caller_loc = head_commit_db.assert_caller_loc
                test_assert_caller_loc = head_commit_db.test_assert_caller_loc
                production_assert_caller_loc = head_commit_db.production_assert_caller_loc

                sloc_delta, test_sloc_delta, production_sloc_delta, monitoring_loc_delta, test_monitoring_loc_delta, \
                    production_monitoring_loc_delta, log_caller_loc_delta, test_log_caller_loc_delta, \
                    production_log_caller_loc_delta, print_caller_loc_delta, test_print_caller_loc_delta, \
                    production_print_caller_loc_delta, assert_caller_loc_delta, test_assert_caller_loc_delta, \
                    production_assert_caller_loc_delta = diff_profiler(git_repo, commit_diff, head_commit_db)
                sloc -= sloc_delta
                test_sloc -= test_sloc_delta
                production_sloc -= production_sloc_delta
                monitoring_loc -= monitoring_loc_delta
                test_monitoring_loc -= test_monitoring_loc_delta
                production_monitoring_loc -= production_monitoring_loc_delta
                log_caller_loc -= log_caller_loc_delta
                test_log_caller_loc -= test_log_caller_loc_delta
                production_log_caller_loc -= production_log_caller_loc_delta
                print_caller_loc -= print_caller_loc_delta
                test_print_caller_loc -= test_print_caller_loc_delta
                production_print_caller_loc -= production_print_caller_loc_delta
                assert_caller_loc -= assert_caller_loc_delta
                test_assert_caller_loc -= test_assert_caller_loc_delta
                production_assert_caller_loc -= production_assert_caller_loc_delta

                parent_commit_db.sloc = sloc
                parent_commit_db.test_sloc = test_sloc
                parent_commit_db.production_sloc = production_sloc
                parent_commit_db.monitoring_loc = monitoring_loc
                parent_commit_db.test_monitoring_loc = test_monitoring_loc
                parent_commit_db.production_monitoring_loc = production_monitoring_loc
                parent_commit_db.log_caller_loc = log_caller_loc
                parent_commit_db.test_log_caller_loc = test_log_caller_loc
                parent_commit_db.production_log_caller_loc = production_log_caller_loc
                parent_commit_db.print_caller_loc = print_caller_loc
                parent_commit_db.test_print_caller_loc = test_print_caller_loc
                parent_commit_db.production_print_caller_loc = production_print_caller_loc
                parent_commit_db.assert_caller_loc = assert_caller_loc
                parent_commit_db.test_assert_caller_loc = test_assert_caller_loc
                parent_commit_db.production_assert_caller_loc = production_assert_caller_loc

                parent_commit_db.save()
        else:
            commit_diff = RepoUtil.get_diff_of_initial_commit(git_repo, head_commit)
            head_commit_db = Commit.get_or_create(repo=repo, commit_id=head_commit_sha)[0]
            if not _is_commit_analyzed(head_commit_db):
                diff_profiler(git_repo, commit_diff, head_commit_db)

    # f.close()
