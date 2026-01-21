import os
import subprocess

def run_python_file(working_directory, file_path, args=None):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))
        valid_target_file = os.path.commonpath([working_directory_abs, target_file]) == working_directory_abs
        if valid_target_file is False:
                return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if os.path.isfile(target_file) is False:
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if target_file.endswith('.py') is False:
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_file]
        if args:
            command.extend(args)
        process = subprocess.run(command, capture_output=True, cwd=working_directory_abs, timeout=30, text=True)
        output_string = []
        if process.returncode != 0:
            output_string.append(f"Process exited with code {process.returncode}")
        if not process.stdout and not process.stderr:
            output_string.append("No output produced")
        else:
            if process.stdout != "":
                output_string.append(f"STDOUT:\n{process.stdout}")
            if process.stderr != "":
                output_string.append(f"STDERR:\n{process.stderr}")
        return "\n".join(output_string)
    except Exception as e:
         return f"Error: executing Python file: {e}"