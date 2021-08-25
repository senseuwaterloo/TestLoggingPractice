from peewee import *

from Models import Config

db = PostgresqlDatabase(Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASSWORD, host=Config.DB_HOST, port=Config.DB_PORT)


class BaseModel(Model):
    class Meta:
        database = db
