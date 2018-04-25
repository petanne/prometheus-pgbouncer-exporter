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

from prometheus_client.core import GaugeMetricFamily

from .utils import get_data_by_named_column, get_data_by_named_row
from .conn import CONN


class PgBouncerCollector(object):
    def __init__(self, connection=None, namespace='pgbouncer'):
        self.connection = connection
        self.namespace = namespace


class NamedColumnCollector(PgBouncerCollector):
    def get_labels_for_row(self, row):
        raise NotImplementedError()

    def collect(self):
        # Each of the metrics is recorded per database, by calling add_metric
        # with the database as the label on the appropriate GaugeMetricFamily.

        # First, create the GaugeMetricFamily objects for each metric
        gauges = {
            key: GaugeMetricFamily(
                name="%s_%s" % (self.namespace, name),
                documentation="%s (%s)" % (documentation, key),
                labels=self.labels,
            )
            for key, (name, documentation) in self.metrics.items()
        }

        rows = get_data_by_named_column(CONN.CONNECTION, self.query_parameter)

        # Each row coresponds to the metrics for a particular database
        for row in rows:
            database = row['database']

            if self.databases is not None and database not in self.databases:
                continue

            # Sort for deterministic ordering in the output
            for key in sorted(self.metrics.keys()):
                value = row[key]
                label_values = self.get_labels_for_row(row)

                gauges[key].add_metric(label_values, value)

        for gauge in gauges.values():
            yield gauge


class ListsCollector(PgBouncerCollector):
    metrics = {
        'databases': (
            'databases',
            "Number of databases",
        ),
        'users': (
            'users',
            "Number of users",
        ),
        'pools': (
            'pools',
            "Number of pools",
        ),
        'free_clients': (
            'free_clients',
            "Number of free clients",
        ),
        'used_clients': (
            'used_clients',
            "Number of used clients",
        ),
        'login_clients': (
            'login_clients',
            "Number of clients in the login stats",
        ),
        'free_servers': (
            'free_servers',
            "Number of free servers",
        ),
        'used_servers': (
            'used_servers',
            "Number of used servers",
        ),
        'dns_names': (
            'dns_names',
            "",
        ),
        'dns_zones': (
            'dns_zones',
            "",
        ),
        'dns_queries': (
            'dns_queries',
            "",
        ),
        'dns_pending': (
            'dns_pending',
            "",
        ),
    }

    def collect(self):
        data = get_data_by_named_row(CONN.CONNECTION, 'LISTS')

        for key, (name, documentation) in sorted(
                self.metrics.items(), key=lambda x: x[0]
        ):
            yield GaugeMetricFamily(
                name="%s_%s" % (self.namespace, name),
                documentation="%s (%s)" % (documentation, key),
                value=data[key],
            )


class StatsCollector(NamedColumnCollector):
    query_parameter = 'STATS'

    labels = ['database']

    metrics = {
        'total_requests': (
            'requests_total',
            "Total number of SQL requests pooled by pgbouncer",
        ),
        'total_received': (
            'received_bytes_total',
            "Total volume in bytes of network traffic received by pgbouncer",
        ),
        'total_sent': (
            'sent_bytes_total',
            "Total volume in bytes of network traffic sent by pgbouncer",
        ),
        'total_query_time': (
            'query_microseconds_total',
            "Total number of microseconds spent by pgbouncer when actively connected to PostgreSQL",
        ),
        'avg_query': (
            'avg_query',
            "Avg time of avg_query",
        ),
    }

    def __init__(self, databases, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.databases = databases

    def get_labels_for_row(self, row):
        return [row['database']]


class Stats18Collector(NamedColumnCollector):
    query_parameter = 'STATS'

    labels = ['database']

    metrics = {
        'total_query_count': (
            'requests_total',
            "Total number of SQL requests pooled by pgbouncer",
        ),
        'total_received': (
            'received_bytes_total',
            "Total volume in bytes of network traffic received by pgbouncer",
        ),
        'total_sent': (
            'sent_bytes_total',
            "Total volume in bytes of network traffic sent by pgbouncer",
        ),
        'total_query_time': (
            'query_microseconds_total',
            "Total number of microseconds spent by pgbouncer when actively connected to PostgreSQL",
        ),
        'avg_query_count': (
            'avg_query_count',
            "Avg number of avg_query",
        ),
        'avg_query_time': (
            'avg_query',
            "Avg time of avg_query",
        ),
    }

    def __init__(self, databases, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.databases = databases

    def get_labels_for_row(self, row):
        return [row['database']]


class PoolsCollector(NamedColumnCollector):
    query_parameter = 'POOLS'

    labels = ['database', 'user']

    metrics = {
        'cl_active': (
            'active_clients',
            "Client connections that are linked to server connection and can process queries",
        ),
        'cl_waiting': (
            'waiting_clients',
            "Client connections have sent queries but have not yet got a server connection",
        ),
    }

    def __init__(self, databases, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.databases = databases

    def get_labels_for_row(self, row):
        return [row['database'], row['user']]


class DatabasesCollector(NamedColumnCollector):
    query_parameter = 'DATABASES'

    labels = ['database']

    metrics = {
        'pool_size': (
            'pool_size',
            "",
        ),
        'reserve_pool': (
            'reserve_pool',
            "",
        ),
    }

    def __init__(self, databases, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.databases = databases

    def get_labels_for_row(self, row):
        return [row['database']]
