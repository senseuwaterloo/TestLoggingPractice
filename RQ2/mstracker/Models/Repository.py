from peewee import *
from playhouse.postgres_ext import DateTimeTZField

# from Models import Commit
from Models.BaseModel import BaseModel


class Repository(BaseModel):
    repo_id = CharField()
    project_name = CharField(null=True)
    authors_num = IntegerField(null=True)
    commits_num = IntegerField(null=True)
    files_num = BigIntegerField(null=True)
    last_commit_date = DateTimeTZField(null=True)
    first_commit_date = DateTimeTZField(null=True)
    sloc = BigIntegerField(null=True)
    test_sloc = BigIntegerField(null=True)
    production_sloc = BigIntegerField(null=True)

    monitoring_loc = BigIntegerField(null=True)
    test_monitoring_loc = BigIntegerField(null=True)
    production_monitoring_loc = BigIntegerField(null=True)

    log_caller_loc = BigIntegerField(null=True)
    test_log_caller_loc = BigIntegerField(null=True)
    production_log_caller_loc = BigIntegerField(null=True)

    print_caller_loc = BigIntegerField(null=True)
    test_print_caller_loc = BigIntegerField(null=True)
    production_print_caller_loc = BigIntegerField(null=True)

    assert_caller_loc = BigIntegerField(null=True)
    test_assert_caller_loc = BigIntegerField(null=True)
    production_assert_caller_loc = BigIntegerField(null=True)

    total_trace_level_num = BigIntegerField(null=True)
    total_debug_level_num = BigIntegerField(null=True)
    total_warn_level_num = BigIntegerField(null=True)
    total_info_level_num = BigIntegerField(null=True)
    total_error_level_num = BigIntegerField(null=True)

    test_trace_level_num = BigIntegerField(null=True)
    test_debug_level_num = BigIntegerField(null=True)
    test_warn_level_num = BigIntegerField(null=True)
    test_info_level_num = BigIntegerField(null=True)
    test_error_level_num = BigIntegerField(null=True)

    production_trace_level_num = BigIntegerField(null=True)
    production_debug_level_num = BigIntegerField(null=True)
    production_warn_level_num = BigIntegerField(null=True)
    production_info_level_num = BigIntegerField(null=True)
    production_error_level_num = BigIntegerField(null=True)

    analyzed_date = DateTimeTZField(null=True)

    def get_non_merge_commits(self):
        from Models import Commit
        return self.commits.where(Commit.is_merge_commit is False)
