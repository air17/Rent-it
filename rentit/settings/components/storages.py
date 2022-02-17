import os.path

from google.oauth2 import service_account

from rentit.settings.components import BASE_DIR, config

DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

# Google storage
GS_BUCKET_NAME = config("GS_BUCKET_NAME")
GS_PROJECT_ID = config("GS_PROJECT_ID")
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, config("GS_CREDENTIALS"))
)
