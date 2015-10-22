# harambee-mobile

Harambee Mobile MVP
===================

|harambee-mobile-ci|_


Installation
~~~~~~~~~~~~

::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -r requirements.txt


Initial data
~~~~~~~~~~~~

::

    $ source ve/bin/activate
    (ve)$ python manage.py migrate


Run Tests
~~~~~~~~~

::

    $ source ve/bin/activate
    (ve)$ python manage.py test



.. |harambee-mobile-ci| image:: https://travis-ci.org/praekelt/harambee-mobile.svg?branch=develop
.. _harambee-mobile-ci: https://travis-ci.org/praekelt/harambee-mobile
