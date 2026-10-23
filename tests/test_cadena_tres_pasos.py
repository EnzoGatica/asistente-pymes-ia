from unittest.mock import MagicMock

from langchain_core.messages import AIMessage

from cadena_tres_pasos import construir_cadena


def test_cadena_conecta_los_tres_pasos():
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content=" Pedido \n"),
        AIMessage(content="borrador con $38.000"),
        AIMessage(content="¡Hola! La torta para 30 personas cuesta $38.000."),
    ]
    resultado = construir_cadena(modelo_falso).invoke({"mensaje": "torta para 30"})
    assert modelo_falso.call_count == 3
    assert resultado == "¡Hola! La torta para 30 personas cuesta $38.000."


def test_paso_redactar_recibe_categoria_normalizada_y_mensaje():
    modelo_falso = MagicMock(side_effect=[AIMessage(content=" RECLAMO "), AIMessage(content="b"), AIMessage(content="c")])
    construir_cadena(modelo_falso).invoke({"mensaje": "el pan venía crudo"})
    prompt_paso_2 = modelo_falso.call_args_list[1].args[0].to_string()
    assert "'reclamo'" in prompt_paso_2
    assert "el pan venía crudo" in prompt_paso_2


def test_paso_revisar_recibe_el_borrador_del_paso_2():
    modelo_falso = MagicMock(side_effect=[AIMessage(content="precio"), AIMessage(content="BORRADOR-X"), AIMessage(content="ok")])
    construir_cadena(modelo_falso).invoke({"mensaje": "¿cuánto vale?"})
    assert "BORRADOR-X" in modelo_falso.call_args_list[2].args[0].to_string()
