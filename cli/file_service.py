import os


def is_exist(current_directory, file_name):
    """Checking for the presence of a @:param file_name in the @:param current_directory"""
    if os.path.isabs(get_absolute_path(current_directory, file_name)):
        return True
    return


def get_absolute_path(current_directory, file_name):
    """Getting the absolute path of the @:param file_name in the @:param current_directory"""
    if os.path.isabs(file_name):
        return file_name
    else:
        path = os.path.join(current_directory, file_name)
        return os.path.abspath(path)


def get_files(current_directory, directory_name):
    """Getting all files from a @:param directory_name located in the @:param current_directory"""
    abs_directory_name = get_absolute_path(current_directory, directory_name)
    all_files_and_dir = os.listdir(abs_directory_name)
    files = [f for f in all_files_and_dir if os.path.isfile(os.path.join(abs_directory_name, f))]
    dirs = [d + "/" for d in all_files_and_dir if os.path.isdir(os.path.join(abs_directory_name, d))]
    return dirs + files

