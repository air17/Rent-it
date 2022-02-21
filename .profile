echo ${GOOGLE_CREDENTIALS_JSON} > gcp-credentials.json
python manage.py collectstatic --noinput
