import base64
import os


def convert_image_to_base64(image_path):
    # check does path exist
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The file at {image_path} was not found.")

    # read and covert image to base64
    with open(image_path, "rb") as f:
        img_bin = base64.b64encode(f.read()).decode("utf-8")
        return img_bin