"""
Teste de fumaca da interface.

Usa o ``AppTest`` do proprio Streamlit para EXECUTAR a aplicacao de ponta a
ponta, pagina por pagina, sem abrir navegador. Nao valida numeros (isso e
papel dos testes do nucleo) -- valida que a aplicacao sobe, que cada modulo
renderiza sem excecao e que os widgets exigidos pelo enunciado existem.
"""

import os

import pytest

pytest.importorskip("streamlit", reason="streamlit nao instalado")

from streamlit.testing.v1 import AppTest

TIMEOUT = 180

# AppTest.from_file resolve caminhos relativos a ESTE arquivo, entao subimos
# um nivel ate a raiz do projeto.
CAMINHO_APP = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"
)


def _abrir(pagina=None):
    """Sobe a aplicacao e, opcionalmente, navega ate um modulo."""
    at = AppTest.from_file(CAMINHO_APP, default_timeout=TIMEOUT).run()
    if pagina is not None:
        at.radio(key="navegacao").set_value(pagina).run()
    return at


def test_aplicacao_sobe_sem_erro():
    at = _abrir()
    assert not at.exception, f"exceção ao subir a aplicação: {at.exception}"


def test_navegacao_lista_os_sete_modulos():
    at = _abrir()
    opcoes = at.radio(key="navegacao").options
    assert len(opcoes) == 7
    for numero in ["Módulo 0", "Módulo 1", "Módulo 2", "Módulo 3", "Módulo 4",
                   "Módulo 5", "Módulo 6"]:
        assert any(numero in o for o in opcoes), f"{numero} ausente na navegação"


@pytest.mark.parametrize(
    "pagina",
    [
        "Módulo 0 — Dados Reais",
        "Módulo 1 — Núcleo Estatístico Próprio",
        "Módulo 2 — Estatística Descritiva",
        "Módulo 3 — Probabilidade e Simulação",
        "Módulo 4 — Distribuições Teóricas",
        "Módulo 5 — Correlação e Regressão",
        "Módulo 6 — Descobertas",
    ],
)
def test_cada_modulo_renderiza(pagina):
    at = _abrir(pagina)
    assert not at.exception, f"exceção em '{pagina}': {at.exception}"


def test_modulo_2_troca_para_categorica_e_renderiza():
    at = _abrir("Módulo 2 — Estatística Descritiva")
    at.radio(key="m2_tipo").set_value("Categórica (qualitativa)").run()
    assert not at.exception


def test_modulo_3_parametros_sao_controlaveis():
    """O enunciado exige que o usuario controle nº de repeticoes e tamanho
    da amostra."""
    at = _abrir("Módulo 3 — Probabilidade e Simulação")
    assert at.session_state["m3_n_lgn"] is not None       # repeticoes da LGN
    assert at.session_state["m3_tamanho"] is not None     # tamanho da amostra do TCL
    assert at.session_state["m3_repeticoes"] is not None  # repeticoes do TCL
    assert not at.exception


def test_modulo_3_alterar_tamanho_da_amostra_do_tcl():
    at = _abrir("Módulo 3 — Probabilidade e Simulação")
    at.session_state["m3_tamanho"] = 100
    at.run()
    assert not at.exception


def test_modulo_5_predicao_interativa_responde():
    """Campo de predicao: usuario digita X e a aplicacao devolve Y-chapeu."""
    at = _abrir("Módulo 5 — Correlação e Regressão")
    entrada = at.number_input(key="m5_predicao")
    assert entrada is not None, "campo de predição interativa não encontrado"
    entrada.set_value(25.0).run()
    assert not at.exception


def test_modulo_5_alerta_de_causalidade_esta_presente():
    """Exigencia explicita do enunciado."""
    at = _abrir("Módulo 5 — Correlação e Regressão")
    textos = " ".join(e.value for e in at.error)
    assert "causalidade" in textos.lower(), (
        "o alerta 'correlação não implica causalidade' não foi exibido"
    )


def test_modulo_5_rejeita_x_igual_a_y():
    at = _abrir("Módulo 5 — Correlação e Regressão")
    at.selectbox(key="m5_y").set_value("temp_c").run()
    textos = " ".join(e.value for e in at.error)
    assert "diferentes" in textos.lower()


def test_modulo_4_exige_ao_menos_uma_distribuicao():
    at = _abrir("Módulo 4 — Distribuições Teóricas")
    at.multiselect(key="m4_candidatas").set_value([]).run()
    assert any("ao menos uma" in w.value.lower() for w in at.warning)


def test_modulo_1_mostra_codigo_fonte_e_imports():
    """A pagina do nucleo exibe o codigo real e confirma a regra de ouro."""
    at = _abrir("Módulo 1 — Núcleo Estatístico Próprio")
    assert not at.exception
    textos = " ".join(e.value for e in at.success)
    assert "math" in textos and "random" in textos, (
        "a pagina deveria confirmar que o nucleo importa apenas math e random"
    )
    codigos = " ".join(c.value for c in at.code)
    assert "def variancia_amostral" in codigos, "codigo-fonte da funcao nao exibido"
