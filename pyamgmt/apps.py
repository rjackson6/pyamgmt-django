import logging

from django.apps import AppConfig
from django.db import connection
from django.db.models.signals import post_migrate, pre_migrate

logger = logging.getLogger(__name__)


def pre_migrate_disable_fk():
    """Temporary work around for a bug with MySQL/MariaDB."""
    logger.info('--DISABLING FOREIGN KEY CHECKS')
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW VARIABLES LIKE 'FOREIGN%';")
        logger.info(cursor.fetchall())


def post_migrate_enable_fk():
    """Re-enable foreign keys."""
    logger.info('--ENABLING FOREIGN KEY CHECKS')
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cursor.execute("SHOW VARIABLES LIKE 'FOREIGN%';")
        logger.info(cursor.fetchall())


# noinspection PyUnusedLocal
def pre_migrate_callback(sender, **kwargs):
    logger.info('--PRE-MIGRATE')
    pre_migrate_disable_fk()


# noinspection PyUnusedLocal
def post_migrate_callback(sender, **kwargs):
    # from pyamgmt.scripts.create_initial_data import create_initial_records
    logger.info('--CALLING FK...')
    post_migrate_enable_fk()
    # print('--CREATING INITIAL RECORDS')
    # try:
    #     create_initial_records()
    # except ProgrammingError:
    #     print('TABLES CHANGED OR DELETED; Stopping initial record creation.')
    #     return


class PyamgmtConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pyamgmt'

    def ready(self):
        pre_migrate.connect(pre_migrate_callback, sender=self)
        post_migrate.connect(post_migrate_callback, sender=self)
