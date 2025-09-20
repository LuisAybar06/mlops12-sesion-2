import os  # Módulo para interactuar con el sistema de archivos (carpetas, archivos).
import ast  # Módulo para analizar el código fuente de Python y convertirlo en un árbol de sintaxis abstracta (AST).
import re  # Módulo para expresiones regulares.
import sys  # Módulo para interactuar con el sistema (como argumentos de línea de comando y salida del programa).
import nbformat  # Módulo para leer y escribir archivos de notebooks Jupyter (formato .ipynb).
from nbconvert import PythonExporter  # Módulo para convertir notebooks Jupyter a scripts Python.
from radon.complexity import cc_visit  # Función de la librería Radon para calcular la complejidad ciclomática de un código.



def convert_notebook_to_script(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:  # Abre el archivo notebook en modo lectura.
        notebook_content = nbformat.read(f, as_version=4)  # Lee el contenido del notebook en formato JSON.
    exporter = PythonExporter()  # Crea un exportador que convierte el notebook a un script Python.
    script, _ = exporter.from_notebook_node(notebook_content)  # Convierte el contenido del notebook a un script.
    return script  # Devuelve el script generado.



def check_cyclomatic_complexity(file_content, file_path, max_complexity=1):
    print(f"Checking file: {file_path}")  # Muestra el archivo que se está verificando.
    errors = 0  # Inicializa el contador de errores.
    tree = ast.parse(file_content)  # Convierte el contenido del archivo en un árbol de sintaxis abstracta (AST).
    
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]  # Encuentra todas las funciones en el código.
    
    for func in functions:  # Recorre todas las funciones del archivo.
        complexities = cc_visit(func)  # Calcula la complejidad ciclomática para cada función.
        for complexity in complexities:
            if complexity.complexity > max_complexity:  # Si la complejidad excede el umbral máximo.
                print(f"{file_path}: Function '{func.name}' has a complexity of {complexity.complexity}, which exceeds the threshold of {max_complexity}")  # Muestra el mensaje de error.
                errors += 1  # Incrementa el contador de errores.

    return errors  # Devuelve la cantidad de errores encontrados.




def check_long_functions(file_content, file_path, max_lines=50):
    print(f"Checking file: {file_path}")  # Muestra el archivo que se está verificando.
    errors = 0  # Inicializa el contador de errores.
    tree = ast.parse(file_content)  # Convierte el contenido del archivo en un árbol de sintaxis abstracta (AST).
    
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]  # Encuentra todas las funciones en el código.
    
    for func in functions:  # Recorre todas las funciones.
        lines = len(func.body)  # Cuenta la cantidad de líneas en el cuerpo de la función.
        if lines > max_lines:  # Si la función tiene más líneas que el umbral máximo.
            print(f"{file_path}: Function '{func.name}' has {lines} lines, which exceeds the threshold of {max_lines}")  # Muestra el mensaje de error.
            errors += 1  # Incrementa el contador de errores.

    return errors  # Devuelve la cantidad de errores encontrados.



def check_naming_conventions(file_content, file_path):
    print(f"Checking file: {file_path}")  # Muestra el archivo que se está verificando.
    errors = 0  # Inicializa el contador de errores.
    snake_case = re.compile(r'^[a-z_][a-z0-9_]*$')  # Expresión regular para verificar el formato snake_case en los nombres.
    special_cases = {"NamedTuple", "Optional", "List", "Dict", "Tuple", "Union", "Any", "Callable", "TypeVar", "Generic", "Exception"}  # Casos especiales que no necesitan seguir snake_case.
    
    tree = ast.parse(file_content)  # Convierte el contenido del archivo en un árbol de sintaxis abstracta (AST).

    # Recolecta todos los nombres importados en el archivo.
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):  # Si es una declaración de importación.
            for alias in node.names:
                imported_names.add(alias.name.split('.')[0])  # Agrega el nombre del módulo importado.
        elif isinstance(node, ast.ImportFrom):  # Si es una importación desde un módulo específico.
            for alias in node.names:
                imported_names.add(alias.name.split('.')[0])  # Agrega el nombre del módulo importado.

    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]  # Extrae los nombres de las funciones.
    variables = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]  # Extrae los nombres de las variables.
    
    # Verifica que los nombres de las funciones y las variables sigan la convención snake_case.
    for func in functions:
        if not snake_case.match(func):  # Si el nombre de la función no sigue snake_case.
            print(f"{file_path}: Function name '{func}' does not follow PEP 8 naming conventions")  # Muestra el mensaje de error.
            errors += 1  # Incrementa el contador de errores.
    
    for var in variables:
        if not snake_case.match(var) and var not in special_cases and var not in imported_names:  # Si la variable no sigue snake_case y no está en los casos especiales o importaciones.
            print(f"{file_path}: Variable name '{var}' does not follow PEP 8 naming conventions")  # Muestra el mensaje de error.
            errors += 1  # Incrementa el contador de errores.

    return errors  # Devuelve la cantidad de errores encontrados.



def lint_file(file_path, max_line_length):
    errors = 0  # Inicializa el contador de errores.
    if file_path.endswith('.ipynb'):  # Si el archivo es un notebook Jupyter.
        file_content = convert_notebook_to_script(file_path)  # Convierte el notebook a script Python.
    else:
        with open(file_path, 'r', encoding='utf-8') as file:  # Si el archivo es un script Python.
            file_content = file.read()  # Lee el contenido del archivo.
    
    # Ejecuta las verificaciones de complejidad ciclomática, funciones largas y convenciones de nombres.
    errors += check_cyclomatic_complexity(file_content, file_path)
    errors += check_long_functions(file_content, file_path, max_line_length)
    errors += check_naming_conventions(file_content, file_path)
    
    return errors  # Devuelve la cantidad total de errores encontrados en el archivo.



def lint_directory(directory, max_line_length):
    total_errors = 0  # Inicializa el contador total de errores.
    for root, _, files in os.walk(directory):  # Recorre todos los archivos en el directorio y subdirectorios.
        for file in files:
            if file.endswith('.ipynb'):  # Si el archivo es un notebook Jupyter.
                file_path = os.path.join(root, file)  # Construye la ruta completa del archivo.
                total_errors += lint_file(file_path, max_line_length)  # Llama a la función lint_file para verificar el archivo.
    return total_errors  # Devuelve el total de errores encontrados en el directorio.



if __name__ == "__main__":  # Si el script se ejecuta directamente.
    import argparse  # Importa el módulo para parsear argumentos de línea de comandos.

    parser = argparse.ArgumentParser(description="Custom Linter")  # Crea un objeto para manejar los argumentos de línea de comandos.
    parser.add_argument("directories", nargs='+', help="Directories to lint")  # Argumento para pasar directorios a analizar.
    parser.add_argument("--max-line-length", type=int, default=88, help="Max line length")  # Argumento para especificar el máximo de caracteres por línea.

    args = parser.parse_args()  # Parsea los argumentos de la línea de comandos.

    total_errors = 0  # Inicializa el contador total de errores.
    for directory in args.directories:  # Recorre todos los directorios proporcionados.
        total_errors += lint_directory(directory, args.max_line_length)  # Llama a la función para verificar cada directorio.
    
    if total_errors > 0:  # Si hay errores, termina el programa con código de error 1.
        sys.exit(1)
    else:  # Si no hay errores, termina el programa con código de éxito 0.
        sys.exit(0)
