from setuptools import setup, find_packages

AUTHOR = 'petanne'
AUTHOR_EMAIL = 'lywxj1992@gmail.com'
URL = 'petanne.com'
VERSION = '1.8.1'

setup(
    name="prometheus-pgbouncer-exporter",
    version=VERSION,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prometheus-pgbouncer-exporter = prometheus_pgbouncer_exporter.cli:main',
        ],
    },
)
