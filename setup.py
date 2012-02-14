#!/usr/bin/env python

from distutils.core import setup

setup(name = 'pybis',
    version = '0.9',
    description = 'Python IBIS parser',
    author = 'Russ Dill',
    requires = [ 'pyparsing', 'numpy' ],
    author_email = 'Russ.Dill@gmail.com',
    url = 'https://github.com/russdill/pybis/wiki',
    download_url = 'https://github.com/russdill/pybis',
    py_modules = [ 'pybis' ],
    scripts = [ 'examples/models.py' ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]
    )
