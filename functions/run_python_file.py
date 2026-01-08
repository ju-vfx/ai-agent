import os
import subprocess

from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a Python file in a specified path relative to the working directory with optional arguments. Captures and returns the standard output and error produced during execution.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to the Python file to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="Optional positional arguments to pass to the Python file",
            ),
        },
    ),
)

def run_python_file(working_directory, file_path, args=None):
    try:
        working_file_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_file_abs, file_path))
        valid_target_file = os.path.commonpath([working_file_abs, target_file]) == working_file_abs
        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not target_file.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python3", target_file]
        if args:
            command.extend(*args)

        process = subprocess.run(command, capture_output=True, text=True, timeout=30, cwd=working_file_abs)

        output_string = ""
        if process.returncode != 0:
            output_string += f'Process exited with code {process.returncode}\n'
        if len(process.stdout) == 0:
            process.stdout += "No output produced"
        if len(process.stderr) == 0:
            process.stderr += "No output produced"
        output_string += f"STDOUT: {process.stdout}\n"
        output_string += f"STDERR: {process.stderr}"
        return output_string
    except Exception as e:
        return f"Error: executing Python file: {e}"
