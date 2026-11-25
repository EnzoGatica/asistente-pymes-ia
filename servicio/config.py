import os


class ConfiguracionIncompleta(Exception):
    """Falta una variable de entorno obligatoria."""


def entorno():
    """Dato de configuracion: no es secreto, tiene valor por omision."""
    return os.environ.get("ENTORNO", "desarrollo")


def modelo_configurado():
    return bool(os.environ.get("OPENAI_API_KEY"))


def clave_modelo():
    """Devuelve la clave solo cuando se necesita, nunca al importar."""
    clave = os.environ.get("OPENAI_API_KEY")
    if not clave:
        raise ConfiguracionIncompleta(
            "Falta la variable de entorno OPENAI_API_KEY."
        )
    return clave
