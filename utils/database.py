import logging
from datetime import datetime
from shutil import copy2

from config import *


def backup():
    logging.info("Starting database backup.")
    time_now = datetime.now()
    backup_file = "{0}.db".format(time_now.strftime("%Y-%m-%d-%H-%M"))
    backup_dir = BACKUP_DIRECTORY + backup_file
    copy2("data.db", backup_dir)
    logging.info("Database backup completed. Saved file as {0}".format(
        backup_file
    ))
    return backup_file
