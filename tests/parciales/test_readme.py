import verificar_readme as v

BASE = """# Proyecto

## Requisitos
x
## Instalación
x
## Configuración
x
## Cómo arrancar
x
## Cómo comprobar
x
## Pruebas
x
## Decisiones técnicas
x
## Limitaciones
x
## Estructura del repositorio
x
## Problemas frecuentes
x
"""


def test_secciones_completas_pasan():
    ok, _ = v.secciones_presentes(BASE)
    assert ok


def test_secciones_dice_cuales_faltan():
    texto = BASE.replace("## Decisiones técnicas\nx\n", "")
    ok, evidencia = v.secciones_presentes(texto)
    assert not ok
    assert "Decisiones" in evidencia


def test_normal_ignora_tildes_y_mayusculas():
    assert v.normal("Cómo ARRANCAR") == "como arrancar"


def test_ruta_inexistente_se_nombra():
    ok, evidencia = v.rutas_validas("Mira `docs/no_existe.md`.")
    assert not ok
    assert "docs/no_existe.md" in evidencia


def test_sin_rutas_no_pasa_en_vacio():
    ok, _ = v.rutas_validas("Sin nada que citar.")
    assert not ok


def test_comando_a_archivo_inexistente_falla():
    ok, evidencia = v.comandos_validos("```\npython no_existe.py\n```")
    assert not ok
    assert "no_existe.py" in evidencia


def test_secreto_en_el_readme_se_detecta():
    ok, _ = v.sin_secretos("GEMINI_API_KEY=abcdefgh1234")
    assert not ok
