#!/bin/sh

set -e 

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata ecomm_data.json

uwsgi --socket :9000 --workers 4 --master --enable-threads --module main_app.wsgi