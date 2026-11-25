import re
import sys

SECRETOS = re.compile(r"KEY|TOKEN|SECRET|PASSWORD", re.IGNORECASE)
IGNORAR_MINIMO = (".env", ".git", ".venv")


def leer(ruta):
    try:
        with open(ruta, encoding="utf-8") as archivo:
            return archivo.read()
    except FileNotFoundError:
        return None


def instrucciones(texto):
    """Devuelve [(INSTRUCCION, argumentos)] sin comentarios."""
    unido = texto.replace("\\\n", " ")
    resultado = []
    for linea in unido.splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            nombre, _, resto = linea.partition(" ")
            resultado.append((nombre.upper(), resto.strip()))
    return resultado


def base_fija(ins):
    desde = [r for n, r in ins if n == "FROM"]
    if not desde:
        return False, "no hay instruccion FROM"
    imagen = desde[0].split()[0]
    etiqueta = imagen.partition(":")[2]
    if not etiqueta or etiqueta == "latest":
        return False, f"{imagen} no fija una version"
    return True, f"imagen base {imagen}"


def dependencias_antes(ins):
    pos = {"req": None, "pip": None, "codigo": None}
    for i, (nombre, resto) in enumerate(ins):
        if nombre == "COPY" and "requirements" in resto:
            clave = "req"
        elif nombre == "RUN" and "pip install" in resto:
            clave = "pip"
        elif nombre == "COPY":
            clave = "codigo"
        else:
            continue
        if pos[clave] is None:
            pos[clave] = i
    if pos["pip"] is None:
        return False, "no hay RUN pip install"
    if pos["codigo"] is not None and pos["codigo"] < pos["pip"]:
        return False, "se copia el codigo antes de instalar librerias"
    if pos["req"] is None or pos["req"] > pos["pip"]:
        return False, "requirements.txt no se copia antes de pip"
    return True, "requirements, pip install y despues el codigo"


def escucha_afuera(ins):
    for nombre, resto in ins:
        if nombre in ("CMD", "ENTRYPOINT") and "0.0.0.0" in resto:
            return True, "el comando escucha en 0.0.0.0"
    return False, "ningun CMD escucha en 0.0.0.0"


def usuario_comun(ins):
    usuarios = [r.split()[0] for n, r in ins if n == "USER"]
    if not usuarios:
        return False, "no hay USER: corre como root"
    if usuarios[-1] in ("root", "0"):
        return False, "el ultimo USER es root"
    return True, f"corre como {usuarios[-1]}"


def sin_secretos(ins):
    nombres = []
    for nombre, resto in ins:
        if nombre in ("ENV", "ARG"):
            clave = re.split(r"[= ]", resto, maxsplit=1)[0]
            if SECRETOS.search(clave):
                nombres.append(clave)
    if nombres:
        return False, f"nombres sospechosos: {nombres}"
    return True, "ningun ENV ni ARG con nombre de secreto"


def ignora_lo_sensible(_):
    texto = leer(".dockerignore")
    if texto is None:
        return False, "no existe .dockerignore"
    lineas = {ln.strip() for ln in texto.splitlines()}
    faltan = [e for e in IGNORAR_MINIMO if e not in lineas]
    if faltan:
        return False, f"el .dockerignore no excluye {faltan}"
    return True, "excluye .env, .git y .venv"


def con_salud(ins):
    ok = any(n == "HEALTHCHECK" for n, _ in ins)
    return ok, "HEALTHCHECK declarado" if ok else "falta HEALTHCHECK"


COMPROBACIONES = [
    ("DF-1", "imagen base con version fija", base_fija),
    ("DF-2", "dependencias antes del codigo", dependencias_antes),
    ("DF-3", "el servicio escucha hacia afuera", escucha_afuera),
    ("DF-4", "usuario sin privilegios", usuario_comun),
    ("DF-5", "sin secretos en la imagen", sin_secretos),
    ("DF-6", ".dockerignore con lo sensible", ignora_lo_sensible),
    ("DF-7", "comprobacion de salud", con_salud),
]


def ejecutar(ruta):
    texto = leer(ruta)
    if texto is None:
        print(f"No se encontro {ruta}.")
        return False
    ins = instrucciones(texto)
    cumplidas = 0
    for id_, descripcion, prueba in COMPROBACIONES:
        ok, evidencia = prueba(ins)
        estado = "PASA " if ok else "FALLA"
        print(f"{estado} {id_} {descripcion} -> {evidencia}")
        cumplidas += 1 if ok else 0
    print(f"\n{cumplidas} de {len(COMPROBACIONES)} reglas cumplidas")
    return cumplidas == len(COMPROBACIONES)


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "Dockerfile"
    sys.exit(0 if ejecutar(ruta) else 1)
