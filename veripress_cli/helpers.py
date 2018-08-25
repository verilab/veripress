import os
import shutil


def copy_folder_content(src, dst):
    """
    Copy all content in src directory to dst directory.
    The src and dst must exist.
    """
    for file in os.listdir(src):
        file_path = os.path.join(src, file)
        dst_file_path = os.path.join(dst, file)
        if os.path.isdir(file_path):
            shutil.copytree(file_path, dst_file_path)
        else:
            shutil.copyfile(file_path, dst_file_path)


def remove_folder_content(path, ignore_hidden_file=False):
    """
    Remove all content in the given folder.
    """
    for file in os.listdir(path):
        if ignore_hidden_file and file.startswith('.'):
            continue

        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)


def makedirs(path, mode=0o777, exist_ok=False):
    """A wrapper of os.makedirs()."""
    os.makedirs(path, mode, exist_ok)
