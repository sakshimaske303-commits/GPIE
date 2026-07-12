import os


def file_exists(filepath):
    """
    Returns True if file already exists.
    """
    return os.path.exists(filepath)


def is_complete_file(filepath, expected_size):
    """
    Returns True if file exists and its size matches
    the expected size from Copernicus metadata.
    """

    if not os.path.exists(filepath):
        return False

    actual_size = os.path.getsize(filepath)

    return actual_size == expected_size


def remove_file(filepath):
    """
    Deletes a corrupted or incomplete file.
    """

    if os.path.exists(filepath):
        os.remove(filepath)


def get_file_size(filepath):
    """
    Returns file size in bytes.
    """

    if not os.path.exists(filepath):
        return 0

    return os.path.getsize(filepath)