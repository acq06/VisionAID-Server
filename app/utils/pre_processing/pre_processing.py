import numpy as np
from PIL import Image, ImageEnhance
from scipy.ndimage import gaussian_filter


def upscale_image(
    image, dpi=300, gaussian_sigmas=[2], sharpen_factor=4, contrast_factor=2
):
    # Convert numpy array to PIL Image if it's a numpy array
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    # If you don't have DPI information, use the given dpi value
    scale_factor = dpi / 72  # Assume original DPI is 72

    # Upscale the image using nearest neighbor interpolation
    upscaled_nearest = image.resize(
        (int(image.width * scale_factor), int(image.height * scale_factor)),
        Image.NEAREST,
    )

    # Apply Gaussian filters sequentially
    gaussian_image = upscaled_nearest
    for sigma in gaussian_sigmas:
        # Apply Gaussian filter with the current sigma
        filtered_image = gaussian_filter(np.array(gaussian_image), sigma=sigma)
        gaussian_image = Image.fromarray(filtered_image).convert("RGB")

    # Upscale using bilinear interpolation on the final Gaussian-filtered image
    upscaled_bilinear = gaussian_image.resize(
        (gaussian_image.width, gaussian_image.height), Image.BILINEAR
    )

    # Upscale using bicubic interpolation on the bilinear-upscaled image
    upscaled_bicubic = upscaled_bilinear.resize(
        (upscaled_bilinear.width, upscaled_bilinear.height), Image.BICUBIC
    )

    # Sharpen Image
    sharpen_enhancer = ImageEnhance.Sharpness(upscaled_bicubic)
    sharpened_image = sharpen_enhancer.enhance(sharpen_factor)

    # Improve contrast
    contrast_enhancer = ImageEnhance.Contrast(sharpened_image)
    improved_image = contrast_enhancer.enhance(contrast_factor)

    # Convert back to numpy array if needed
    return np.array(improved_image)
