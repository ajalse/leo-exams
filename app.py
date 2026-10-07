import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta



app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones"
app.permanent_session_lifetime = timedelta(minutes=10)

PASSWORD = "071215"


# Estados posibles
ESTADOS = ["habilitado", "realizado", "deshabilitado"]

# Diccionario donde guardaremos los estados de cada examen
# Inicialmente todos habilitados
examenes_estado = {}

def cargar_examenes():
    """Lee los nombres de los exámenes desde las carpetas templates/toefl y templates/sat"""
    examenes = {"toefl": [], "sat": []}

    base_path = os.path.join(app.root_path, "templates")

    for tipo in examenes.keys():
        carpeta = os.path.join(base_path, tipo)
        if os.path.exists(carpeta):
            for fichero in sorted(os.listdir(carpeta)):
                if fichero.endswith(".html"):
                    nombre = fichero.replace(".html", "")
                    examenes[tipo].append(nombre)
                    # Si no existe estado previo, lo inicializamos
                    if nombre not in examenes_estado:
                        examenes_estado[nombre] = "deshabilitado"

    return examenes


@app.route("/")
def index():
    examenes = cargar_examenes()
    return render_template("index.html", examenes=examenes, estados=examenes_estado)


@app.route("/examen/<tipo>/<nombre>")
def examen(tipo, nombre):
    # Solo permitir acceso si está habilitado
    if examenes_estado.get(nombre) != "habilitado":
        return "Este examen no está habilitado.", 403

    plantilla = f"{tipo}/{nombre}.html"
    return render_template(plantilla)


@app.route("/configure", methods=["GET", "POST"])
def configure():
    if "autorizado" not in session:
        return redirect(url_for("configure_login"))

    examenes = cargar_examenes()

    if request.method == "POST":
        for nombre in examenes_estado.keys():
            nuevo_estado = request.form.get(nombre)
            if nuevo_estado in ESTADOS:
                examenes_estado[nombre] = nuevo_estado

        return redirect(url_for("index"))

    return render_template("configure.html", examenes=examenes, estados=examenes_estado)


@app.route("/configure/login", methods=["GET", "POST"])
def configure_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == PASSWORD:
            session["autorizado"] = True
            return redirect(url_for("configure"))
        else:
            return render_template("configure_login.html", error="Contraseña incorrecta")

    return render_template("configure_login.html")


@app.route("/logout")
def logout():
    session.pop("autorizado", None)
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)

