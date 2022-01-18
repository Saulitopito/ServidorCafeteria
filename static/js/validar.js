function validar() {
    let usuario = document.getElementById("usuario").value;
    let clave = document.getElementById("clave").value;
    
    if (usuario==""){
        //alert("Debe ingresar un usuario válido");
        alertify.error("Debe ingresar un usuario válido");
        document.getElementById("usuario").focus();
        return false;
    }
    if (clave==""){
        //alert("Debe ingresar una contraseña");
        alertify.error("Debe ingresar una contraseña");
        document.getElementById("clave").focus();
        return false;
    }
    if (clave.length<6){
        //alert("La contraseña debe contar con 6 caracteres mínimo");
        alertify.error("La contraseña debe contar con 6 caracteres mínimo");
        document.getElementById("clave").focus();
        return false;
    }

    return true;
}

function acceso() {
    let usuario = document.getElementById("usuario").value;
    let clave = document.getElementById("clave").value;
    if (usuario=='cajero'&&clave=="123456"){
        return "href='/admin'";
    }
    else if (usuario=="admin"&&clave=="admin123"){
        return "href='/cajeroVenta'";
    }
    else {
        alert("Credenciales inválidas");
        return false;
    }
}

function motrarClave() {
    document.getElementById("clave").type="text"
}

function ocultarClave() {
    document.getElementById("clave").type="password"
}