#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask import Flask, request, jsonify
#from flask import request

# Instalar con pip install flask-cors
from flask_cors import CORS


# Instalar con pip install mysql-connector-python
import mysql.connector

# No es necesario instalar, es parte del sistema standard de Python
import os
# import time, datetime
from datetime import datetime

#--------------------------------------------------------------------

app = Flask(__name__)

# Permitir acceso desde cualquier origen externo
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "PUT", "DELETE"]) 

#-Inicio seccion class Mensaje---------------------------------------
class Mensaje:
    
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        # El atributo .conn pertenece al objeto que se está instanciando. 
        # Representa la conexión a la base de datos MySQL. 
        # permite realizar operaciones como ejecutar consultas SQL, realizar transacciones, etc.
        # El atributo .cursor es un objeto de cursor que se utiliza para ejecutar comandos SQL en la base de datos conectada (self.conn). 
        # El cursor actúa como un "puntero" a un resultado específico en la base de datos, y se usa para ejecutar consultas y recuperar resultados.
        self.cursor = self.conn.cursor()
        # En resumen, self.conn representa la conexión a la base de datos MySQL, mientras que self.cursor representa 
        # el objeto que se utiliza para ejecutar comandos y consultas en esa conexión. 
        # Estos dos objetos son esenciales para interactuar con la base de datos desde Python mediante la librería mysql.connector.

        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, Python arrojará un error de excepción que queda capturado en esta parte. 
            # Entonces creamos la base de datos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS mensajes (
            id int(11) NOT NULL AUTO_INCREMENT,
            nombre varchar(30) NOT NULL,
            apellido varchar(30) NOT NULL,
            telefono varchar(15) NOT NULL,
            direccion VARCHAR(30) NOT NULL ,
            email varchar(60) NOT NULL,
            mensaje varchar(500) NOT NULL,
            fecha_envio datetime NOT NULL,
            leido tinyint(1) NOT NULL,
            gestion varchar(500) DEFAULT NULL,
            fecha_gestion datetime DEFAULT NULL,
            PRIMARY KEY(`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;
            ''')
        # Confirma la transacción en la base de datos.
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

               
    #----------------------------------------------------------------
    def enviar_mensaje(self, nombre, apellido, telefono, direccion, email, consulta):
        sql = "INSERT INTO mensajes(nombre, apellido, telefono, direccion, email, mensaje, fecha_envio) VALUES (%s, %s, %s, %s, %s,%s,%s)"
        fecha_envio = datetime.now()
        valores = (nombre, apellido, telefono, direccion, email, consulta, fecha_envio)
        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return True

    #----------------------------------------------------------------
    def listar_mensajes(self):
        self.cursor.execute("SELECT * FROM mensajes")
        mensajes = self.cursor.fetchall()
        return mensajes

    #----------------------------------------------------------------
    def responder_mensaje(self, id, gestion):
        fecha_gestion = datetime.now()
        sql = "UPDATE mensajes SET leido = 1, gestion = %s, fecha_gestion = %s WHERE id = %s"
        valores = (gestion, fecha_gestion, id)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def eliminar_mensaje(self, id):
        # Eliminamos un mensaje de la tabla a partir de su código
        #sql = "DELETE FROM mensajes WHERE id = %s"
        #valores = (id,)
        #self.cursor.execute(sql, valores)
        #self.conn.commit()
        #return self.cursor.rowcount > 0
        self.cursor.execute(f"DELETE FROM mensajes WHERE id = {id}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_mensaje(self, id):
        sql =f"SELECT id, nombre, apellido, telefono, direccion, email, mensaje, fecha_envio, leido, gestion, fecha_gestion FROM mensajes WHERE id = {id}"        
        self.cursor.execute(sql)
        return self.cursor.fetchone()
       
#-Fin de Seccion class mensaje----------------------------------------------------

# Creamos el objeto---------------------------------------------------------------
mensaje = Mensaje(host='JulianLucero.mysql.pythonanywhere-services.com', user='JulianLucero', password='TpfinalCaC2023', database='JulianLucero$mensajes')
#----------------------------------------------------------------------------------

#-INICIO SECCION RUTAS-------------------------------------------------------------
#-RUTA LEER CLIENTES-MENSAJES-----------------------------------------------
@app.route("/mensajes", methods=["GET"])
def listar_mensajes():
    respuesta = mensaje.listar_mensajes()
    return jsonify(respuesta)


#-RUTA AGREGAR CLIENTE+MENSAJE----------------------------------------------
@app.route("/mensajes", methods=["POST"])
def agregar_producto():
    #Recojo los datos del form
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    direccion = request.form['direccion']
    email = request.form['email']
    consulta = request.form['mensaje']  

    if mensaje.enviar_mensaje(nombre, apellido, telefono, direccion, email, consulta):
        return jsonify({"mensaje": "Mensaje agregado"}), 201
    else:
        return jsonify({"mensaje": "No fue posible registrar el mensaje"}), 400
  

#-RUTA MODIFICAR MENSAJE (gestion+leido)------------------------------------------
@app.route("/mensajes/<int:id>", methods=["PUT"])
def responder_mensaje(id):
    #Recojo los datos del form
    gestion = request.form.get("gestion")
    
    if mensaje.responder_mensaje(id, gestion):
        return jsonify({"mensaje": "Mensaje modificado"}), 200
    else:
        return jsonify({"mensaje": "Mensaje no encontrado"}), 403

#-RUTA BORRAR CLIENTES-MENSAJES----------------------------------------------------
@app.route("/mensajes/<int:id>", methods=["DELETE"])
def eliminar_mensaje(id):
    #Recojo los datos del form
    #gestion = request.form.get("gestion")
    
    if mensaje.eliminar_mensaje(id):
        return jsonify({"mensaje": "Mensaje eliminado"}), 200
    else:
        return jsonify({"mensaje": "Mensaje no encontrado"}), 404

#-FIN SECCION RUTAS--------------------------------------------------------------------

#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)


#--------------------------------------------------------------------------------


