#!/usr/bin/env python3
""" Define logger with custom log formatter """
import os
import re
import logging
from typing import List, Tuple

import mysql.connector


PII_FIELDS: Tuple[str] = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(
    fields: List[str], redaction: str,
    message: str, separator: str
) -> str:
    """ Filter message by replacing each value in fields with redaction """
    for key in fields:
        pattern = r'({0}=)[^{1}]*({1})'.format(key, separator)
        message = re.sub(pattern, r'\1{}\2'.format(redaction), message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """ Set fields for each instance """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ Format LogRecord instance """
        log = super(RedactingFormatter, self).format(record=record)
        return filter_datum(self.fields, self.REDACTION, log, self.SEPARATOR)


def get_logger() -> logging.Logger:
    """ Creates and configures logger """
    logger = logging.getLogger('user_data')
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(fields=PII_FIELDS))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ Connect to mysql database """
    db_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    db_user = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_pwd = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    connector = mysql.connector.connect(
        host=db_host,
        port=3306,
        user=db_user,
        password=db_pwd,
        database=db_name,
    )
    return connector


def main() -> None:
    """ database users log """
    db = get_db()
    logger = get_logger()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        msg = (
            "name={}; email={}; phone={}; ssn={}; "
            "password={}; ip={}; last_login={}; user_agent={};"
        ).format(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        logger.info(msg)
    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
