import os
from os.path import join

from distutils.core import setup

data_files = []
for dirpath, dirnames, filenames in os.walk('hexathel'):
    # ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    if "__init__.py" in filenames:
        data_files.append(".".join(fullsplit(dirpath)))

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
        ('/usr/local/hexathel', data_files),
        ('/usr/bin', [join('wrapper', _) for _ in os.listdir('wrapper') if _[-1] != '~'])
    ]
)