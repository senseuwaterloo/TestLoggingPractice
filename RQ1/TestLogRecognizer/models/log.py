from models.base_model import BaseModel
from peewee import *
from models.file import File


class Log(BaseModel):
    file = ForeignKeyField(File, db_column='file_fk', related_name='logs', on_delete='CASCADE')
    file_path = TextField()
    content = TextField()
    verbosity_type = CharField(null=True)
    argument_type = CharField(null=True)
    variable_number = IntegerField(null=True)
    # added for calculate variable number, comment out for calculate variable and text length
    # text_length = IntegerField(null=True)


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
