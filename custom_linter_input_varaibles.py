import os
import argparse
import re
import sys


def check_line_length(file_path, max_length):
    errors = 0

    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if len(line) > max_length:
                print(f"{file_path}:{i+1}: Line exceeds {max_length} characters")
                errors += 1
    return errors


def check_function_arguments(file_path, max_args):
    errors = 0
    function_regex = re.compile(r'^\s*def\s+\w+\((.*?)\)\s*:')
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            match = function_regex.match(line)
            if match:
                args = match.group(1).split(',')
                if len(args) > max_args:
                    print(f"{file_path}:{i+1}: Function has more than {max_args} arguments")
                    errors += 1
    return errors


def lint_directory(directory, max_line_length, max_args):
    total_errors = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_errors += check_line_length(file_path, max_line_length)
                total_errors += check_function_arguments(file_path, max_args)
    return total_errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom Linter")
    parser.add_argument("directories", nargs='+', help="Directories to lint")
    parser.add_argument("--max-line-length", type=int, default=88, help="Max line length")
    parser.add_argument("--max-args", type=int, default=5, help="Max number of arguments in functions")

    args = parser.parse_args()

    total_errors = 0
    for directory in args.directories:
        total_errors += lint_directory(directory, args.max_line_length, args.max_args)
    
    if total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)
