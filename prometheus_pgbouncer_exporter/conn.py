# coding: utf-8
import datetime
from .utils import get_connection


class CONN(object):
    CONNECTION = None
    PGBOUNCER_USER = None
    PGBOUNCER_PASSWORD = None
    PGBOUNCER_PORT = None
    PGBOUNCER_HOST = None

    @staticmethod
    def reconnect():
        """重连机制"""
        print('reconnect: ' + str(CONN.PGBOUNCER_USER) + ' ' + str(CONN.PGBOUNCER_HOST) + ' ' + str(
            CONN.PGBOUNCER_PORT))
        CONN.CONNECTION = get_connection(CONN.PGBOUNCER_USER, CONN.PGBOUNCER_PASSWORD, CONN.PGBOUNCER_PORT,
                                         CONN.PGBOUNCER_HOST)
