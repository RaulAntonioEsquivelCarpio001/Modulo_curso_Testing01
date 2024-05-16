from flask import *
import pymysql

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



# Ruta para editar la factura
@app.route('/editar_factura/<numero_factura>', methods=['GET', 'POST'])
def editar_factura(numero_factura):
    if request.method == 'GET':
        try:
            # Obtener los datos de la factura a editar desde la base de datos
            with db.cursor() as cursor:
                # Consulta para obtener los detalles de la factura
                cursor.execute("SELECT * FROM Cuerpo_Factura WHERE Numero_Factura = %s", (numero_factura,))
                detalles_factura = cursor.fetchall()

                # Consulta para obtener la factura
                cursor.execute("SELECT * FROM Cabecera_Factura WHERE Numero_Factura = %s", (numero_factura,))
                factura = cursor.fetchone()

            # Obtener la lista de clientes desde la base de datos
            with db.cursor() as cursor:
                cursor.callproc('SeleccionarClientes')
                clientes = cursor.fetchall()

            # Obtener la lista de vendedores desde la base de datos
            with db.cursor() as cursor:
                cursor.callproc('SeleccionarVendedores')
                vendedores = cursor.fetchall()

            # Obtener la lista de artículos desde la base de datos
            with db.cursor() as cursor:
                cursor.callproc('SeleccionarArticulos')
                articulos = cursor.fetchall()

            # Renderizar la plantilla editar.html con los datos obtenidos
            return render_template('editar_factura.html', factura=factura, detalles_factura=detalles_factura, clientes=clientes, vendedores=vendedores, articulos=articulos)
        except Exception as e:
            return render_template('error.html', error=str(e))
    elif request.method == 'POST':
        # Obtener los datos actualizados del formulario
        numero_factura = request.form['numero_factura']
        fecha_factura = request.form['fecha_factura']
        ruc_cliente = request.form['ruc_cliente']
        codigo_vendedor = request.form['codigo_vendedor']
        subtotal = request.form['subtotal']
        igv = request.form['igv']
        total_factura = request.form['total_factura']

        # Obtener los detalles del cuerpo de la factura
        detalles_factura = []
        for key, value in request.form.items():
            if key.startswith('articulo_'):
                codigo_item = value
                cantidad = request.form['cantidad_' + key.split('_')[1]]
                precio_venta = request.form['precio_' + key.split('_')[1]]
                detalles_factura.append((codigo_item, cantidad, precio_venta))

        # Actualizar los datos en la base de datos
        try:
            with db.cursor() as cursor:
                # Actualizar la factura en la tabla Cabecera_Factura
                cursor.execute("UPDATE Cabecera_Factura SET Fecha_Factura=%s, RUC_Cliente=%s, Codigo_Vendedor=%s, Subtotal=%s, IGV=%s, Total_Factura=%s WHERE Numero_Factura=%s", (fecha_factura, ruc_cliente, codigo_vendedor, subtotal, igv, total_factura, numero_factura))
                
                # Eliminar los registros existentes de Cuerpo_Factura para esta factura
                cursor.execute("DELETE FROM Cuerpo_Factura WHERE Numero_Factura=%s", (numero_factura,))
                
                # Insertar los nuevos detalles de la factura en la tabla Cuerpo_Factura
                for detalle in detalles_factura:
                    cursor.execute("INSERT INTO Cuerpo_Factura (Numero_Factura, Codigo_Item, Cantidad, Precio_Venta) VALUES (%s, %s, %s, %s)", (numero_factura, detalle[0], detalle[1], detalle[2]))

            # Realizar commit para guardar los cambios
            db.commit()
            # Redirigir a la página de ver factura con un mensaje de éxito
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
        nombre_vendedor = request.form['nombre_vendedor']
        apellido_vendedor = request.form['apellido_vendedor']
        try:
            with db.cursor() as cursor:
                cursor.callproc('ActualizarVendedor', (codigo_vendedor, nombre_vendedor, apellido_vendedor))
            db.commit()
            return redirect(url_for('mostrar_vendedores'))
        except pymysql.Error as e:
            return "Error al actualizar el vendedor: " + str(e)
    else:
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Vendedor WHERE Codigo_Vendedor = %s", (codigo_vendedor,))
                vendedor = cursor.fetchone()
            return render_template('editar_vendedor.html', vendedor=vendedor)
        except pymysql.Error as e:
            return "Error al obtener el vendedor: " + str(e)

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


if __name__ == '__main__':
    app.run(debug=True)
