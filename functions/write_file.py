import os

from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write content to a file in a specified path relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to the file to be written to, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content that will be written to the file",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    working_file_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_file_abs, file_path))
    valid_target_file = os.path.commonpath([working_file_abs, target_file]) == working_file_abs
    if not valid_target_file:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{file_path}" as it is a directory'
    
    os.makedirs(os.path.dirname(target_file), exist_ok=True)

    with open(target_file, 'w') as file:
        file.write(content)
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
