from unittest.mock import Mock, patch

import pytest
import requests

import cliente
from cliente import con_reintento, consultar_modelo, enviar_peticion, registrar_costo

URL = "https://api.openai.com/v1/chat/completions"
BODY = {"model": "gpt-4.1-nano", "messages": [{"role": "user", "content": "test"}]}


@pytest.fixture(autouse=True)
def entorno_controlado(monkeypatch):
    cliente.costo_total_sesion = 0
    monkeypatch.setenv("OPENAI_API_KEY", "sk-prueba")
    yield


def respuesta_exitosa(texto="respuesta simulada", entrada=1000, salida=500):
    falsa = Mock(status_code=200)
    falsa.json.return_value = {
        "choices": [{"message": {"content": texto}}],
        "usage": {"prompt_tokens": entrada, "completion_tokens": salida},
    }
    return falsa


# enviar_peticion

def test_enviar_peticion_exito():
    with patch("cliente.requests.post", return_value=respuesta_exitosa()):
        resultado = enviar_peticion(URL, BODY)
    assert resultado["choices"][0]["message"]["content"] == "respuesta simulada"


def test_enviar_peticion_credencial_invalida():
    with patch("cliente.requests.post", return_value=Mock(status_code=401)):
        with pytest.raises(ValueError):
            enviar_peticion(URL, BODY)


def test_enviar_peticion_sin_permiso():
    with patch("cliente.requests.post", return_value=Mock(status_code=403)):
        with pytest.raises(ValueError):
            enviar_peticion(URL, BODY)


def test_enviar_peticion_limite_de_uso():
    with patch("cliente.requests.post", return_value=Mock(status_code=429)):
        with pytest.raises(TimeoutError):
            enviar_peticion(URL, BODY)


def test_enviar_peticion_error_del_servidor_se_trata_como_temporal():
    with patch("cliente.requests.post", return_value=Mock(status_code=503)):
        with pytest.raises(TimeoutError):
            enviar_peticion(URL, BODY)


def test_enviar_peticion_sin_conexion():
    with patch("cliente.requests.post", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(TimeoutError):
            enviar_peticion(URL, BODY)


def test_enviar_peticion_sin_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    with patch("cliente.requests.post") as post:
        with pytest.raises(ValueError):
            enviar_peticion(URL, BODY)
    post.assert_not_called()


# con_reintento

def test_con_reintento_exito_al_primer_intento():
    assert con_reintento(lambda: "ok") == "ok"


def test_con_reintento_agota_intentos():
    funcion = Mock(side_effect=TimeoutError("simulado"))
    with patch("cliente.time.sleep") as sleep:
        with pytest.raises(TimeoutError):
            con_reintento(funcion, intentos=3)
    assert funcion.call_count == 3
    assert [llamada.args[0] for llamada in sleep.call_args_list] == [1, 2]  # backoff exponencial


def test_con_reintento_recupera_despues_de_fallar():
    funcion = Mock(side_effect=[TimeoutError("simulado"), "ok"])
    with patch("cliente.time.sleep"):
        assert con_reintento(funcion) == "ok"
    assert funcion.call_count == 2


def test_con_reintento_no_reintenta_value_error():
    funcion = Mock(side_effect=ValueError("credencial"))
    with patch("cliente.time.sleep") as sleep:
        with pytest.raises(ValueError):
            con_reintento(funcion)
    assert funcion.call_count == 1
    sleep.assert_not_called()


# registrar_costo

def test_registrar_costo_calcula_con_precios_del_modelo():
    respuesta = {"usage": {"prompt_tokens": 1_000_000, "completion_tokens": 1_000_000}}
    assert registrar_costo(respuesta, "gpt-4.1-nano") == pytest.approx(0.10 + 0.40)


def test_registrar_costo_acumula():
    respuesta = {"usage": {"prompt_tokens": 1000, "completion_tokens": 500}}
    costo = registrar_costo(respuesta)
    registrar_costo(respuesta)
    assert cliente.costo_total_sesion == pytest.approx(2 * costo)


def test_registrar_costo_sin_usage_es_cero():
    assert registrar_costo({}) == 0


# consultar_modelo

def test_consultar_modelo_devuelve_texto_y_registra_costo():
    with patch("cliente.requests.post", return_value=respuesta_exitosa("Santiago")):
        assert consultar_modelo("¿Capital de Chile?") == "Santiago"
    assert cliente.costo_total_sesion > 0


def test_consultar_modelo_convierte_error():
    with patch("cliente.con_reintento", side_effect=TimeoutError("simulado")):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba")


def test_consultar_modelo_propaga_credencial_invalida_sin_reintentar():
    with patch("cliente.requests.post", return_value=Mock(status_code=401)) as post:
        with pytest.raises(ValueError):
            consultar_modelo("pregunta de prueba")
    assert post.call_count == 1


def test_consultar_modelo_valida_pregunta_vacia():
    with pytest.raises(ValueError):
        consultar_modelo("   ")
