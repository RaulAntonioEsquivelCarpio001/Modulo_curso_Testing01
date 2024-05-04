-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS ventaFactura;
USE ventaFactura;

-- Tabla para almacenar información de clientes
CREATE TABLE IF NOT EXISTS Cliente (
    RUC_Cliente VARCHAR(11) PRIMARY KEY, 
    Nombre_Cliente VARCHAR(60) NOT NULL,
    Apellido_Cliente VARCHAR(60) NOT NULL,
    Direccion_Cliente VARCHAR(100),
    Telefono_Cliente VARCHAR(15)
);

-- Tabla para almacenar información de vendedores
CREATE TABLE IF NOT EXISTS Vendedor (
    Codigo_Vendedor VARCHAR(9) PRIMARY KEY, 
    Nombre_Vendedor VARCHAR(60) NOT NULL,
    Apellido_Vendedor VARCHAR(60) NOT NULL
);

-- Tabla para almacenar información de artículos
CREATE TABLE IF NOT EXISTS Articulo (
    Codigo_Item INT AUTO_INCREMENT PRIMARY KEY, 
    Descripcion VARCHAR(30), 
    Precio DECIMAL(6,2)
);

-- Tabla para almacenar cabeceras de factura
CREATE TABLE IF NOT EXISTS Cabecera_Factura (
    Numero_Factura VARCHAR(30) PRIMARY KEY, 
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
    Numero_Factura VARCHAR(30), 
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

-- Disparador para evitar inserción de clientes duplicados
DELIMITER //
CREATE TRIGGER Cliente_Insert_Duplicate 
BEFORE INSERT ON Cliente
FOR EACH ROW
BEGIN
    DECLARE count_clientes INT;
    SELECT COUNT(*) INTO count_clientes FROM Cliente WHERE RUC_Cliente = NEW.RUC_Cliente;
    IF count_clientes > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: La inserción del cliente está intentando duplicar una clave primaria.';
    END IF;
END //
DELIMITER ;

-- Disparador para evitar inserción de vendedores duplicados
DELIMITER //
CREATE TRIGGER Vendedor_Insert_Duplicate 
BEFORE INSERT ON Vendedor
FOR EACH ROW
BEGIN
    DECLARE count_vendedores INT;
    SELECT COUNT(*) INTO count_vendedores FROM Vendedor WHERE Codigo_Vendedor = NEW.Codigo_Vendedor;
    IF count_vendedores > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: La inserción del vendedor está intentando duplicar una clave primaria.';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE InsertarArticulo(
    IN p_Descripcion VARCHAR(30),
    IN p_Precio DECIMAL(6,2)
)
BEGIN
    -- Insertar en la tabla Articulo
    INSERT INTO Articulo (Descripcion, Precio)
    VALUES (p_Descripcion, p_Precio);
END //
DELIMITER ;


-- Disparador para evitar inserción de artículos duplicados
DELIMITER //
CREATE TRIGGER Articulo_Insert_Duplicate 
BEFORE INSERT ON Articulo
FOR EACH ROW
BEGIN
    DECLARE count_articulos INT;
    SELECT COUNT(*) INTO count_articulos FROM Articulo WHERE Codigo_Item = NEW.Codigo_Item;
    IF count_articulos > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: La inserción del artículo está intentando duplicar una clave primaria.';
    END IF;
END //
DELIMITER ;


-- Procedimiento almacenado para actualizar información de un cliente
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

-- Procedimiento almacenado para actualizar información de un vendedor
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

-- Procedimiento almacenado para seleccionar todos los artículos
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
DELIMITER ;
DELIMITER //

CREATE PROCEDURE SeleccionarCabecerasFacturas()
BEGIN
    SELECT Numero_Factura, Fecha_Factura, Total_Factura
    FROM Cabecera_Factura;
END //

DELIMITER ;

DELIMITER //

DELIMITER //

CREATE PROCEDURE dtlleFact(
    IN p_Numero_Factura VARCHAR(30)
)
BEGIN
    SELECT 
        CF.Numero_Factura, 
        CF.Fecha_Factura, 
        C.Nombre_Cliente, 
        C.Apellido_Cliente, 
        C.Direccion_Cliente, 
        C.Telefono_Cliente,
        V.Nombre_Vendedor, 
        V.Apellido_Vendedor, 
        CF.Subtotal,
        CF.IGV,
        CF.Total_Factura, 
        AF.Descripcion AS Articulo, 
        CoF.Cantidad AS Cantidad,
        CoF.Precio_Venta AS Precio 
    FROM 
        Cabecera_Factura CF
    LEFT JOIN 
        Cliente C ON CF.RUC_Cliente = C.RUC_Cliente
    LEFT JOIN 
        Vendedor V ON CF.Codigo_Vendedor = V.Codigo_Vendedor
    JOIN 
        Cuerpo_Factura CoF ON CF.Numero_Factura = CoF.Numero_Factura
    JOIN 
        Articulo AF ON CoF.Codigo_Item = AF.Codigo_Item
    WHERE 
        CF.Numero_Factura = p_Numero_Factura;
END //

DELIMITER ;



CALL InsertarCliente('12345678901', 'Juan', 'Pérez', 'Calle Principal 123', '123456789');
CALL InsertarVendedor('71949154', 'Jackson', 'Smith');
CALL InsertarArticulo('Camisa', 25.99);
-- Insertar una factura de ejemplo
INSERT INTO Cabecera_Factura (Numero_Factura, Fecha_Factura, RUC_Cliente, Codigo_Vendedor, Subtotal, IGV, Total_Factura)
VALUES ('FACT-001', '2024-05-02', '12345678901', '71949154', 100.00, 18.00, 118.00);
-- Insertar detalles de la factura (cuerpo de la factura)
INSERT INTO Cuerpo_Factura (Numero_Factura, Codigo_Item, Cantidad, Precio_Venta)
VALUES ('FACT-001', 1, 2, 50.00);

