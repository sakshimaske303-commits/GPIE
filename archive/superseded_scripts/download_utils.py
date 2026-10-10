import os


def file_exists(filepath):
    """True if the file is already there."""
    return os.path.exists(filepath)


def is_complete_file(filepath, expected_size):
    """True if the file is there and its size matches the size in the Copernicus metadata."""

    if not os.path.exists(filepath):
        return False

    actual_size = os.path.getsize(filepath)

    return actual_size == expected_size


def remove_file(filepath):
    """Delete a broken or incomplete file."""

    if os.path.exists(filepath):
        os.remove(filepath)


def get_file_size(filepath):
    """File size in bytes, 0 if the file is missing."""

    if not os.path.exists(filepath):
        return 0

    return os.path.getsize(filepath)