from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def get_temporary_image(ext="jpeg"):
    file = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(file, ext)
    return SimpleUploadedFile(f"test.{ext}", file.getvalue())
