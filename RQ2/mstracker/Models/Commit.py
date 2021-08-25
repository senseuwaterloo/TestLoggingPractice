from peewee import *
from playhouse.postgres_ext import DateTimeTZField

from Models.BaseModel import BaseModel
from Models.Repository import Repository


class Commit(BaseModel):
    repo = ForeignKeyField(Repository, db_column='repo_fk', related_name='commits', on_delete='CASCADE')
    commit_id = CharField()
    parent_commit_id = CharField(null=True)
    is_merge_commit = BooleanField(default=False)
    author_email = CharField(null=True)
    author_name = CharField(null=True)
    authored_date = DateTimeTZField(null=True)
    committer_email = CharField(null=True)
    committer_name = CharField(null=True)
    committed_date = DateTimeTZField(null=True)
    message = TextField(null=True)

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


    added_sloc = BigIntegerField(null=True)
    deleted_sloc = BigIntegerField(null=True)
    updated_sloc = BigIntegerField(null=True)

    added_test_sloc = BigIntegerField(null=True)
    deleted_test_sloc = BigIntegerField(null=True)
    updated_test_sloc = BigIntegerField(null=True)

    added_production_sloc = BigIntegerField(null=True)
    deleted_production_sloc = BigIntegerField(null=True)
    updated_production_sloc = BigIntegerField(null=True)

    added_monitoring_loc = BigIntegerField(null=True)
    deleted_monitoring_loc = BigIntegerField(null=True)
    updated_monitoring_loc = BigIntegerField(null=True)

    added_test_monitoring_loc = BigIntegerField(null=True)
    deleted_test_monitoring_loc = BigIntegerField(null=True)
    updated_test_monitoring_loc = BigIntegerField(null=True)

    added_production_monitoring_loc = BigIntegerField(null=True)
    deleted_production_monitoring_loc = BigIntegerField(null=True)
    updated_production_monitoring_loc = BigIntegerField(null=True)

    added_log_caller_loc = BigIntegerField(null=True)
    deleted_log_caller_loc = BigIntegerField(null=True)
    updated_log_caller_loc = BigIntegerField(null=True)

    added_test_log_caller_loc = BigIntegerField(null=True)
    deleted_test_log_caller_loc = BigIntegerField(null=True)
    updated_test_log_caller_loc = BigIntegerField(null=True)

    added_production_log_caller_loc = BigIntegerField(null=True)
    deleted_production_log_caller_loc = BigIntegerField(null=True)
    updated_production_log_caller_loc = BigIntegerField(null=True)

    added_print_caller_loc = BigIntegerField(null=True)
    deleted_print_caller_loc = BigIntegerField(null=True)
    updated_print_caller_loc = BigIntegerField(null=True)

    added_test_print_caller_loc = BigIntegerField(null=True)
    deleted_test_print_caller_loc = BigIntegerField(null=True)
    updated_test_print_caller_loc = BigIntegerField(null=True)

    added_production_print_caller_loc = BigIntegerField(null=True)
    deleted_production_print_caller_loc = BigIntegerField(null=True)
    updated_production_print_caller_loc = BigIntegerField(null=True)

    added_assert_caller_loc = BigIntegerField(null=True)
    deleted_assert_caller_loc = BigIntegerField(null=True)
    updated_assert_caller_loc = BigIntegerField(null=True)

    added_test_assert_caller_loc = BigIntegerField(null=True)
    deleted_test_assert_caller_loc = BigIntegerField(null=True)
    updated_test_assert_caller_loc = BigIntegerField(null=True)

    added_production_assert_caller_loc = BigIntegerField(null=True)
    deleted_production_assert_caller_loc = BigIntegerField(null=True)
    updated_production_assert_caller_loc = BigIntegerField(null=True)

    # code_churn = BigIntegerField(null=True)
    # test_code_churn = BigIntegerField(null=True)
    # production_code_churn = BigIntegerField(null=True)
    # logging_code_churn = BigIntegerField(null=True)
    # test_logging_code_churn = BigIntegerField(null=True)
    # production_logging_code_churn = BigIntegerField(null=True)


