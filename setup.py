import os
from os.path import join

from distutils.core import setup

setup(
    name = 'hexathel',
    version = '1.0',
    description = 'Tiny Crawler with RabbitMQ',
    keywords = 'crawler',
    license = 'GPL',
    author = 'Imdedr',
    author_email = '',
    maintainer = 'Imdedr',
    maintainer_email = '',
    url = 'http://github.com/imdedr/hexathel/',
    dependency_links = [],
    install_requires=[
        'lxml',
        'pika',
        'pymongo<=2.9',
        'raven',
        'setproctitle'
    ],
    data_files=[
        ('/usr/local/hexathel', [join('hexathel', _) for _ in os.listdir('hexathel') if _[-1] != '~']),
        ('/usr/bin', [join('wrapper', _) for _ in os.listdir('wrapper') if _[-1] != '~'])
    ]
)