#!/bin/bash

python manage.py makemigrations rentitapp accounts payments subscriptions
python manage.py migrate
