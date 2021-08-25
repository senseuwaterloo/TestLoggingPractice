from models.base_model import BaseModel
from peewee import *
from models.repo import Repo


class File(BaseModel):
    repo = ForeignKeyField(Repo, db_column='repo_fk', related_name='files', on_delete='CASCADE')
    file_path = TextField()
    # Comment out for calculating variable number
    sloc = BigIntegerField(null=True)
    is_test_file = BooleanField(null=True)
    loc = BigIntegerField(null=True)


    # Comment out for calculating variable number
    # monitoring_loc = BigIntegerField(null=True)
    # assert_caller_loc = BigIntegerField(null=True)
    # print_caller_loc = BigIntegerField(null=True)
    # log_caller_loc = BigIntegerField(null=True)
    #
    # trace_level_num = BigIntegerField(null=True)
    # debug_level_num = BigIntegerField(null=True)
    # info_level_num = BigIntegerField(null=True)
    # warn_level_num = BigIntegerField(null=True)
    # error_level_num = BigIntegerField(null=True)
