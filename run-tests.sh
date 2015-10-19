#!/bin/sh
python manage.py syncdb | tee
python manage.py migrate
coverage run --source=harambee manage.py test
