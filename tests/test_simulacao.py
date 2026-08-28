"""
Validacao do modulo minhastats.simulacao (Modulo 3).

Simulacao nao tem "valor de referencia" exato como uma media -- o que se
valida aqui e outra coisa:

1. REPRODUTIBILIDADE  : a mesma semente produz exatamente o mesmo resultado;
2. CONVERGENCIA (LGN) : o erro cai quando n cresce, e a estimativa fica
                        dentro do intervalo previsto pela teoria;
3. TCL                : a media das medias reproduz mu, o desvio das medias
                        reproduz sigma/sqrt(n), e a distribuicao das medias
                        fica mais Normal (assimetria -> 0) conforme n cresce.

Os limites usados nas assercoes vem da propria teoria (erro padrao,
desigualdade de Chebyshev), nao de valores "chutados".
"""

import math

import numpy as np
import pytest
from scipy import stats as scipy_stats

from minhastats import simulacao as sim
from minhastats import descritiva as d
from conftest import TOL, quase_igual


# ===========================================================================
# REPRODUTIBILIDADE
# ===========================================================================


def test_moeda_e_reprodutivel_com_semente():
    a = sim.simular_moeda(5000, 0.5, semente=123)
    b = sim.simular_moeda(5000, 0.5, semente=123)
    assert a["frequencias_acumuladas"] == b["frequencias_acumuladas"]


def test_sementes_diferentes_produzem_resultados_diferentes():
    a = sim.simular_moeda(5000, 0.5, semente=1)
    b = sim.simular_moeda(5000, 0.5, semente=2)
    assert a["frequencia_final"] != b["frequencia_final"]


def test_tcl_e_reprodutivel_com_semente(coluna_numerica):
    x = coluna_numerica("cnt")
    a = sim.simular_tcl(x, 30, 500, semente=99)
    b = sim.simular_tcl(x, 30, 500, semente=99)
    assert a["medias_amostrais"] == b["medias_amostrais"]


# ===========================================================================
# LEI DOS GRANDES NUMEROS -- MOEDA
# ===========================================================================


@pytest.mark.parametrize("p", [0.5, 0.3, 0.75])
def test_moeda_converge_para_p(p):
    r = sim.simular_moeda(100000, p, semente=7)
    # Desvio padrao da proporcao amostral: sqrt(p(1-p)/n). Com n = 100.000
    # e 4 desvios, a probabilidade de estourar e < 0,01%.
    erro_maximo = 4 * math.sqrt(p * (1 - p) / 100000)
    assert abs(r["frequencia_final"] - p) < erro_maximo


def test_moeda_erro_diminui_com_n():
    """A essencia da LGN: mais repeticoes, menos erro. Comparamos a MEDIA do
    erro em varias sementes para nao depender de um sorteio sortudo."""
    def erro_medio(n):
        erros = [
            abs(sim.simular_moeda(n, 0.5, semente=s)["frequencia_final"] - 0.5)
            for s in range(20)
        ]
        return sum(erros) / len(erros)

    assert erro_medio(10) > erro_medio(1000) > erro_medio(100000)


def test_moeda_contagem_coerente():
    r = sim.simular_moeda(1000, 0.5, semente=5)
    assert r["sucessos"] == pytest.approx(r["frequencia_final"] * 1000, abs=1e-9)
    assert 0 <= r["sucessos"] <= 1000
    assert len(r["frequencias_acumuladas"]) == 1000


def test_moeda_p_zero_e_um():
    """Casos extremos deterministicos."""
    assert sim.simular_moeda(100, 0.0, semente=1)["frequencia_final"] == 0.0
    assert sim.simular_moeda(100, 1.0, semente=1)["frequencia_final"] == 1.0


def test_moeda_parametros_invalidos():
    with pytest.raises(ValueError):
        sim.simular_moeda(0, 0.5)
    with pytest.raises(ValueError):
        sim.simular_moeda(10, 1.5)


# ===========================================================================
# LEI DOS GRANDES NUMEROS -- DADO
# ===========================================================================


@pytest.mark.parametrize("faces", [6, 20])
def test_dado_converge_para_esperanca(faces):
    r = sim.simular_dado(200000, faces=faces, semente=11)
    esperado = (faces + 1) / 2.0
    assert r["esperanca_teorica"] == esperado

    # Desvio padrao de um dado honesto: sqrt((f^2 - 1)/12)
    sigma = math.sqrt((faces ** 2 - 1) / 12.0)
    erro_maximo = 4 * sigma / math.sqrt(200000)
    assert abs(r["media_final"] - esperado) < erro_maximo


def test_dado_frequencias_convergem_para_um_sexto():
    r = sim.simular_dado(200000, faces=6, semente=13)
    for i, fr in enumerate(r["frequencias_relativas"]):
        assert fr == pytest.approx(1.0 / 6.0, abs=0.01), f"face {i+1} desviou demais"
    assert sum(r["contagem_faces"]) == 200000


def test_dado_media_final_bate_com_numpy():
    """A media acumulada final tem de ser exatamente a media dos resultados."""
    r = sim.simular_dado(5000, semente=3)
    quase_igual(r["media_final"], float(np.mean(r["resultados"])),
                contexto="media acumulada final vs numpy.mean")


def test_dado_parametros_invalidos():
    with pytest.raises(ValueError):
        sim.simular_dado(100, faces=1)


def test_tabela_de_convergencia():
    r = sim.simular_moeda(10000, 0.5, semente=17)
    linhas = sim.convergencia_lgn(r["frequencias_acumuladas"], 0.5)
    assert [l["n"] for l in linhas] == [10, 100, 1000, 10000]
    for l in linhas:
        assert l["erro_absoluto"] == pytest.approx(abs(l["estimativa"] - 0.5))
    # marcos maiores que a simulacao sao simplesmente ignorados
    assert sim.convergencia_lgn([0.5] * 5, 0.5, marcos=(10, 100)) == []


# ===========================================================================
# ESTIMATIVA DE PI
# ===========================================================================


def test_monte_carlo_estima_pi():
    r = sim.estimar_pi_monte_carlo(200000, semente=21)
    assert r["pi_estimado"] == pytest.approx(math.pi, abs=0.02)
    assert r["pi_teorico"] == math.pi


def test_monte_carlo_pi_guarda_pontos_para_o_grafico():
    r = sim.estimar_pi_monte_carlo(10000, semente=1)
    # so os 3000 primeiros pontos sao guardados, para nao pesar o grafico
    assert len(r["pontos_x"]) == 3000
    assert len(r["pontos_y"]) == 3000
    assert len(r["dentro"]) == 3000
    assert all(0.0 <= v <= 1.0 for v in r["pontos_x"])


# ===========================================================================
# TEOREMA CENTRAL DO LIMITE
# ===========================================================================


def test_tcl_media_das_medias_recupera_mu(coluna_numerica):
    r"""E[X_barra] = mu: a media das medias amostrais e um estimador nao
    viesado da media populacional."""
    x = coluna_numerica("cnt")
    r = sim.simular_tcl(x, tamanho_amostra=50, n_repeticoes=4000, semente=42)

    # tolerancia: 4 erros padrao da MEDIA DAS MEDIAS
    tolerancia = 4 * r["erro_padrao_teorico"] / math.sqrt(r["n_repeticoes"])
    assert abs(r["media_das_medias"] - r["mu_populacao"]) < tolerancia


@pytest.mark.parametrize("n", [5, 30, 100])
def test_tcl_erro_padrao_observado_bate_com_sigma_sobre_raiz_n(coluna_numerica, n):
    r"""O resultado central do TCL: sd(X_barra) = sigma / sqrt(n).
    Aceitamos 10% de folga porque o desvio observado e ele proprio uma
    estimativa a partir de 4.000 repeticoes."""
    x = coluna_numerica("cnt")
    r = sim.simular_tcl(x, tamanho_amostra=n, n_repeticoes=4000, semente=42)

    quase_igual(r["erro_padrao_teorico"], r["sigma_populacao"] / math.sqrt(n),
                contexto="formula do erro padrao teorico")
    assert r["erro_padrao_observado"] == pytest.approx(
        r["erro_padrao_teorico"], rel=0.10
    ), "o desvio das medias amostrais nao seguiu sigma/sqrt(n)"


def test_tcl_normalidade_melhora_com_n(coluna_numerica):
    """A demonstracao visual do Modulo 3, expressa em numero: partindo de
    'casual' (fortemente assimetrica), a assimetria da distribuicao das
    medias amostrais cai conforme o tamanho da amostra cresce."""
    x = coluna_numerica("casual")
    assimetria_populacao = abs(d.assimetria_momento(x))

    assimetrias = []
    for n in [2, 10, 100]:
        r = sim.simular_tcl(x, tamanho_amostra=n, n_repeticoes=5000, semente=2024)
        assimetrias.append(abs(d.assimetria_momento(r["medias_amostrais"])))

    assert assimetrias[0] > assimetrias[1] > assimetrias[2], (
        f"a assimetria deveria cair monotonicamente: {assimetrias}"
    )
    assert assimetrias[-1] < assimetria_populacao / 3.0


def test_tcl_com_n_grande_passa_no_teste_de_normalidade(coluna_numerica):
    """Confirmacao independente com SciPy: com n = 200, as medias amostrais
    de uma variavel assimetrica ja nao sao distinguiveis de uma Normal pelo
    teste de D'Agostino-Pearson (p > 0.05)."""
    x = coluna_numerica("cnt")
    r = sim.simular_tcl(x, tamanho_amostra=200, n_repeticoes=2000, semente=2024)
    _, p_valor = scipy_stats.normaltest(r["medias_amostrais"])
    assert p_valor > 0.05, f"p-valor = {p_valor:.4f}: as medias nao pareceram Normais"


def test_tcl_amostragem_sem_reposicao(coluna_numerica):
    x = coluna_numerica("temp")
    r = sim.simular_tcl(x, 100, 200, semente=1, com_reposicao=False)
    assert len(r["medias_amostrais"]) == 200


def test_tcl_sem_reposicao_amostra_maior_que_populacao():
    with pytest.raises(ValueError, match="nao pode exceder a populacao"):
        sim.simular_tcl([1.0, 2.0, 3.0], 10, 5, com_reposicao=False)


def test_tcl_parametros_invalidos(coluna_numerica):
    x = coluna_numerica("temp")
    with pytest.raises(ValueError):
        sim.simular_tcl(x, 0, 100)
    with pytest.raises(ValueError):
        sim.simular_tcl(x, 10, 0)
    with pytest.raises(ValueError, match="ao menos 2 valores"):
        sim.simular_tcl([1.0], 1, 10)


def test_tcl_estrutura_do_retorno(coluna_numerica):
    x = coluna_numerica("temp")
    r = sim.simular_tcl(x, 25, 300, semente=8)
    assert len(r["medias_amostrais"]) == 300
    assert r["tamanho_amostra"] == 25
    assert r["n_repeticoes"] == 300
    quase_igual(r["mu_populacao"], float(np.mean(x)), contexto="mu da populacao")
    quase_igual(r["sigma_populacao"], float(np.std(x, ddof=1)),
                contexto="sigma da populacao")
