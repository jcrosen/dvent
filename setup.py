"""
Dvent setup
"""

from codecs import open
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dvent',
    version='0.1.1',
    url='https://github.com/jcrosen/dvent',
    author='Jeremy Crosen',
    author_email='jeremy.crosen@gmail.com',
    description=(
        'Simple, immutable, functional models for '
        'domain driven design with event sourcing'
    ),
    long_description=long_description,
    license='Apache License 2.0',
    keywords=(
        'eventsourcing event sourcing '
        'ddd domain driven design immutable functional'
    ),
    packages=['dvent'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'pyrsistent>=0.14.2,<1',
    ],
    python_requires='>=3.4',
)
