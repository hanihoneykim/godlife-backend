from uuid import uuid4
from PIL import Image
from PIL import ImageFile
from io import BytesIO
from django.core.files import File

ImageFile.LOAD_TRUNCATED_IMAGES = True


def compress_image(image, filetype="JPEG", quality=80, size=None):
    img = Image.open(image)
    img_io = BytesIO()
    subsampling = 0
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.format == "JPEG":
        subsampling = "keep"
    if size:
        print(size)
        img.thumbnail(size)
    img.save(
        img_io,
        filetype,
        quality=quality,
        optimize=True,
        progressive=True,
        subsampling=subsampling,
    )
    new_image = File(img_io, name=image.name)
    return new_image


def upload_path(instance, filename):
    uuid = str(uuid4())
    name = f"{uuid[:2]}/{uuid[2:]}"
    if not len(filename.split(".")) == 1:
        name += f'.{filename.split(".")[-1]}'
    return f"files/{name}"
