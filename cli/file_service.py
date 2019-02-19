import os


def is_exist(current_directory, file_name):
    if os.path.isabs(file_name) and os.path.exists(file_name):
        return True
    elif os.path.exists(os.path.join(current_directory, file_name)):
        return True
    return


def get_absolute_path(current_directory, file_name):
    if os.path.isabs(file_name):
        return file_name
    else:
        path = os.path.join(current_directory, file_name)
        return os.path.abspath(path)


def get_files(current_directory, directory_name):
    abs_directory_name = get_absolute_path(current_directory, directory_name)
    all_files_and_dir = os.listdir(abs_directory_name)
    files = [f for f in all_files_and_dir if os.path.isfile(os.path.join(abs_directory_name, f))]
    dirs = [d + "/" for d in all_files_and_dir if os.path.isdir(os.path.join(abs_directory_name, d))]
    return dirs + files


def is_dir_exist(current_directory, file_name):
    return is_exist(current_directory, file_name) \
           and os.path.isdir(get_absolute_path(current_directory, file_name))
