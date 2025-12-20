import subprocess

try:
    output = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
    print(output.decode())
except FileNotFoundError:
    print("Java no está accesible desde este entorno virtual.")
