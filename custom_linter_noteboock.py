import os
import ast
import re
import sys
import nbformat
from nbconvert import PythonExporter
from radon.complexity import cc_visit



def convert_notebook_to_script(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_content = nbformat.read(f, as_version=4)
    exporter = PythonExporter()
    script, _ = exporter.from_notebook_node(notebook_content)
    return script



def check_cyclomatic_complexity(file_content, file_path, max_complexity=1):
    print(f"Checking file: {file_path}")
    errors = 0
    tree = ast.parse(file_content)
    
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    for func in functions:
        complexities = cc_visit(func)
        for complexity in complexities:
            if complexity.complexity > max_complexity:
                print(f"{file_path}: Function '{func.name}' has a complexity of {complexity.complexity}, which exceeds the threshold of {max_complexity}")
                errors += 1

    return errors




def check_long_functions(file_content, file_path, max_lines=50):
    print(f"Checking file: {file_path}")
    errors = 0
    tree = ast.parse(file_content)
    
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    for func in functions:
        lines = len(func.body)
        if lines > max_lines:
            print(f"{file_path}: Function '{func.name}' has {lines} lines, which exceeds the threshold of {max_lines}")
            errors += 1

    return errors



def check_naming_conventions(file_content, file_path):
    print(f"Checking file: {file_path}")
    errors = 0
    snake_case = re.compile(r'^[a-z_][a-z0-9_]*$')
    special_cases = {"NamedTuple", "Optional", "List", "Dict", "Tuple", "Union", "Any", "Callable", "TypeVar", "Generic", "Exception"}
    
    tree = ast.parse(file_content)


    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name.split('.')[0])

    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    variables = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
    

    for func in functions:
        if not snake_case.match(func):
            print(f"{file_path}: Function name '{func}' does not follow PEP 8 naming conventions")
            errors += 1
    
    for var in variables:
        if not snake_case.match(var) and var not in special_cases and var not in imported_names:
            print(f"{file_path}: Variable name '{var}' does not follow PEP 8 naming conventions")
            errors += 1

    return errors



def lint_file(file_path, max_line_length):
    errors = 0
    if file_path.endswith('.ipynb'):
        file_content = convert_notebook_to_script(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()  

    errors += check_cyclomatic_complexity(file_content, file_path)
    errors += check_long_functions(file_content, file_path, max_line_length)
    errors += check_naming_conventions(file_content, file_path)
    
    return errors



def lint_directory(directory, max_line_length):
    total_errors = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.ipynb'):
                file_path = os.path.join(root, file) 
                total_errors += lint_file(file_path, max_line_length) 
    return total_errors 


if __name__ == "__main__": 
    import argparse 

    parser = argparse.ArgumentParser(description="Custom Linter") 
    parser.add_argument("directories", nargs='+', help="Directories to lint")
    parser.add_argument("--max-line-length", type=int, default=88, help="Max line length")

    args = parser.parse_args()

    total_errors = 0 
    for directory in args.directories:
        total_errors += lint_directory(directory, args.max_line_length) 
    
    if total_errors > 0:
        sys.exit(1)
    else:  
        sys.exit(0)
