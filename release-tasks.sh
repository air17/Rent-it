#!/bin/bash

echo ${GOOGLE_CREDENTIALS_JSON} > gcp-credentials.json

python manage.py collectstatic --noinput
python manage.py makemigrations rentitapp accounts payments subscriptions
python manage.py migrate
