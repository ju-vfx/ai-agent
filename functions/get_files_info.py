import os

def get_files_info(working_directory, directory="."):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory.'
        if not os.path.isdir(target_dir):
            return f'Error: "{target_dir}" is not a directory'
    
        return_items = []
        for file in os.listdir(target_dir):
            filename = file
            filesize = os.path.getsize(os.path.join(target_dir, filename))
            is_dir = os.path.isdir(os.path.join(target_dir, filename))
            return_items.append(f"- {filename}: file_size={filesize} bytes, is_dir={is_dir}")
        return "\n".join(return_items)

    except:
        return f'Error: Could not access contents of directory "{directory}".'