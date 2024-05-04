from flask import *
import pymysql

app = Flask(__name__)

# Configura la conexión a la base de datos
db = pymysql.connect(host='localhost',
                     user='root',
                     password='',
                     database='ventaFactura',
                     cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    # Función para la página principal
    return render_template('index.html')

@app.route('/ver_factura')
def ver_facturas():
    try:
        # Llama al procedimiento almacenado para seleccionar las cabeceras de las facturas
        with db.cursor() as cursor:
            cursor.callproc('SeleccionarCabecerasFacturas')
            cabeceras_facturas = cursor.fetchall()
            print(cabeceras_facturas)

        # Renderiza la plantilla HTML y pasa los datos obtenidos como contexto
        return render_template('ver_factura.html', cabeceras_facturas=cabeceras_facturas)
    except Exception as e:
        print(type(e), e)
        # Manejo de errores
        return render_template('error.html', error=str(e))

@app.route('/detalles_factura/<numero_factura>')
def detalles_factura(numero_factura):
    try:
        # Llama al procedimiento almacenado para obtener los detalles de la factura
        with db.cursor() as cursor:
            cursor.callproc('dtlleFact', (numero_factura,))
            detalles_factura = cursor.fetchall()

        # Renderiza la plantilla HTML y pasa los detalles de la factura como contexto
        return render_template('detalles_factura.html', detalles_factura=detalles_factura)
    except Exception as e:
        # Manejo de errores
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)