import os
import argparse
import re
import sys



def check_black (file_path):
    errors = 0
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

        for i in range(2, len(lines)):

            if re.match(r'^\s*(class|def|if|for|while)', lines[i]):

                if not re.match(r'^\s*', lines[i-1]) or not re.match(r'^\s*', lines[i-2]):

                    print(f"{file_path}:{i+1}: Expected 2 black line befone block definition")
                    errors += 1

                elif re.match(r'^\s*', lines[i-3]):
                    print(f"{file_path}:{i+1}: Too many line befone block definition")
                    errors += 1

    return errors



def lint_directory(directory):
    total_error = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswitch('.py'):
                file_path = os.path.join(root, file)
                total_error += check_black(file_path)

    return total_error


if __name__=='__main__':

    parser = argparse.ArgumentParser(description="Custom linter")
    parser.add_argument("directories", nargs='+', help="Directories to lint")

    args = parser.parse_args()

    total_errors = 0

    for directory in args.directories:
        total_errors += lint_directory(directory)

    
    if total_errors > 0:
        sys.exit(1)

    else:
        sys.exit(0)
