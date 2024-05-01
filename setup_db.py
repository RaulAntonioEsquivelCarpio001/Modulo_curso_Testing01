import mysql.connector
import os

def ejecutar_script_sql(script_path, host, user, password, database):
    try:
        # Establecer la conexión a la base de datos MySQL
        db_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = db_connection.cursor()

        # Leer el contenido del script SQL
        with open(script_path, 'r') as file:
            script = file.read()

        # Ejecutar el script SQL
        cursor.execute(script)
        db_connection.commit()

        print("Script SQL ejecutado exitosamente.")

    except mysql.connector.Error as error:
        print("Error al ejecutar el script SQL:", error)

    finally:
        # Cerrar la conexión
        if 'db_connection' in locals() and db_connection.is_connected():
            cursor.close()
            db_connection.close()

def conectar_bd(host, user, password, database):
    try:
        # Establecer la conexión a la base de datos MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("Conexión exitosa a la base de datos.")

        return connection

    except mysql.connector.Error as error:
        print("Error al conectar a la base de datos:", error)
        return None
