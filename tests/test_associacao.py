"""
Validacao do modulo minhastats.associacao contra NumPy / SciPy.

Referencias usadas:
    covariancia amostral    -> numpy.cov(ddof=1)
    covariancia populacional-> numpy.cov(ddof=0)
    correlacao de Pearson   -> scipy.stats.pearsonr / numpy.corrcoef
    minimos quadrados       -> numpy.polyfit(deg=1) / scipy.stats.linregress
    R^2                     -> scipy.stats.linregress(...).rvalue ** 2
"""

import math

import numpy as np
import pytest
from scipy import stats as scipy_stats

from minhastats import associacao as a
from conftest import TOL, quase_igual

PARES_DATASET = [
    ("temp", "cnt"),
    ("atemp", "registered"),
    ("hum", "cnt"),
    ("windspeed", "casual"),
    ("temp", "atemp"),
    ("registered", "casual"),
]


@pytest.fixture(scope="module")
def pares_sinteticos():
    """Pares (x, y) com relacoes conhecidas, semente fixa."""
    import random

    rng = random.Random(7)
    n = 500
    x = [rng.uniform(0, 100) for _ in range(n)]
    return {
        # relacao linear perfeita: r deve ser exatamente 1
        "perfeita_positiva": (x, [3.0 * v + 5.0 for v in x]),
        # relacao linear perfeita invertida: r = -1
        "perfeita_negativa": (x, [-2.0 * v + 100.0 for v in x]),
        # linear com ruido: r alto mas < 1
        "com_ruido": (x, [3.0 * v + 5.0 + rng.gauss(0, 20) for v in x]),
        # sem relacao: r proximo de zero
        "independente": (x, [rng.uniform(0, 100) for _ in range(n)]),
        # relacao quadratica: r linear baixo mesmo havendo dependencia forte
        "quadratica": (x, [(v - 50.0) ** 2 for v in x]),
    }


# ===========================================================================
# COVARIANCIA
# ===========================================================================


def test_covariancia_caso_manual():
    """x = [1,2,3,4], y = [2,4,6,8]. Desvios de x: -1.5,-0.5,0.5,1.5;
    de y: -3,-1,1,3. Soma dos produtos = 4.5+0.5+0.5+4.5 = 10.
    Cov amostral = 10/3; populacional = 10/4 = 2.5."""
    x = [1.0, 2.0, 3.0, 4.0]
    y = [2.0, 4.0, 6.0, 8.0]
    assert a.covariancia_amostral(x, y) == pytest.approx(10.0 / 3.0, rel=TOL)
    assert a.covariancia_populacional(x, y) == pytest.approx(2.5, rel=TOL)


@pytest.mark.parametrize("cenario", ["perfeita_positiva", "perfeita_negativa",
                                     "com_ruido", "independente", "quadratica"])
def test_covariancia_vs_numpy_sintetico(pares_sinteticos, cenario):
    x, y = pares_sinteticos[cenario]
    # numpy.cov devolve a matriz de covariancias; o termo cruzado e [0][1]
    quase_igual(a.covariancia_amostral(x, y), float(np.cov(x, y, ddof=1)[0][1]),
                contexto=f"cov amostral [{cenario}]")
    quase_igual(a.covariancia_populacional(x, y), float(np.cov(x, y, ddof=0)[0][1]),
                contexto=f"cov populacional [{cenario}]")


@pytest.mark.parametrize("cx,cy", PARES_DATASET)
def test_covariancia_vs_numpy_dataset(coluna_numerica, cx, cy):
    x, y = coluna_numerica(cx), coluna_numerica(cy)
    quase_igual(a.covariancia_amostral(x, y), float(np.cov(x, y, ddof=1)[0][1]),
                contexto=f"cov amostral [{cx} x {cy}]")


def test_covariancia_e_simetrica(coluna_numerica):
    """Cov(X,Y) = Cov(Y,X) -- propriedade que a implementacao deve preservar."""
    x, y = coluna_numerica("temp"), coluna_numerica("cnt")
    quase_igual(a.covariancia_amostral(x, y), a.covariancia_amostral(y, x),
                contexto="simetria da covariancia")


def test_covariancia_de_x_com_x_e_a_variancia(coluna_numerica):
    """Cov(X,X) = Var(X) -- consistencia entre os dois modulos do nucleo."""
    from minhastats import descritiva as d

    x = coluna_numerica("hum")
    quase_igual(a.covariancia_amostral(x, x), d.variancia_amostral(x),
                contexto="Cov(X,X) = Var(X)")


# ===========================================================================
# CORRELACAO DE PEARSON
# ===========================================================================


def test_correlacao_perfeita_positiva(pares_sinteticos):
    x, y = pares_sinteticos["perfeita_positiva"]
    assert a.correlacao_pearson(x, y) == pytest.approx(1.0, rel=1e-12)


def test_correlacao_perfeita_negativa(pares_sinteticos):
    x, y = pares_sinteticos["perfeita_negativa"]
    assert a.correlacao_pearson(x, y) == pytest.approx(-1.0, rel=1e-12)


@pytest.mark.parametrize("cenario", ["perfeita_positiva", "perfeita_negativa",
                                     "com_ruido", "independente", "quadratica"])
def test_correlacao_vs_scipy_sintetico(pares_sinteticos, cenario):
    x, y = pares_sinteticos[cenario]
    esperado = float(scipy_stats.pearsonr(x, y)[0])
    quase_igual(a.correlacao_pearson(x, y), esperado, contexto=f"Pearson [{cenario}]")


@pytest.mark.parametrize("cx,cy", PARES_DATASET)
def test_correlacao_vs_scipy_dataset(coluna_numerica, cx, cy):
    x, y = coluna_numerica(cx), coluna_numerica(cy)
    esperado = float(scipy_stats.pearsonr(x, y)[0])
    quase_igual(a.correlacao_pearson(x, y), esperado, contexto=f"Pearson [{cx} x {cy}]")
    quase_igual(a.correlacao_pearson(x, y), float(np.corrcoef(x, y)[0][1]),
                contexto=f"Pearson vs corrcoef [{cx} x {cy}]")


def test_correlacao_sempre_no_intervalo_valido(coluna_numerica):
    """r tem de estar em [-1, 1] mesmo com erro de arredondamento."""
    for cx, cy in PARES_DATASET:
        r = a.correlacao_pearson(coluna_numerica(cx), coluna_numerica(cy))
        assert -1.0 <= r <= 1.0, f"r fora do intervalo em {cx} x {cy}: {r}"


def test_correlacao_invariante_a_transformacao_linear(coluna_numerica):
    """r nao muda se aplicarmos y' = a + b*y com b > 0 -- a correlacao mede
    forma, nao escala."""
    x = coluna_numerica("temp")
    y = coluna_numerica("cnt")
    y_transformado = [1000.0 + 7.0 * v for v in y]
    quase_igual(a.correlacao_pearson(x, y),
                a.correlacao_pearson(x, y_transformado),
                contexto="invariancia da correlacao a transformacao linear")


def test_correlacao_com_variavel_constante_levanta_erro():
    with pytest.raises(ValueError, match="constante"):
        a.correlacao_pearson([1.0, 2.0, 3.0], [5.0, 5.0, 5.0])


def test_tamanhos_diferentes_levantam_erro():
    with pytest.raises(ValueError, match="mesmo tamanho"):
        a.correlacao_pearson([1.0, 2.0, 3.0], [1.0, 2.0])


def test_pares_com_nan_sao_descartados_juntos():
    """Se y[1] e NaN, o par (2, NaN) inteiro sai -- sobra [(1,10),(3,30)]."""
    x = [1.0, 2.0, 3.0]
    y = [10.0, float("nan"), 30.0]
    assert a.correlacao_pearson(x, y) == pytest.approx(1.0, rel=1e-12)


def test_interpretar_correlacao_texto():
    assert "muito forte" in a.interpretar_correlacao(0.95)
    assert "positiva" in a.interpretar_correlacao(0.95)
    assert "negativa" in a.interpretar_correlacao(-0.8)
    assert "fraca" in a.interpretar_correlacao(0.2)


# ===========================================================================
# REGRESSAO LINEAR (MINIMOS QUADRADOS)
# ===========================================================================


def test_regressao_caso_manual():
    """Pontos exatamente sobre y = 2x + 1 -> b = 2, a = 1, R2 = 1."""
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [3.0, 5.0, 7.0, 9.0, 11.0]
    m = a.regressao_linear(x, y)
    assert m["b"] == pytest.approx(2.0, rel=1e-12)
    assert m["a"] == pytest.approx(1.0, abs=1e-12)
    assert m["r2"] == pytest.approx(1.0, rel=1e-12)
    assert m["sq_residuos"] == pytest.approx(0.0, abs=1e-18)


@pytest.mark.parametrize("cenario", ["perfeita_positiva", "com_ruido",
                                     "independente", "quadratica"])
def test_regressao_vs_numpy_polyfit(pares_sinteticos, cenario):
    x, y = pares_sinteticos[cenario]
    m = a.regressao_linear(x, y)
    b_np, a_np = np.polyfit(x, y, 1)  # polyfit devolve [inclinacao, intercepto]
    quase_igual(m["b"], float(b_np), contexto=f"coef. angular [{cenario}]")
    quase_igual(m["a"], float(a_np), contexto=f"intercepto [{cenario}]")


@pytest.mark.parametrize("cenario", ["perfeita_positiva", "com_ruido",
                                     "independente", "quadratica"])
def test_regressao_vs_scipy_linregress(pares_sinteticos, cenario):
    x, y = pares_sinteticos[cenario]
    m = a.regressao_linear(x, y)
    ref = scipy_stats.linregress(x, y)
    quase_igual(m["b"], float(ref.slope), contexto=f"slope [{cenario}]")
    quase_igual(m["a"], float(ref.intercept), contexto=f"intercept [{cenario}]")
    quase_igual(m["r2"], float(ref.rvalue) ** 2, contexto=f"R2 [{cenario}]")
    quase_igual(m["erro_padrao_estimativa"],
                float(np.sqrt(np.sum((np.array(y) - (ref.intercept + ref.slope * np.array(x))) ** 2) / (len(x) - 2))),
                contexto=f"erro padrao da estimativa [{cenario}]")


@pytest.mark.parametrize("cx,cy", PARES_DATASET)
def test_regressao_vs_scipy_dataset(coluna_numerica, cx, cy):
    x, y = coluna_numerica(cx), coluna_numerica(cy)
    m = a.regressao_linear(x, y)
    ref = scipy_stats.linregress(x, y)
    quase_igual(m["b"], float(ref.slope), contexto=f"slope [{cx} x {cy}]")
    quase_igual(m["a"], float(ref.intercept), contexto=f"intercept [{cx} x {cy}]")
    quase_igual(m["r2"], float(ref.rvalue) ** 2, contexto=f"R2 [{cx} x {cy}]")


def test_r2_igual_r_ao_quadrado_na_regressao_simples(coluna_numerica):
    """Identidade teorica da regressao SIMPLES: R2 = r^2. Se as duas
    implementacoes (correlacao e regressao) concordam nisso, ambas estao
    coerentes."""
    for cx, cy in PARES_DATASET:
        x, y = coluna_numerica(cx), coluna_numerica(cy)
        r = a.correlacao_pearson(x, y)
        m = a.regressao_linear(x, y)
        quase_igual(m["r2"], r * r, contexto=f"R2 = r^2 [{cx} x {cy}]")


def test_decomposicao_da_variacao(coluna_numerica):
    """SQtot = SQreg + SQres -- a identidade fundamental da ANOVA da regressao."""
    x, y = coluna_numerica("temp"), coluna_numerica("cnt")
    m = a.regressao_linear(x, y)
    quase_igual(m["sq_regressao"] + m["sq_residuos"], m["sq_total"],
                contexto="SQtot = SQreg + SQres")


def test_reta_passa_pelo_ponto_medio(coluna_numerica):
    """A reta de minimos quadrados sempre passa por (x_barra, y_barra)."""
    from minhastats import descritiva as d

    x, y = coluna_numerica("temp"), coluna_numerica("cnt")
    m = a.regressao_linear(x, y)
    quase_igual(a.prever(m, d.media(x)), d.media(y),
                contexto="a reta passa por (x_barra, y_barra)")


def test_soma_dos_residuos_e_zero(coluna_numerica):
    """Propriedade dos minimos quadrados: a soma dos residuos e nula.
    Comparamos com uma fracao do desvio dos y para tornar a tolerancia
    independente da escala da variavel."""
    x, y = coluna_numerica("temp"), coluna_numerica("cnt")
    m = a.regressao_linear(x, y)
    res = a.residuos(m, x, y)
    escala = sum(abs(v) for v in y)
    assert abs(sum(res)) / escala < 1e-12


def test_predicao_interativa():
    """Campo de predicao do Modulo 5: usuario digita X, recebe Y_chapeu."""
    x = [1.0, 2.0, 3.0, 4.0]
    y = [2.0, 4.0, 6.0, 8.0]
    m = a.regressao_linear(x, y)
    assert a.prever(m, 10.0) == pytest.approx(20.0, rel=1e-12)
    assert a.prever(m, 0.0) == pytest.approx(0.0, abs=1e-12)


def test_regressao_com_x_constante_levanta_erro():
    with pytest.raises(ValueError, match="constante"):
        a.regressao_linear([5.0, 5.0, 5.0], [1.0, 2.0, 3.0])
