import os
from os.path import join

from distutils.core import setup


def listfiles( basepath ):
    l = []
    for filenames in os.listdir(basepath):
        path = os.path.join( basepath, filenames)
        if os.path.isfile(path):
            l.append( path )
    return l

os.chmod('wrapper/hexathel', 0o755)
os.chmod('wrapper/hexathel-shell', 0o755)
os.chmod('wrapper/hexathel-artisan', 0o755)

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
        ('/usr/local/hexathel', listfiles('hexathel')),
        ('/usr/local/hexathel/helper', listfiles('hexathel/helper')),
        ('/usr/local/hexathel/template', listfiles('hexathel/template')),
        ('/usr/bin', [join('wrapper', _) for _ in os.listdir('wrapper') if _[-1] != '~'])
    ]
)