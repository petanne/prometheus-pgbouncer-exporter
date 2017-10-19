# Copyright (C) 2015  Christopher Baines <mail@cbaines.net>
#
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
import psycopg2

from prometheus_client.exposition import MetricsHandler, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import core
from urllib.parse import quote_plus, parse_qs, urlparse

from .conn import CONN

index_page = """
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>Prometheus PgBouncer Exporter</title>
</head>

<body>
  <h1>PgBouncer exporter for Prometheus</h1>

  <p>
    This is a simple exporter for PgBouncer that makes several metrics
    available to Prometheus.
  </p>

  <p>
    Metrics are exported from the SHOW LISTS, STATS, POOLS and DATABASES comand
    output.
  </p>

  <a href="/debug/metrics">View metrics</a>

  <h2>Example Configuration</h2>
  <p>
    You must configure Prometheus to scrape the metrics exported here. The port
    is 9127, and the configuration should look something like the example
    below.
  </p>
  <pre><code>
    scrape_configs:
      - job_name: pgbouncer
        target_groups:
          - targets:
            - MACHINE_ADDRESS:9127
  </code></pre>

  <h2>Information</h2>
  <p>
    Copyright (C) 2015  Christopher Baines <mail@cbaines.net><br>
    <a href="/licence">View Licence</a>
  </p>

  <p>
    The source may be obtained from
    <a href="http://git.cbaines.net/prometheus-pgbouncer-exporter/">
    this Git repository</a>
  </p>

  <p>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
  </p>

  <p>
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
  </p>
</body>
</html>
"""


def create_request_handler(licence_location):
    class RequestHandler(MetricsHandler):
        def do_GET_super(self):
            """extended super MetricsHandler().do_GET()
                add reconnect when psycopg2.Error
            """
            registry = core.REGISTRY
            params = parse_qs(urlparse(self.path).query)
            if 'name[]' in params:
                registry = registry.restricted_registry(params['name[]'])
            try:
                output = generate_latest(registry)
            except psycopg2.Error:
                CONN.reconnect()
                # generate_latest again after re-connect
                try:
                    output = generate_latest(registry)
                except:
                    self.send_error(500, 'error generating metric output')
                    raise
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(output)

        def do_GET(self):
            if self.path == "/debug/metrics":
                return self.do_GET_super()

            self.send_response(200)
            self.end_headers()

            if self.path == "/licence":
                with open(
                        licence_location,
                        'rb',
                ) as licence:
                    self.wfile.write(licence.read())
            else:
                self.wfile.write(index_page.encode('UTF-8'))

    return RequestHandler
