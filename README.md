django-customer-billing-datatrans
============

[![Build Status](https://travis-ci.org/skioo/django-customer-billing-datatrans.svg?branch=master)](https://travis-ci.org/skioo/django-customer-billing-datatrans)
[![PyPI version](https://badge.fury.io/py/django-customer-billing-datatrans.svg)](https://badge.fury.io/py/django-customer-billing-datatrans)
[![Requirements Status](https://requires.io/github/skioo/django-customer-billing-datatrans/requirements.svg?branch=master)](https://requires.io/github/skioo/django-customer-billing-datatrans/requirements/?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)




Requirements
------------

* Python: 3.5 and over
* Django: 2.0 and over


Usage
-----

A bridge between django-customer-billing and django-datatrans-gateway

Add to your `INSTALLED_APPS` (django-customer-billing and django-datratrans-gateway should already be present):

    INSTALLED_APPS = (
        'billing.apps.BillingConfig',
        'datatrans.apps.DatatransConfig',
        ...
        'billing_datatrans.apps.BillingDatatransConfig',
        ...
    )


Run migrations: 

    ./manage.py migrate
    


Development
-----------

To install all dependencies:

    python setup.py develop

To run tests:

    pip install pytest-django
    pytest