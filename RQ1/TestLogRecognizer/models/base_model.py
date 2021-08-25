from peewee import *
from conf import config

db = PostgresqlDatabase(config.DB_NAME, user=config.DB_USER, password=config.DB_PASSWORD, host=config.DB_HOST, port=config.DB_PORT)


class BaseModel(Model):
    class Meta:
        database = db
