#!/bin/bash
psql -c 'create database harambee;' -U postgres
echo "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2', 'NAME': 'harambee', 'USER': 'postgres', 'PASSWORD': '', 'HOST': 'localhost', 'PORT': ''}}" > harambee/local_settings.py
