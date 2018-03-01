#!/usr/bin/env python
from setuptools import setup

import billing_datatrans

setup(
    name='django-customer-billing-datatrans',
    version=billing_datatrans.__version__,
    description='',
    long_description='',
    author='Nicholas Wolff',
    author_email='nwolff@gmail.com',
    url=billing_datatrans.__URL__,
    download_url='https://pypi.python.org/pypi/django-customer-billing-datatrans',
    packages=[
        'billing_datatrans',
        'billing_datatrans.migrations',
        'billing_datatrans.signals'
    ],
    install_requires=[
        'Django>=1.11',
        'djangorestframework',
        'django-money',
        'structlog',
        'hashids',
        'typing',
        'django-customer-billing',
        'django-datatrans-gateway',
    ],
    license=billing_datatrans.__licence__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
