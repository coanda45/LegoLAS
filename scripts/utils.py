from PIL import Image


def resize_image(image, max_size=(1024, 512)):
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

    width_ratio = max_width / width
    height_ratio = max_height / height
    if width_ratio < height_ratio:
        # shrink to match max_width
        new_width = max_width
        new_height = int(height * width_ratio)
    else:
        # shrink to match max_height
        new_width = int(width * height_ratio)
        new_height = max_height

    resized_image = image.resize((new_width, new_height),
                                 Image.Resampling.LANCZOS).copy()
    resized_image.info = image.info
    return resized_image
