from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def get_temporary_image(ext="jpeg"):
    file = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(file, ext)
    return SimpleUploadedFile(f"test.{ext}", file.getvalue())
