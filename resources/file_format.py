import io

import PIL
import pyheif
from PIL import Image


def shrink_image_size(original_image, fixed_height: int = 200):
    height_percent = (fixed_height / float(original_image.size[1]))
    width_size = int((float(original_image.size[0]) * float(height_percent)))
    resized_image = original_image.resize((width_size, fixed_height), PIL.Image.NEAREST)
    buf = io.BytesIO()
    resized_image.save(buf, format='JPEG')
    byte_im = buf.getvalue()
    return byte_im


def generate_cache_content(original_contents: bytes, key: str, fixed_height: int = 200):
    image = None

    # todo check https://blog.josephmisiti.com/creating-image-thumbnails-in-python-using-PIL
    if key.lower().endswith(("jpg", "jpeg", "png", "tiff")):
        image = Image.open(io.BytesIO(original_contents))
    elif key.lower().endswith("heic"):
        i = pyheif.read(original_contents)
        image = Image.frombytes(mode=i.mode, size=i.size, data=i.data)

    if image is None:
        return None
    else:
        return shrink_image_size(image, fixed_height=fixed_height)
