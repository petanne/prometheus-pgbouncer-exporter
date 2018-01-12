# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import psycopg2
import os
import re


def get_connection(user, password, port, host):
    connection = psycopg2.connect(
        database='pgbouncer',
        user=user,
        password=password,
        port=port,
        host=host
    )

    # pgbouncer does not support transactions (as it does not make sense to),
    # so don't start a transaction when connecting
    connection.set_session(autocommit=True)

    return connection


def get_data_by_named_column(connection, key):
    with connection.cursor() as cursor:
        cursor.execute('SHOW %s;' % key)

        rows = cursor.fetchall()
        column_names = list(column.name for column in cursor.description)

    return [
        dict(zip(column_names, row))
        for row in rows
    ]


def get_data_by_named_row(connection, key):
    with connection.cursor() as cursor:
        cursor.execute('SHOW %s;' % key)

        return dict(cursor.fetchall())


def get_pgbouncer_version():
    version = '1.8'
    s = os.popen('pgbouncer --version').read()
    res = re.match('.*version (?P<v1>\d+)\.(?P<v2>\d+)\..*', s).groupdict()
    try:
        if int(res['v1']) <= 1 and int(res['v2']) <= 7:
            version = '1.7'
    except:
        logging.warning('get bgbouncer version failed, default to 1.8')
    return version
