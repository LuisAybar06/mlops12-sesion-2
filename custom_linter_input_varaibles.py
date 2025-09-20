# Importación de módulos necesarios para trabajar con el sistema de archivos, expresiones regulares y manejo de argumentos
import os  # Para interactuar con el sistema de archivos (recorrer directorios, obtener archivos)
import argparse  # Para manejar los argumentos que se pasan al script desde la línea de comandos
import re  # Para trabajar con expresiones regulares, necesarias para analizar las funciones y las líneas de código
import sys  # Para interactuar con el sistema (como salir del script con códigos de estado)

# Función que comprueba si alguna línea de un archivo excede la longitud máxima de caracteres permitidos
def check_line_length(file_path, max_length):
    errors = 0  # Inicializa un contador para los errores encontrados
    # Abre el archivo en modo lectura
    with open(file_path, 'r') as file:
        # Recorre cada línea del archivo, obteniendo el índice (i) y el contenido de la línea
        for i, line in enumerate(file):
            # Si la longitud de la línea es mayor que el máximo permitido (max_length)
            if len(line) > max_length:
                # Imprime un mensaje de error con el archivo, la línea y el número de caracteres excedentes
                print(f"{file_path}:{i+1}: Line exceeds {max_length} characters")
                # Incrementa el contador de errores
                errors += 1
    # Devuelve el número total de errores encontrados en el archivo
    return errors

# Función que comprueba si alguna función tiene más de un número máximo de argumentos
def check_function_arguments(file_path, max_args):
    errors = 0  # Inicializa un contador para los errores encontrados
    # Compila una expresión regular para detectar definiciones de funciones
    # Esta regex busca líneas que empiecen con "def", seguidas por el nombre de la función, paréntesis y argumentos
    function_regex = re.compile(r'^\s*def\s+\w+\((.*?)\)\s*:')  
    # Abre el archivo en modo lectura
    with open(file_path, 'r') as file:
        # Recorre cada línea del archivo, obteniendo el índice (i) y el contenido de la línea
        for i, line in enumerate(file):
            # Intenta hacer coincidir la línea con la expresión regular para detectar definiciones de funciones
            match = function_regex.match(line)
            # Si hay una coincidencia (es una definición de función)
            if match:
                # Obtiene los argumentos de la función (todo lo que está entre paréntesis)
                args = match.group(1).split(',')
                # Si la cantidad de argumentos excede el número máximo permitido (max_args)
                if len(args) > max_args:
                    # Imprime un mensaje de error con el archivo, la línea y el número de argumentos excesivos
                    print(f"{file_path}:{i+1}: Function has more than {max_args} arguments")
                    # Incrementa el contador de errores
                    errors += 1
    # Devuelve el número total de errores encontrados en el archivo
    return errors

# Función que recorre un directorio y verifica todos los archivos Python en busca de errores de formato
def lint_directory(directory, max_line_length, max_args):
    total_errors = 0  # Inicializa un contador para los errores totales encontrados en el directorio
    # Recorre todos los archivos en el directorio y sus subdirectorios
    for root, _, files in os.walk(directory):
        # Recorre cada archivo en el directorio
        for file in files:
            # Si el archivo tiene extensión .py (es un archivo Python)
            if file.endswith('.py'):
                # Obtiene la ruta completa del archivo
                file_path = os.path.join(root, file)
                # Llama a las funciones de verificación de longitud de línea y número de argumentos
                # y acumula los errores encontrados
                total_errors += check_line_length(file_path, max_line_length)
                total_errors += check_function_arguments(file_path, max_args)
    # Devuelve el número total de errores encontrados en el directorio
    return total_errors

# Bloque principal del script
if __name__ == "__main__":
    # Crea un objeto parser que maneja los argumentos que se pasan al script desde la línea de comandos
    parser = argparse.ArgumentParser(description="Custom Linter")  # Descripción del script
    # Añade un argumento para especificar uno o más directorios que se desean analizar
    parser.add_argument("directories", nargs='+', help="Directories to lint")
    # Añade un argumento opcional para especificar la longitud máxima de las líneas
    parser.add_argument("--max-line-length", type=int, default=88, help="Max line length")  # Valor predeterminado de 88
    # Añade un argumento opcional para especificar el número máximo de argumentos en las funciones
    parser.add_argument("--max-args", type=int, default=5, help="Max number of arguments in functions")  # Valor predeterminado de 5



# En la línea de comandos:
# Cuando usas --max-line-length en el comando, el argumento que se pasa es una cadena de texto con guiones (--max-line-length). Este formato con guiones es común en las herramientas de línea de comandos para separar palabras en los nombres de los parámetros.

# En el código Python (con argparse):
# Cuando pasas un argumento con guiones (--max-line-length), Python los convierte internamente en nombres de variables con guiones bajos (max_line_length). Esto es porque en Python, los nombres de las variables o atributos de los objetos no pueden contener guiones (-), pero sí pueden contener guiones bajos (_).




    # Analiza los argumentos pasados al script y los guarda en 'args'
    args = parser.parse_args()

    # Inicializa el contador total de errores
    total_errors = 0
    # Recorre todos los directorios especificados como argumento en la línea de comandos
    for directory in args.directories:
        # Llama a la función que procesa el directorio y acumula los errores encontrados
        total_errors += lint_directory(directory, args.max_line_length, args.max_args)
    
    # Si se encontraron errores (total_errors > 0), termina el script con código de salida 1
    # Esto indica que hubo problemas con los archivos
    if total_errors > 0:
        sys.exit(1)
    # Si no se encontraron errores, termina el script con código de salida 0
    # Esto indica que todo está correcto
    else:
        sys.exit(0)
