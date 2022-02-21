echo ${GOOGLE_CREDENTIALS_JSON} > gcp-credentials.json
./manage.py collectstatic
