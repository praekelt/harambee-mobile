Harambee Mobile MVP
===================

|harambee-mobile-ci|_
|harambee-mobile-coveralls|_


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

.. |harambee-mobile-coveralls| image:: https://coveralls.io/repos/praekelt/harambee-mobile/badge.svg?branch=develop&service=github
.. _harambee-mobile-coveralls: https://coveralls.io/github/praekelt/harambee-mobile?branch=develop
