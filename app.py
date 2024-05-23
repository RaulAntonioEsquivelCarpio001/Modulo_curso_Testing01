from flask import *
import pymysql
import json


app = Flask(__name__)

# Configura la conexión a la base de datos
db = pymysql.connect(host='localhost',
                     user='root',
                     password='EsquivelIntiPirat3s',
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

# Ruta para la página de generar factura
@app.route('/generar_factura')
def generar_factura():
    # Obtener la lista de clientes desde la base de datos
    try:
        with db.cursor() as cursor:
            cursor.callproc('SeleccionarClientes')
            clientes = cursor.fetchall()
    except pymysql.Error as e:
        return render_template('error.html', error=str(e))

    # Obtener la lista de vendedores desde la base de datos
    try:
        with db.cursor() as cursor:
            cursor.callproc('SeleccionarVendedores')
            vendedores = cursor.fetchall()
    except pymysql.Error as e:
        return render_template('error.html', error=str(e))

    # Obtener la lista de artículos desde la base de datos
    try:
        with db.cursor() as cursor:
            cursor.callproc('SeleccionarArticulos')
            articulos = cursor.fetchall()
    except pymysql.Error as e:
        return render_template('error.html', error=str(e))
    
    return render_template('generar_factura.html', clientes=clientes, vendedores=vendedores, articulos=articulos)


# Ruta para guardar la factura
@app.route('/guardar_factura', methods=['POST'])
def guardar_factura():
    # Obtener los datos del formulario
    numero_factura = request.form['numero_factura']
    fecha_factura = request.form['fecha_factura']
    ruc_cliente = request.form['ruc_cliente']
    codigo_vendedor = request.form['codigo_vendedor']
    subtotal = request.form['subtotal']
    igv = request.form['igv']
    total_factura = request.form['total_factura']
    
    # Obtener los detalles del cuerpo de la factura
    detalles_articulos = zip(request.form.getlist('articulo[]'), request.form.getlist('cantidad[]'), request.form.getlist('precio[]'))

    # Guardar los datos en la base de datos
    try:
        with db.cursor() as cursor:
            # Insertar datos en la tabla Cabecera_Factura
            cursor.execute("INSERT INTO Cabecera_Factura (Numero_Factura, Fecha_Factura, RUC_Cliente, Codigo_Vendedor, Subtotal, IGV, Total_Factura) VALUES (%s, %s, %s, %s, %s, %s, %s)", (numero_factura, fecha_factura, ruc_cliente, codigo_vendedor, subtotal, igv, total_factura))
            
            # Insertar datos en la tabla Cuerpo_Factura
            for articulo in detalles_articulos:
                cursor.execute("INSERT INTO Cuerpo_Factura (Numero_Factura, Codigo_Item, Cantidad, Precio_Venta) VALUES (%s, %s, %s, %s)", (numero_factura, articulo[0], articulo[1], articulo[2]))

        # Realizar commit para guardar los cambios
        db.commit()
        # Redirigir al índice con un mensaje de éxito
        return "Factura guardada exitosamente. <a href='/'>Regresar al Inicio</a>"
    except pymysql.Error as e:
        # En caso de error, hacer rollback y mostrar mensaje de error
        db.rollback()
        return "Error al guardar la factura: " + str(e)

@app.route('/eliminar_factura/<numero_factura>')
def eliminar_factura(numero_factura):
    try:
        with db.cursor() as cursor:
            # Eliminar los registros de la tabla Cuerpo_Factura para esta factura
            cursor.execute("DELETE FROM Cuerpo_Factura WHERE Numero_Factura = %s", (numero_factura,))
            # Eliminar la fila correspondiente en la tabla Cabecera_Factura
            cursor.execute("DELETE FROM Cabecera_Factura WHERE Numero_Factura = %s", (numero_factura,))
        # Confirmar la transacción
        db.commit()
        # Redirigir a la página de ver facturas
        return redirect(url_for('ver_facturas'))
    except pymysql.Error as e:
        # En caso de error, hacer rollback y mostrar mensaje de error
        db.rollback()
        return render_template('error.html', error=str(e))


# Ruta para mostrar los vendedores
@app.route('/vendedores')
def mostrar_vendedores():
    try:
        with db.cursor() as cursor:
            cursor.callproc('SeleccionarVendedores')
            vendedores = cursor.fetchall()
        return render_template('vendedores.html', vendedores=vendedores)
    except pymysql.Error as e:
        return "Error al obtener los vendedores de la base de datos: " + str(e)

# Ruta para eliminar un vendedor
@app.route('/eliminar_vendedor/<codigo_vendedor>')
def eliminar_vendedor(codigo_vendedor):
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Vendedor WHERE Codigo_Vendedor = %s", (codigo_vendedor,))
        db.commit()
        return redirect(url_for('mostrar_vendedores'))
    except pymysql.Error as e:
        return "Error al eliminar el vendedor: " + str(e)

# Ruta para editar un vendedor
@app.route('/editar_vendedor/<codigo_vendedor>', methods=['GET', 'POST'])
def editar_vendedor(codigo_vendedor):
    if request.method == 'POST':
        try:
            # Obtener los nuevos datos del formulario
            nuevo_nombre = request.form['nuevo_nombre']
            nuevo_apellido = request.form['nuevo_apellido']

            # Llamar al procedimiento almacenado para actualizar el vendedor en la base de datos
            with db.cursor() as cursor:
                cursor.callproc('ActualizarVendedor', (codigo_vendedor, nuevo_nombre, nuevo_apellido))
                db.commit()

            # Redireccionar a la página de vendedores después de la edición exitosa
            return redirect(url_for('vendedores'))
        except Exception as e:
            # Manejar cualquier error y mostrar una página de error
            return render_template('error.html', error=str(e))
    elif request.method == 'GET':
        try:
            # Obtener los datos del vendedor a editar desde la base de datos
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Vendedor WHERE Codigo_Vendedor = %s", (codigo_vendedor,))
                vendedor = cursor.fetchone()

            # Renderizar la plantilla editar_vendedor.html con los datos obtenidos
            return render_template('editar_vendedor.html', vendedor=vendedor)
        except Exception as e:
            return render_template('error.html', error=str(e))

# Ruta para agregar un nuevo vendedor
@app.route('/agregar_vendedor', methods=['GET', 'POST'])
def agregar_vendedor():
    if request.method == 'POST':
        codigo_vendedor = request.form['codigo_vendedor']
        nombre_vendedor = request.form['nombre_vendedor']
        apellido_vendedor = request.form['apellido_vendedor']
        try:
            with db.cursor() as cursor:
                cursor.callproc('InsertarVendedor', (codigo_vendedor, nombre_vendedor, apellido_vendedor))
            db.commit()
            return redirect(url_for('mostrar_vendedores'))
        except pymysql.Error as e:
            return "Error al agregar el vendedor: " + str(e)
    else:
        return render_template('agregar_vendedor.html')

@app.route('/articulo')
def mostrar_articulos():
    try:
        with db.cursor() as cursor:
            cursor.callproc('SeleccionarArticulos')
            articulos = cursor.fetchall()
        return render_template('articulo.html', articulos=articulos)
    except pymysql.Error as e:
        return "Error al obtener los artículos de la base de datos: " + str(e)

# Ruta para eliminar un artículo
@app.route('/eliminar_articulo/<codigo_item>')
def eliminar_articulo(codigo_item):
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Articulo WHERE Codigo_Item = %s", (codigo_item,))
        db.commit()
        return redirect(url_for('mostrar_articulos'))
    except pymysql.Error as e:
        return "Error al eliminar el artículo: " + str(e)

# Ruta para editar un artículo
@app.route('/editar_articulo/<codigo_item>', methods=['GET', 'POST'])
def editar_articulo(codigo_item):
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        try:
            with db.cursor() as cursor:
                cursor.callproc('ActualizarArticulo', (codigo_item, descripcion, precio))
            db.commit()
            return redirect(url_for('mostrar_articulos'))
        except pymysql.Error as e:
            return "Error al actualizar el artículo: " + str(e)
    else:
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Articulo WHERE Codigo_Item = %s", (codigo_item,))
                articulo = cursor.fetchone()
            return render_template('editar_articulo.html', articulo=articulo)
        except pymysql.Error as e:
            return "Error al obtener el artículo: " + str(e)

# Ruta para agregar un nuevo artículo
@app.route('/agregar_articulo', methods=['GET', 'POST'])
def agregar_articulo():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        try:
            with db.cursor() as cursor:
                cursor.callproc('InsertarArticulo', (descripcion, precio))
            db.commit()
            return redirect(url_for('mostrar_articulos'))
        except pymysql.Error as e:
            return "Error al agregar el artículo: " + str(e)
    else:
        return render_template('agregar_articulo.html')

# Ruta para mostrar los clientes
@app.route('/clientes')
def mostrar_clientes():
    try:
        with db.cursor() as cursor:
            cursor.callproc('SeleccionarClientes')
            clientes = cursor.fetchall()
        return render_template('clientes.html', clientes=clientes)
    except pymysql.Error as e:
        return "Error al obtener los clientes de la base de datos: " + str(e)

# Ruta para eliminar un cliente
@app.route('/eliminar_cliente/<ruc_cliente>')
def eliminar_cliente(ruc_cliente):
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Cliente WHERE RUC_Cliente = %s", (ruc_cliente,))
        db.commit()
        return redirect(url_for('mostrar_clientes'))
    except pymysql.Error as e:
        return "Error al eliminar el cliente: " + str(e)

# Ruta para editar un cliente
@app.route('/editar_cliente/<ruc_cliente>', methods=['GET', 'POST'])
def editar_cliente(ruc_cliente):
    if request.method == 'POST':
        nombre_cliente = request.form['nombre_cliente']
        apellido_cliente = request.form['apellido_cliente']
        direccion_cliente = request.form['direccion_cliente']
        telefono_cliente = request.form['telefono_cliente']
        try:
            with db.cursor() as cursor:
                cursor.callproc('ActualizarCliente', (ruc_cliente, nombre_cliente, apellido_cliente, direccion_cliente, telefono_cliente))
            db.commit()
            return redirect(url_for('mostrar_clientes'))
        except pymysql.Error as e:
            return "Error al actualizar el cliente: " + str(e)
    else:
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Cliente WHERE RUC_Cliente = %s", (ruc_cliente,))
                cliente = cursor.fetchone()
            return render_template('editar_cliente.html', cliente=cliente)
        except pymysql.Error as e:
            return "Error al obtener el cliente: " + str(e)



# Ruta para agregar un nuevo cliente
@app.route('/agregar_cliente', methods=['GET', 'POST'])
def agregar_cliente():
    if request.method == 'POST':
        ruc_cliente = request.form['ruc_cliente']
        nombre_cliente = request.form['nombre_cliente']
        apellido_cliente = request.form['apellido_cliente']
        direccion_cliente = request.form['direccion_cliente']
        telefono_cliente = request.form['telefono_cliente']
        try:
            with db.cursor() as cursor:
                cursor.callproc('InsertarCliente', (ruc_cliente, nombre_cliente, apellido_cliente, direccion_cliente, telefono_cliente))
            db.commit()
            return redirect(url_for('mostrar_clientes'))
        except pymysql.Error as e:
            return "Error al agregar el cliente: " + str(e)
    else:
        return render_template('agregar_cliente.html')

@app.route('/editar_factura/<numero_factura>', methods=['GET', 'POST'])
def editar_factura(numero_factura):
    try:
        if request.method == 'POST':
            # Obtener datos del formulario
            fecha_factura = request.form['fecha_factura']
            ruc_cliente = request.form['ruc_cliente']
            codigo_vendedor = request.form['codigo_vendedor']
            subtotal = request.form['subtotal']
            igv = request.form['igv']
            total_factura = request.form['total_factura']
            
            articulos = request.form.getlist('articulo[]')
            cantidades = request.form.getlist('cantidad[]')
            precios = request.form.getlist('precio[]')
            
            # Actualizar cabecera de la factura
            with db.cursor() as cursor:
                sql_cabecera = """
                    UPDATE Cabecera_Factura 
                    SET Fecha_Factura = %s, RUC_Cliente = %s, Codigo_Vendedor = %s, Subtotal = %s, IGV = %s, Total_Factura = %s
                    WHERE Numero_Factura = %s
                """
                cursor.execute(sql_cabecera, (fecha_factura, ruc_cliente, codigo_vendedor, subtotal, igv, total_factura, numero_factura))
                
                # Eliminar los detalles actuales de la factura
                sql_delete_cuerpo = "DELETE FROM Cuerpo_Factura WHERE Numero_Factura = %s"
                cursor.execute(sql_delete_cuerpo, (numero_factura,))
                
                # Insertar los nuevos detalles de la factura
                for articulo, cantidad, precio in zip(articulos, cantidades, precios):
                    sql_cuerpo = """
                        INSERT INTO Cuerpo_Factura (Numero_Factura, Codigo_Item, Cantidad, Precio_Venta)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_cuerpo, (numero_factura, articulo, cantidad, precio))
                
                db.commit()
                
            return redirect(url_for('ver_facturas'))
        
        else:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                # Obtener la cabecera de la factura
                sql_cabecera = "SELECT * FROM Cabecera_Factura WHERE Numero_Factura = %s"
                cursor.execute(sql_cabecera, (numero_factura,))
                factura = cursor.fetchone()
                
                # Obtener los detalles de la factura
                sql_detalles = """
                    SELECT cf.*, a.Descripcion 
                    FROM Cuerpo_Factura cf
                    JOIN Articulo a ON cf.Codigo_Item = a.Codigo_Item
                    WHERE cf.Numero_Factura = %s
                """
                cursor.execute(sql_detalles, (numero_factura,))
                detalles_factura = cursor.fetchall()
                
                # Obtener la lista de clientes
                sql_clientes = "SELECT * FROM Cliente"
                cursor.execute(sql_clientes)
                clientes = cursor.fetchall()
                
                # Obtener la lista de vendedores
                sql_vendedores = "SELECT * FROM Vendedor"
                cursor.execute(sql_vendedores)
                vendedores = cursor.fetchall()
                
                # Obtener la lista de artículos
                sql_articulos = "SELECT * FROM Articulo"
                cursor.execute(sql_articulos)
                articulos = cursor.fetchall()
                
            return render_template('editar_factura.html', factura=factura, detalles_factura=detalles_factura, clientes=clientes, vendedores=vendedores, articulos=articulos)
    
    except Exception as e:
        return str(e)
    
    
if __name__ == '__main__':
    app.run(debug=True)
