#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations rentitapp accounts payments subscriptions
python manage.py migrate
