"""
Input validation helpers.

Uses Pillow for image format detection (imghdr was removed
in Python 3.13).
"""
import io
from PIL import Image, UnidentifiedImageError

from config.settings import ALLOWED_MIME_TYPES, MAX_IMAGE_SIZE_BYTES


class ValidationError(Exception):
    """Raised when user input fails validation."""


# Pillow's format names -> MIME types
_PIL_FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
    "BMP": "image/bmp",
    "TIFF": "image/tiff",
}


def validate_image(uploaded_file) -> bytes:
    """
    Validate an uploaded image and return its raw bytes.

    Raises
    ------
    ValidationError
        If the file is empty, too large, or not a supported image.
    """
    if uploaded_file is None:
        raise ValidationError("No file uploaded.")

    image_bytes = uploaded_file.getvalue()

    if not image_bytes:
        raise ValidationError("The uploaded file is empty.")

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            f"Image is too large "
            f"(> {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB)."
        )

    # ---- Detect real format with Pillow ----
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()  # raises if file is corrupt
            pil_format = img.format  # e.g. "JPEG", "PNG"
    except UnidentifiedImageError:
        raise ValidationError(
            "Could not detect a valid image format."
        )
    except Exception as exc:
        raise ValidationError(
            f"Invalid or corrupted image: {exc}"
        )

    if not pil_format:
        raise ValidationError("Could not determine image format.")

    mime = _PIL_FORMAT_TO_MIME.get(pil_format.upper())

    if not mime or mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"Unsupported image format: {pil_format}. "
            f"Allowed: {', '.join(ALLOWED_MIME_TYPES)}."
        )

    return image_bytes