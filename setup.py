import os
 
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
        ('/usr/local/', 'hexathel'),
        ('/usr/bin/', 'wrapper/*')
    ]
)