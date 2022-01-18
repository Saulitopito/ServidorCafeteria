function alertaNoInicio(){
	alertify.error("Credenciales incorrectas");
}

function alertaRecuperarClave(){
	alertify.success("Correo remitido solicitando al administrador el cambio de las credenciales de acceso");
}

function alertaNoRecuperarClave(){
	alertify.error("El usuario no existe");
}

function alertaNoAcceso(){
	alertify.error("Acceso denegado \nInicie sesión")
}

function alertaNoUsuario(){
	alertify.error("El usuario ya existe");
}

function alertaSiUsuario(){
	alertify.success("Usuario creado con éxito");
}

function alertaNoProducto(){
	alertify.error("El producto ya existe");
}

function alertaSiProducto(){
	alertify.success("Producto creado con éxito");
}

