import os

MAX_CHARS = 10000

def get_file_content(working_directory, file_path):
    try:
        working_file_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_file_abs, file_path))
        valid_target_file = os.path.commonpath([working_file_abs, target_file]) == working_file_abs
        if not valid_target_file:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory.'
        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        with open(target_file, 'r') as file:
            content = file.read(MAX_CHARS)  # Read up to 10,000 characters
            if file.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'

        return content

    except:
        return f'Error: Could not read file contents from "{file_path}".'