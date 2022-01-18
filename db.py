import sqlite3
from sqlite3 import Error

conexion = None

def conectarDB():
    try:
        conexion = sqlite3.connect('db/cafeteria.db')
        return conexion
    except Error as e:
        print('Error al conectar con la base de datos'+e)

def desconectarDB():
    if conexion is not None:
        conexion.close()