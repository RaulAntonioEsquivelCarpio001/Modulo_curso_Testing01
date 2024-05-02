-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS ventaFactura;
USE ventaFactura;

-- Tabla para almacenar informaci�n de clientes
CREATE TABLE IF NOT EXISTS Cliente (
    RUC_Cliente VARCHAR(11) PRIMARY KEY, 
    Nombre_Cliente VARCHAR(60) NOT NULL,
    Apellido_Cliente VARCHAR(60) NOT NULL,
    Direccion_Cliente VARCHAR(100),
    Telefono_Cliente VARCHAR(15)
);

-- Tabla para almacenar informaci�n de vendedores
CREATE TABLE IF NOT EXISTS Vendedor (
    Codigo_Vendedor VARCHAR(9) PRIMARY KEY, 
    Nombre_Vendedor VARCHAR(60) NOT NULL,
    Apellido_Vendedor VARCHAR(60) NOT NULL
);

-- Tabla para almacenar informaci�n de art�culos
CREATE TABLE IF NOT EXISTS Articulo (
    Codigo_Item INT PRIMARY KEY, 
    Descripcion VARCHAR(30), 
    Precio DECIMAL(6,2)
);

-- Tabla para almacenar cabeceras de factura
CREATE TABLE IF NOT EXISTS Cabecera_Factura (
    Numero_Factura INT PRIMARY KEY, 
    Fecha_Factura DATE, 
    RUC_Cliente VARCHAR(11), 
    Codigo_Vendedor VARCHAR(9), 
    Subtotal DECIMAL(6,2), 
    IGV DECIMAL(6,2), 
    Total_Factura DECIMAL(8,2), 
    FOREIGN KEY(RUC_Cliente) REFERENCES Cliente(RUC_Cliente),
    FOREIGN KEY(Codigo_Vendedor) REFERENCES Vendedor(Codigo_Vendedor)
);

-- Tabla para almacenar cuerpos de factura
CREATE TABLE IF NOT EXISTS Cuerpo_Factura (
    Numero_Factura INT, 
    Codigo_Item INT, 
    Cantidad INT, 
    Precio_Venta DECIMAL(6,2),
    FOREIGN KEY(Numero_Factura) REFERENCES Cabecera_Factura(Numero_Factura),
    FOREIGN KEY(Codigo_Item) REFERENCES Articulo(Codigo_Item),
    PRIMARY KEY(Numero_Factura, Codigo_Item)
);


-- Procedimiento almacenado para insertar un nuevo cliente
DELIMITER //
CREATE PROCEDURE InsertarCliente(
    IN p_RUC_Cliente VARCHAR(11),
    IN p_Nombre_Cliente VARCHAR(60),
    IN p_Apellido_Cliente VARCHAR(60),
    IN p_Direccion_Cliente VARCHAR(100),
    IN p_Telefono_Cliente VARCHAR(15)
)
BEGIN
    INSERT INTO Cliente (RUC_Cliente, Nombre_Cliente, Apellido_Cliente, Direccion_Cliente, Telefono_Cliente)
    VALUES (p_RUC_Cliente, p_Nombre_Cliente, p_Apellido_Cliente, p_Direccion_Cliente, p_Telefono_Cliente);
END //
DELIMITER ;

-- Procedimiento almacenado para insertar un nuevo vendedor
DELIMITER //
CREATE PROCEDURE InsertarVendedor(
    IN p_Codigo_Vendedor VARCHAR(9),
    IN p_Nombre_Vendedor VARCHAR(60),
    IN p_Apellido_Vendedor VARCHAR(60)
)
BEGIN
    INSERT INTO Vendedor (Codigo_Vendedor, Nombre_Vendedor, Apellido_Vendedor)
    VALUES (p_Codigo_Vendedor, p_Nombre_Vendedor, p_Apellido_Vendedor);
END //
DELIMITER ;

-- Disparador para evitar inserci�n de clientes duplicados
DELIMITER //
CREATE TRIGGER Cliente_Insert_Duplicate 
BEFORE INSERT ON Cliente
FOR EACH ROW
BEGIN
    DECLARE count_clientes INT;
    SELECT COUNT(*) INTO count_clientes FROM Cliente WHERE RUC_Cliente = NEW.RUC_Cliente;
    IF count_clientes > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: La inserci�n del cliente est� intentando duplicar una clave primaria.';
    END IF;
END //
DELIMITER ;

-- Disparador para evitar inserci�n de vendedores duplicados
DELIMITER //
CREATE TRIGGER Vendedor_Insert_Duplicate 
BEFORE INSERT ON Vendedor
FOR EACH ROW
BEGIN
    DECLARE count_vendedores INT;
    SELECT COUNT(*) INTO count_vendedores FROM Vendedor WHERE Codigo_Vendedor = NEW.Codigo_Vendedor;
    IF count_vendedores > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: La inserci�n del vendedor est� intentando duplicar una clave primaria.';
    END IF;
END //
DELIMITER ;

-- Procedimiento almacenado para insertar un art�culo y actualizar el inventario
DELIMITER //
CREATE PROCEDURE InsertarArticulo(
    IN p_Descripcion VARCHAR(30),
    IN p_Precio DECIMAL(6,2),
    IN p_Stock INT
)
BEGIN
    DECLARE p_Codigo_Item INT;

    -- Insertar en la tabla Articulo
    INSERT INTO Articulo (Descripcion, Precio)
    VALUES (p_Descripcion, p_Precio)
END //
DELIMITER ;

-- Disparador para evitar inserci�n de art�culos duplicados
DELIMITER //
CREATE TRIGGER Articulo_Insert_Duplicate 
BEFORE INSERT ON Articulo
FOR EACH ROW
BEGIN
    DECLARE count_articulos INT;
    SELECT COUNT(*) INTO count_articulos FROM Articulo WHERE Codigo_Item = NEW.Codigo_Item;
    IF count_articulos > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: La inserci�n del art�culo est� intentando duplicar una clave primaria.';
    END IF;
END //
DELIMITER ;

-- Disparador para verificar la existencia de un n�mero de factura en la tabla Cabecera_Factura
DELIMITER //
CREATE TRIGGER Verificar_Numero_Factura
BEFORE INSERT ON Cuerpo_Factura
FOR EACH ROW
BEGIN
    DECLARE factura_existente INT;
    SELECT COUNT(*) INTO factura_existente FROM Cabecera_Factura WHERE Numero_Factura = NEW.Numero_Factura;
    IF factura_existente = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: El n�mero de factura ingresado no existe en la tabla Cabecera_Factura.';
    END IF;
END //
DELIMITER ;

-- Procedimiento almacenado para actualizar informaci�n de un cliente
DELIMITER //
CREATE PROCEDURE ActualizarCliente(
    IN p_RUC_Cliente VARCHAR(11),
    IN p_Nombre_Cliente VARCHAR(60),
    IN p_Apellido_Cliente VARCHAR(60),
    IN p_Direccion_Cliente VARCHAR(100),
    IN p_Telefono_Cliente VARCHAR(15)
)
BEGIN
    UPDATE Cliente 
    SET Nombre_Cliente = p_Nombre_Cliente,
        Apellido_Cliente = p_Apellido_Cliente,
        Direccion_Cliente = p_Direccion_Cliente,
        Telefono_Cliente = p_Telefono_Cliente
    WHERE RUC_Cliente = p_RUC_Cliente;
END //
DELIMITER ;

-- Procedimiento almacenado para actualizar informaci�n de un vendedor
DELIMITER //
CREATE PROCEDURE ActualizarVendedor(
    IN p_Codigo_Vendedor VARCHAR(9),
    IN p_Nombre_Vendedor VARCHAR(60),
    IN p_Apellido_Vendedor VARCHAR(60)
)
BEGIN
    UPDATE Vendedor 
    SET Nombre_Vendedor = p_Nombre_Vendedor,
        Apellido_Vendedor = p_Apellido_Vendedor
    WHERE Codigo_Vendedor = p_Codigo_Vendedor;
END //
DELIMITER ;

-- Procedimiento almacenado para actualizar informaci�n de un art�culo
DELIMITER //
CREATE PROCEDURE ActualizarArticulo(
    IN p_Codigo_Item INT,
    IN p_Descripcion VARCHAR(30),
    IN p_Precio DECIMAL(6,2)
)
BEGIN
    UPDATE Articulo 
    SET Descripcion = p_Descripcion,
        Precio = p_Precio
    WHERE Codigo_Item = p_Codigo_Item;
END //
DELIMITER ;

-- Procedimiento almacenado para seleccionar todos los art�culos
DELIMITER //
CREATE PROCEDURE SeleccionarArticulos()
BEGIN
    SELECT * FROM Articulo;
END //
DELIMITER ;

-- Procedimiento almacenado para seleccionar todos los clientes
DELIMITER //
CREATE PROCEDURE SeleccionarClientes()
BEGIN
    SELECT * FROM Cliente;
END //
DELIMITER ;

-- Procedimiento almacenado para seleccionar todos los vendedores
DELIMITER //
CREATE PROCEDURE SeleccionarVendedores()
BEGIN
    SELECT * FROM Vendedor;
END //
DELIMITER 


