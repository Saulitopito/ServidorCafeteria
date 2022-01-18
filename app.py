from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
import yagmail, functools, db, time
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
#importar el sqlite3 para el manejo de BD
import sqlite3
#importar el modulo de errores de sqlite3
from sqlite3 import Error

palabra = None

app = Flask(__name__)
#app.secret_key = os.urandom(24)
app.secret_key = '5fffa2e766c5f3d1a85ad8979864459a4d12b25e727ae7a78d1d8f958952a828L'

app.config['UPLOAD_FOLDER'] = 'static/img/'

#;;;;;;;;;;;;;;;;;;;;;;;,;;; Rutas;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not 'user_id' in session :
            mensaje = 2
            return render_template('Login.html', mensaje=mensaje)
        return view()
    return wrapped_view

@app.route('/')
def login():
    return render_template('Login.html')

@app.route('/acceso', methods=['GET', 'POST'])
def acceso():
	if request.method=='POST':
		conexion = db.conectarDB()
		usuario = request.form['usuario']
		clave = request.form['clave']
		cur = conexion.cursor()
		cur.execute("SELECT * FROM USUARIOS WHERE nickName=?", (usuario, ))
		resultado = cur.fetchone()
		if resultado is None:
			mensaje = 1
			return render_template('Login.html', mensaje=mensaje)
		else:
			if check_password_hash(resultado[4], clave):
				session.clear()
				session['user_id'] = resultado[0]
				session['user_name'] = resultado[1]
				session['user_user'] = resultado[2]
				session['user_rol'] = resultado[5]
				if session.get('user_rol')==1:
					return render_template('Admin.html')
				else:
					busqueda = sql_productos()
					venta = sql_num_venta()
					datos = sql_llenar_venta(venta[0])
					
					return render_template('Cajero-Venta.html', busqueda=busqueda, datos=datos, venta=venta)
			else:
				mensaje = 1
				return render_template('Login.html', mensaje=mensaje)
	else:
		return redirect(url_for('/'))

@app.route('/recuperar/')
def recuperar():
    return render_template('recuperarContrasena.html')

@app.route('/recuperacion', methods=['GET', 'POST'])
def recuperacion():
	if request.method=='POST':
		conexion = db.conectarDB()
		user = request.form['user']
		cur = conexion.cursor()
		cur.execute("SELECT * FROM USUARIOS WHERE nickName=?", (user, ))
		resultado = cur.fetchone()
		if resultado is None:
			mensaje = 2
			return render_template('recuperarContrasena.html', mensaje=mensaje)
		else:
			cur.execute("SELECT * FROM USUARIOS WHERE rol=?", (1, ))
			resultado = cur.fetchone()
			correo = resultado[3]
			#clave = resultado[4]
			yag = yagmail.SMTP('alergia.sandoval@gmail.com', 'tigres1992')
			yag.send(to=correo, subject='Recuperación de credenciales', contents='El usuario: '+user+' solicitó la actualización de su contraseña. Por favor gestionar el cambio lo más pronto posible.')
			mensaje = 1
			return render_template('recuperarContrasena.html', mensaje=mensaje)		
	else:
		return render_template('recuperarContrasena.html')

@app.route('/admin/')
@login_required
def admin():
	if session['user_rol']==0:
		mensaje = 1
		return render_template('Login.html', mensaje=mensaje)
	else:
		return render_template('Admin.html')

@app.route('/gestionProductos/')
@login_required
def gestionProductos():
	if session['user_rol']==0:
		mensaje = 1
		return render_template('Login.html', mensaje=mensaje)
	else:
		productos = sql_select_productos()
		return render_template('GestionProductos.html', productos=productos)

@app.route('/gestionUsuarios/' )
@login_required
def gestionUsuarios():
	if session['user_rol']==0:
		mensaje = 1
		return render_template('Login.html', mensaje=mensaje)
	else:
		usuarios = sql_select_usuarios()
		return render_template('GestionUsuarios.html', usuarios = usuarios)

#================================================================

#inserta un usuario
#funciona
@app.route('/crearUsuario', methods=['POST'])
@login_required
def crearUsuario():
	if request.method=='POST':
		nick = request.form['nick']
		nombre = request.form['nombre']
		rol = request.form['rol']
		correo = request.form['correo']
		clave = request.form['clave']
		con = Conexion()
		cur = con.cursor()
		cur.execute("SELECT * FROM USUARIOS WHERE nombre=?", (nombre, ))
		reg = cur.fetchone()
		if reg:
			usuarios = sql_select_usuarios()
			mensaje = 3
			return render_template('GestionUsuarios.html', usuarios = usuarios, mensaje=mensaje)
		hash_clave = generate_password_hash(clave)
		guardar_usuarios(nombre, nick, correo, hash_clave, rol)
		#guardar_usuarios(nombre, nick, correo, clave, rol)
		usuarios = sql_select_usuarios()
		mensaje = 4
		return render_template('GestionUsuarios.html', usuarios = usuarios, mensaje=mensaje)
	else:
		usuarios = sql_select_usuarios()
		return render_template('GestionUsuarios.html', usuarios = usuarios)

#edita un usuario
#funciona
@app.route('/editarUsuario', methods=['POST'])
@login_required
def editarUsuario():
	if request.method=='POST':
		nick = request.form['nickU']
		nombre = request.form['nombreU']
		correo = request.form['correoU']
		clave = request.form['claveU']
		hash_clave = generate_password_hash(clave)
		id_usuario = request.form['id_usuario']
		sql_edit_usuario(id_usuario,nick,nombre,correo,hash_clave)
		usuarios = sql_select_usuarios()
		return render_template('GestionUsuarios.html', usuarios = usuarios)
	else:
		usuarios = sql_select_usuarios()
		return render_template('GestionUsuarios.html', usuarios = usuarios)

#eliminar usuario
#funciona
@app.route('/eliminarUsuario')
@login_required
def eliminarUsuario():
		id_usuario = request.args.get('id')
		sql_delete_usuario(id_usuario)
		usuarios = sql_select_usuarios()
		return render_template('GestionUsuarios.html', usuarios=usuarios)

#inserta un producto
#funciona
@app.route('/crearProducto', methods=['POST'])
@login_required
def crearProducto():
	path = ''
	if request.method=='POST':
		nombre = request.form['nProducto']
		precio = request.form['Precio']
		descripcion = request.form['Descripcion']
		cantidad = request.form['Cantidad']
		imagen = request.files['foto']
		filename = secure_filename(imagen.filename)
		path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		imagen.save(path)
		con = Conexion()
		cur = con.cursor()
		cur.execute("SELECT * FROM PRODUCTOS WHERE nombre=?", (nombre, ))
		reg = cur.fetchone()
		if reg:
			productos = sql_select_productos()
			mensaje = 3
			return render_template('GestionProductos.html', productos = productos, mensaje=mensaje, path=path)
		guardar_productos(nombre, precio, cantidad, descripcion, filename)
		productos = sql_select_productos()
		mensaje = 4
		return render_template('GestionProductos.html', productos = productos, mensaje=mensaje)
	else:
		productos = sql_select_productos()
		return render_template('GestionProductos.html', productos = productos)

#edita un producto
#funciona
@app.route('/editarProducto', methods=['POST'])
@login_required
def editarProducto():
	if request.method=='POST':
		id_producto = request.form['nId']
		nombre = request.form['nProducto']
		precio = request.form['Precio']
		cantidad = request.form['Cantidad']
		descripcion = request.form['Descripcion']
		imagen = request.files['foto']
		filename = secure_filename(imagen.filename)
		path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		imagen.save(path)
		sql_edit_producto(id_producto,nombre,precio,cantidad,descripcion,filename)
		productos = sql_select_productos()
		return render_template('GestionProductos.html', productos = productos)
	else:
		productos = sql_select_productos()
		return render_template('GestionProductos.html', productos = productos)

#eliminar producto
#funciona
@app.route('/eliminarProducto')
@login_required
def eliminarProducto():
		id_producto = request.args.get('id')
		sql_delete_producto(id_producto)
		productos = sql_select_productos()
		return render_template('GestionProductos.html', productos=productos)

#================================================================

@app.route('/cajeroVenta/')
@login_required
def cajeroVenta():
	busqueda = sql_productos()
	venta = sql_num_venta()
	datos = sql_llenar_venta(venta[0])
	
	return render_template('Cajero-Venta.html', busqueda=busqueda, datos=datos, venta=venta)

@app.route( '/logout' )
def logout():
    session['user_id'] = None
    session['user_name'] = None
    session['user_user'] = None
    session['user_rol'] = None
    session.clear()
    return login()

@app.before_request
def load_logged_in_user():
    user_id = session.get( 'user_id' )
    if user_id is None:
      session['user_login'] = None

#============== conexion ala BD======================
def Conexion():
    try:
        con=sqlite3.connect('db/cafeteria.db')
        return con
    except Error:
        print(Error)

#--------- Para listar los usuarios-------------
def sql_select_usuarios():
        strsql = "select * from USUARIOS;"
        con = Conexion()
        cursorObj = con.cursor()
        cursorObj.execute(strsql)
        usuarios = cursorObj.fetchall()
        return usuarios

#=====Guardar usuarios================
#funciona
def guardar_usuarios(nombre,nick,correo,clave,rol):
        con=Conexion()
        cursorObj=con.cursor() # que es?
        cursorObj.execute("insert into USUARIOS(nombre,nickName,correo,clave,rol) values(?, ?, ?, ?, ?);", (nombre, nick, correo, clave, rol))
        con.commit()
        con.close()
#endGuardar


#-------------- Para editar un usuario--------------        
def sql_edit_usuario(id,nickName,nombre,correo,clave):
      con = Conexion()
      cursorObj = con.cursor()
      cursorObj.execute("update USUARIOS set  nombre = ?, nickName = ?, correo= ?, clave = ?  where id = ?;", (nombre, nickName, correo, clave, id))
      con.commit()
      con.close()

#-------------- Para Eliminar un usuario--------------        
def sql_delete_usuario(id):
        con = Conexion()
        cursorObj = con.cursor()
        cursorObj.execute("delete from USUARIOS where id = ?;", (id, ))
        con.commit()
        con.close()


#--------- Para listar los productos-------------
def sql_select_productos():
        strsql = "select * from PRODUCTOS;"
        con = Conexion()
        cursorObj = con.cursor()
        cursorObj.execute(strsql)
        productos = cursorObj.fetchall()
        return productos

#=====Guardar productos================
#funciona
def guardar_productos(nombre,precio,cantidad,descripcion,imagen):
		img = "/static/img/"+imagen
		con=Conexion()
		cursorObj=con.cursor() # que es?
		cursorObj.execute("insert into PRODUCTOS(nombre,precio,cantidad_Inv,descripcion,imagen) values(?, ?, ?, ?, ?);", (nombre, precio, cantidad, descripcion, img))
		con.commit()
		con.close()
#endGuardar


#-------------- Para editar un producto--------------        
def sql_edit_producto(id,nombre,precio,cantidad,descripcion,imagen):
      img = "/static/img/"+imagen
      con = Conexion()
      cursorObj = con.cursor()
      cursorObj.execute("update PRODUCTOS set  nombre = ?, precio = ?, cantidad_Inv= ?, descripcion = ?, imagen = ?  where id = ?;", (nombre, precio, cantidad, descripcion, img, id))
      con.commit()
      con.close()

#-------------- Para Eliminar un usuario--------------        
def sql_delete_producto(id):
        con = Conexion()
        cursorObj = con.cursor()
        cursorObj.execute("delete from PRODUCTOS where id = ?;", (id, ))
        con.commit()
        con.close()


#--------------------- Gestión de la Venta --------------------

#funciona
def sql_productos():
	sql="SELECT * FROM PRODUCTOS;"
	conexion = db.conectarDB()
	cur = conexion.cursor()
	cur.execute(sql)
	busqueda = cur.fetchall()
	return busqueda

#llama creación de línea en la tabla
#funciona
@app.route('/tablaVenta')
@login_required
def tablaVenta():
	id = request.args.get('id')
	if id:
		sql_insertar_producto_venta(id)
		venta = sql_num_venta()
		datos = sql_llenar_venta(venta[0])
		if palabra:
			busqueda = sql_busca_productos(palabra)
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
		else:
			busqueda = sql_productos()
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
	else:
		return render_template('Cajero-Venta.html')

#crea línea en tabla Ventas
#funciona
def sql_insertar_producto_venta(id_producto):
	conexion = db.conectarDB()
	cur = conexion.cursor()
	venta = "SELECT id FROM VENTAS ORDER BY VENTAS.id DESC LIMIT 1"
	cur.execute(venta)
	id_venta = cur.fetchone()
	cur.execute("SELECT precio FROM PRODUCTOS WHERE PRODUCTOS.id=?", (id_producto, ))
	valores = cur.fetchone()
	cantidad = '1'
	cur.execute("INSERT INTO REGISTRO_VENTAS (id_venta, id_producto, Cantidad, Total_Prod) VALUES (?, ?, ?, ?);", (id_venta[0], id_producto, cantidad, valores[0]))
	conexion.commit()
	conexion.close()

#funciona
#llama info de Ventas
def sql_llenar_venta(id_venta):
	conexion = db.conectarDB()
	cur = conexion.cursor()
	cur.execute("SELECT REGISTRO_VENTAS.*, PRODUCTOS.nombre, PRODUCTOS.precio FROM REGISTRO_VENTAS JOIN PRODUCTOS ON REGISTRO_VENTAS.id_producto=PRODUCTOS.id WHERE id_venta=?", (id_venta, ))
	datos = cur.fetchall()
	return datos

@app.route('/masProducto')
@login_required
def masProducto():
	id = request.args.get('id')
	cant = request.args.get('cantidad')
	val = request.args.get('valor')
	if id:
		sql_aumentar_venta(id, cant, val)
		venta = sql_num_venta()
		datos = sql_llenar_venta(venta[0])
		if palabra:
			busqueda = sql_busca_productos(palabra)
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
		else:
			busqueda = sql_productos()
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
	else:
		return render_template('Cajero-Venta.html')

@app.route('/menosProducto')
@login_required
def menosProducto():
	id = request.args.get('id')
	cant = request.args.get('cantidad')
	val = request.args.get('valor')
	if id:
		sql_disminuir_venta(id, cant, val)
		venta = sql_num_venta()
		datos = sql_llenar_venta(venta[0])
		if palabra:
			busqueda = sql_busca_productos(palabra)
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
		else:
			busqueda = sql_productos()
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
	else:
		return render_template('Cajero-Venta.html')

@app.route('/eliminaProducto')
@login_required
def eliminaProducto():
	id = request.args.get('id')
	if id:
		sql_eliminar_producto(id)
		venta = sql_num_venta()
		datos = sql_llenar_venta(venta[0])
		if palabra:
			busqueda = sql_busca_productos(palabra)
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
		else:
			busqueda = sql_productos()
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, venta=venta)
	else:
		return render_template('Cajero-Venta.html')

#aumenta en 1 la cantidad del producto
#funciona
def sql_aumentar_venta(id_producto, cant, val):
	conexion = db.conectarDB()
	cur = conexion.cursor()
	cur.execute("UPDATE REGISTRO_VENTAS SET Cantidad=?, Total_Prod=? WHERE id_producto=?", (cant, val, id_producto))
	conexion.commit()
	conexion.close()

#disminuye en 1 la cantidad del producto
#funciona
def sql_disminuir_venta(id_producto, cant, val):
	conexion = db.conectarDB()
	cur = conexion.cursor()
	cur.execute("UPDATE REGISTRO_VENTAS SET Cantidad=?, Total_Prod=? WHERE id_producto=?", (cant, val, id_producto))
	conexion.commit()
	conexion.close()

#elimina la linea del producto
#funciona
def sql_eliminar_producto(id_producto):
	conexion = db.conectarDB()
	cur = conexion.cursor()
	cur.execute("DELETE FROM REGISTRO_VENTAS WHERE id_producto=?", (id_producto, ))
	conexion.commit()
	conexion.close()

#funciona
#busca productos
@app.route('/busca', methods=['GET'])
@login_required
def busca():
	if request.method =='GET':
		palabra = request.args.get('buscador')
		busqueda = sql_busca_productos(palabra)
		venta = sql_num_venta()
		datos = sql_llenar_venta(venta[0])
		
		return render_template('Cajero-Venta.html', busqueda=busqueda, datos=datos, venta=venta)
	else:
		return render_template('Cajero-Venta.html')

#funciona
#busca productos
def sql_busca_productos(palabra):
	conexion = db.conectarDB()
	cur = conexion.cursor()
	cur.execute("SELECT * FROM PRODUCTOS WHERE PRODUCTOS.nombre LIKE ? OR PRODUCTOS.nombre LIKE '%"+palabra+"%'", (palabra, ))
	busqueda = cur.fetchall()
	return busqueda

#para crear otra venta
#funciona
@app.route('/nuevaVenta', methods=['GET'])
@login_required
def nuevaVenta():
	if request.method =='GET':
		sql_nueva_venta()
		venta = sql_num_venta()
		busqueda = sql_productos()
		return render_template('Cajero-Venta.html', busqueda=busqueda, venta=venta)
	else:
		busqueda = sql_productos()
		return render_template('Cajero-Venta.html', busqueda=busqueda)

#para crear otra tabla venta
#funciona
def sql_nueva_venta():
	conexion = db.conectarDB()
	cur = conexion.cursor()
	tot = '0'
	cur.execute("INSERT INTO VENTAS (id_usuario, fechaVenta, TotalVenta) VALUES (?, ?, ?)", (session.get('user_id'), time.strftime("%d/%m/%y"), tot))
	conexion.commit()
	conexion.close()

#trae el número y fecha de la venta
#funciona
def sql_num_venta():
	conexion = db.conectarDB()
	cur = conexion.cursor()
	sql = "SELECT id, fechaVenta FROM VENTAS ORDER BY VENTAS.id DESC LIMIT 1"
	cur.execute(sql)
	id_venta = cur.fetchone()
	return id_venta

#calcula y muestra el total de la venta
#funciona
@app.route('/calculaTotal', methods=['GET'])
@login_required
def calculaTotal():
	if request.method=='GET':
		venta = sql_num_venta()
		datos = sql_llenar_venta(venta[0])
		
		total = sql_total_venta(venta[0])
		mensaje = 4
		if palabra:
			busqueda = sql_busca_productos(palabra)
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, total=total, mensaje=mensaje, venta=venta)
		else:
			busqueda = sql_productos()
			return render_template('Cajero-Venta.html', datos=datos, busqueda=busqueda, total=total, mensaje=mensaje, venta=venta)
	else:
		return render_template('Cajero-Venta.html')

#devuelve el total de la venta
#funciona
def sql_total_venta(id_venta):
	conexion = db.conectarDB()
	cur = conexion.cursor()
	cur.execute("SELECT SUM(Total_Prod) FROM REGISTRO_VENTAS WHERE id_venta=?", (id_venta, ))
	total = cur.fetchone()
	sql = "SELECT id FROM VENTAS ORDER BY VENTAS.id DESC LIMIT 1"
	cur.execute(sql)
	id_venta = cur.fetchone()
	cur.execute("UPDATE VENTAS SET TotalVenta=? WHERE id=?", (total[0], id_venta[0]))
	conexion.commit()
	conexion.close()
	return total