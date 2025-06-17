from PIL import Image

from models.constants import SAM_TEST_MASKS_08  # tmp for demo day

def resize_image(image, max_size=(1024,512)):
    """
    Resize an image to fit within the specified maximum dimensions, preserving aspect ratio.

    Parameters:
        image (PIL.Image.Image): the input image to be resized
        max_size (tuple)       : a tuple (max_width, max_height) specifying the maximum allowed dimensions

    Returns:
        PIL.Image.Image: the resized image if the original exceeds the maximum size,
                         otherwise the original image unchanged
    """
    width, height = image.size
    max_width, max_height = max_size
    if (width <= max_width and height <= max_height):
        return image

    width_ratio  = max_width  / width
    height_ratio = max_height / height
    if width_ratio < height_ratio:
        # shrink to match max_width
        new_width  = max_width
        new_height = int(height * width_ratio)
    else:
        # shrink to match max_height
        new_width  = int(width * height_ratio)
        new_height = max_height

    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS).copy()
    resized_image.info = image.info
    return resized_image


 # tmp for demo day
def resize_SAM_masks(shrink_ratio=1):
    """SAM_TEST_MASKS_08 holds output values for a 1440*1920 image, but it has
    been resized (see fast.py:post_predict()).
    So we need to recompute bboxes and other pixel-dependent stuff to overimpose
    them on the resized image. None of this will be needed when SAM is called
    the normal way, it is just to save computing time for the demo day.
    """
    masks_out = SAM_TEST_MASKS_08.copy()
    for mask in masks_out:
        mask["area"] /= shrink_ratio**2
        mask["bbox"] = [int(e/shrink_ratio) for e in mask["bbox"]]
        mask["point_coords"] = [[e/shrink_ratio for e in mask["point_coords"][0]]]
        mask["crop_box"] = [int(e/shrink_ratio) for e in mask["crop_box"]]

    return masks_out
