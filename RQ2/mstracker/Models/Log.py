from peewee import *

from Models.BaseModel import BaseModel
from Models.Commit import Commit


class Log(BaseModel):
    commit = ForeignKeyField(Commit, db_column='commit_fk', related_name='logs', on_delete='CASCADE')
    file_path = TextField()
    embed_method = TextField()
    change_type = CharField()
    content = TextField()
    update_type = CharField(null=True)
    content_update_from = TextField(null=True)
    verbosity = CharField(null=True)
    verbosity_type = CharField(null=True)
    argument_type = CharField(null=True)
    call_type = CharField(null=True)
    is_consistent_update = BooleanField(null=True)
    is_test_log = BooleanField(null=True)

    def is_type_added(self):
        return self.change_type == LogChangeType.ADDED_WITH_FILE or \
               self.change_type == LogChangeType.ADDED_WITH_METHOD or \
               self.change_type == LogChangeType.ADDED_INSIDE_METHOD

    def is_type_deleted(self):
        return self.change_type == LogChangeType.DELETED_WITH_FILE or \
               self.change_type == LogChangeType.DELETED_WITH_METHOD or \
               self.change_type == LogChangeType.DELETED_INSIDE_METHOD

    def is_type_updated(self):
        return self.change_type == LogChangeType.UPDATED


class LogChangeType(object):
    DELETED_WITH_FILE = 'DELETED_WITH_FILE'
    ADDED_WITH_FILE = 'ADDED_WITH_FILE'
    DELETED_WITH_METHOD = 'DELETED_WITH_METHOD'
    ADDED_WITH_METHOD = 'ADDED_WITH_METHOD'
    DELETED_INSIDE_METHOD = 'DELETED_INSIDE_METHOD'
    ADDED_INSIDE_METHOD = 'ADDED_INSIDE_METHOD'
    UPDATED = 'UPDATED'


class LogUpdateType(object):
    UPDATED_FORMAT = 'UPDATED_FORMAT'
    UPDATED_VERBOSITY = 'UPDATED_VERBOSITY'
    UPDATED_LOGGING_METHOD = 'UPDATED_LOGGING_METHOD'
    ADDED_TEXT = 'ADDED_TEXT'
    ADDED_VAR = 'ADDED_VAR'
    ADDED_SIM = 'ADDED_SIM'
    DELETED_TEXT = 'DELETED_TEXT'
    DELETED_VAR = 'DELETED_VAR'
    DELETED_SIM = 'DELETED_SIM'
    REPLACED_TEXT = 'REPLACED_TEXT'
    REPLACED_VAR = 'REPLACED_VAR'
    REPLACED_SIM = 'REPLACED_SIM'


class LogArgumentType(object):
    TEXT_ONLY = 'TEXT_ONLY'
    VAR_ONLY = 'VAR_ONLY'
    SIM_ONLY = 'SIM_ONLY'
    TEXT_VAR = 'TEXT_VAR'
    TEXT_SIM = 'TEXT_SIM'
    VAR_SIM = 'VAR_SIM'
    TEXT_VAR_SIM = 'TEXT_VAR_SIM'


class LogVerbosityType(object):
    TRACE = 'TRACE'
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'


class LogCallerType(object):
    LOG_CALL = 'LOG_CALL'
    PRINT_CALL = 'PRINT_CALL'
    ASSERT_CALL ='ASSERT_CALL'
