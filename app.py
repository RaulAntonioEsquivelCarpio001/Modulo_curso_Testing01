import os  # Importar el módulo os
from flask import Flask

# Importar funciones para manejar la base de datos desde setup_db.py
from setup_db import ejecutar_script_sql, conectar_bd

app = Flask(__name__)

# Ruta al script SQL
script_path = 'E:/raulproperty/UCSM/VII Semestre/Testing emplmetnacion y monitorei Ing Sistemas/Practicas Laboratorio/Fase 2/Facturacion/facturacion.sql'

# Configuración de la conexión a la base de datos MySQL
host = 'localhost'
user = 'root'
password = ''
database = 'ventaFactura'

# Verificar si la base de datos ya está creada
if not os.path.exists(database + ".sql"):
    # Si la base de datos no está creada, ejecutar el script SQL para crearla
    ejecutar_script_sql(script_path, host, user, password, database)

# Llamar a la función para establecer la conexión
conexion = conectar_bd(host, user, password, database)

# Cerrar la conexión cuando hayas terminado de usarla
if conexion:
    conexion.close()

@app.route('/')
def index():
    # Función para la página principal
    return render_template('index.html')

@app.route('/generar_factura')
def generar_factura():
    # Función para generar una factura
    return 'Generar factura'

@app.route('/ver_factura')
def ver_factura():
    # Función para ver facturas
    return 'Ver facturas'

@app.route('/articulo')
def articulo():
    # Función para administrar artículos
    return 'Administrar artículos'

@app.route('/inventario')
def inventario():
    # Función para ver el inventario
    return 'Ver inventario'

@app.route('/clientes')
def clientes():
    # Función para administrar clientes
    return 'Clientes'

@app.route('/vendedores')
def vendedores():
    # Función para administrar vendedores
    return 'Vendedores'

if __name__ == '__main__':
    app.run(debug=True)
