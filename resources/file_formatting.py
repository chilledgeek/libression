import io

import pyheif
from botocore.response import StreamingBody
from PIL import Image


def shrink_image_size(original_image: Image, fixed_width: int = 128):
    width_percent = (fixed_width / float(original_image.size[1]))
    height = int((float(original_image.size[0]) * float(width_percent)))
    original_image.thumbnail((fixed_width, height))
    buf = io.BytesIO()
    original_image.save(buf, format='JPEG')
    byte_im = buf.getvalue()
    return byte_im


def generate_cache_content(original_contents: StreamingBody, key: str, fixed_width: int = 200):
    image = None

    # todo check https://blog.josephmisiti.com/creating-image-thumbnails-in-python-using-PIL
    # can get metadata with some i.metadat[0].get("data")
    if key.lower().endswith(("jpg", "jpeg", "png", "tiff")):
        image = Image.open(original_contents)
    elif key.lower().endswith("heic"):
        i = pyheif.read(original_contents)
        image = Image.frombytes(mode=i.mode, size=i.size, data=i.data)

    if image is None:
        return None
    else:
        return shrink_image_size(image, fixed_width=fixed_width)
