"""
Validacao do modulo minhastats.distribuicoes contra SciPy.

Referencias usadas:
    Normal      -> scipy.stats.norm.pdf / .cdf
    Uniforme    -> scipy.stats.uniform.pdf
    Exponencial -> scipy.stats.expon.pdf
    Binomial    -> scipy.stats.binom.pmf
    Poisson     -> scipy.stats.poisson.pmf
    C(n,k)      -> math.comb
"""

import math

import numpy as np
import pytest
from scipy import stats as scipy_stats

from minhastats import distribuicoes as dist
from conftest import TOL, quase_igual


# ===========================================================================
# NORMAL
# ===========================================================================


def test_normal_pdf_no_pico():
    """No ponto x = mu a densidade vale 1/(sigma*sqrt(2*pi))."""
    assert dist.normal_pdf(0.0, 0.0, 1.0) == pytest.approx(
        1.0 / math.sqrt(2 * math.pi), rel=1e-12
    )


@pytest.mark.parametrize("mu,sigma", [(0, 1), (10, 3), (-5, 0.5), (100, 15), (0.5, 0.2)])
@pytest.mark.parametrize("x", [-3.0, -1.0, 0.0, 0.7, 2.5, 10.0, 100.0])
def test_normal_pdf_vs_scipy(x, mu, sigma):
    quase_igual(dist.normal_pdf(x, mu, sigma),
                float(scipy_stats.norm.pdf(x, loc=mu, scale=sigma)),
                contexto=f"normal_pdf(x={x}, mu={mu}, sigma={sigma})")


@pytest.mark.parametrize("mu,sigma", [(0, 1), (10, 3), (-5, 0.5), (100, 15)])
@pytest.mark.parametrize("x", [-3.0, -1.0, 0.0, 0.7, 2.5, 10.0, 100.0])
def test_normal_cdf_vs_scipy(x, mu, sigma):
    quase_igual(dist.normal_cdf(x, mu, sigma),
                float(scipy_stats.norm.cdf(x, loc=mu, scale=sigma)),
                contexto=f"normal_cdf(x={x}, mu={mu}, sigma={sigma})")


def test_normal_cdf_propriedades():
    """F(mu) = 0.5 por simetria; F cresce monotonicamente."""
    assert dist.normal_cdf(10.0, 10.0, 3.0) == pytest.approx(0.5, rel=1e-12)
    valores = [dist.normal_cdf(x, 0, 1) for x in [-3, -1, 0, 1, 3]]
    assert valores == sorted(valores)


def test_regra_empirica_68_95_99():
    """Verificacao classica: dentro de 1, 2 e 3 desvios ficam ~68%, ~95% e
    ~99,7% da massa da Normal."""
    for k, esperado in [(1, 0.6827), (2, 0.9545), (3, 0.9973)]:
        massa = dist.normal_cdf(k, 0, 1) - dist.normal_cdf(-k, 0, 1)
        assert massa == pytest.approx(esperado, abs=1e-4)


def test_estimar_normal_vs_numpy(coluna_numerica):
    x = coluna_numerica("temp")
    p = dist.estimar_normal(x)
    quase_igual(p["mu"], float(np.mean(x)), contexto="mu estimado")
    quase_igual(p["sigma"], float(np.std(x, ddof=1)), contexto="sigma estimado")


def test_normal_sigma_invalido():
    with pytest.raises(ValueError, match="sigma deve ser positivo"):
        dist.normal_pdf(0.0, 0.0, 0.0)


# ===========================================================================
# UNIFORME
# ===========================================================================


@pytest.mark.parametrize("a,b", [(0, 1), (2, 10), (-5, 5)])
@pytest.mark.parametrize("x", [-10.0, 0.0, 3.0, 5.0, 20.0])
def test_uniforme_pdf_vs_scipy(x, a, b):
    """scipy parametriza a Uniforme por (loc=a, scale=b-a)."""
    quase_igual(dist.uniforme_pdf(x, a, b),
                float(scipy_stats.uniform.pdf(x, loc=a, scale=b - a)),
                contexto=f"uniforme_pdf(x={x}, a={a}, b={b})")


def test_estimar_uniforme(coluna_numerica):
    x = coluna_numerica("hum")
    p = dist.estimar_uniforme(x)
    assert p["a"] == pytest.approx(float(np.min(x)), rel=TOL)
    assert p["b"] == pytest.approx(float(np.max(x)), rel=TOL)


def test_uniforme_limites_invalidos():
    with pytest.raises(ValueError, match="maior que a"):
        dist.uniforme_pdf(0.5, 1.0, 1.0)


# ===========================================================================
# EXPONENCIAL
# ===========================================================================


@pytest.mark.parametrize("lam", [0.5, 1.0, 2.0, 10.0])
@pytest.mark.parametrize("x", [0.0, 0.1, 1.0, 5.0, 20.0])
def test_exponencial_pdf_vs_scipy(x, lam):
    """scipy usa scale = 1/lambda."""
    quase_igual(dist.exponencial_pdf(x, lam),
                float(scipy_stats.expon.pdf(x, scale=1.0 / lam)),
                contexto=f"exponencial_pdf(x={x}, lam={lam})")


def test_exponencial_negativa_e_zero():
    assert dist.exponencial_pdf(-1.0, 2.0) == 0.0


def test_estimar_exponencial(amostras_aleatorias):
    """A amostra 'assimetrica' foi gerada com expovariate(0.5); a estimativa
    de maxima verossimilhanca 1/x_barra tem de recuperar algo proximo de 0.5."""
    x = amostras_aleatorias["assimetrica"]
    p = dist.estimar_exponencial(x)
    quase_igual(p["lam"], 1.0 / float(np.mean(x)), contexto="lambda estimado")
    assert p["lam"] == pytest.approx(0.5, rel=0.15)


def test_exponencial_lambda_invalido():
    with pytest.raises(ValueError, match="lambda deve ser positiva"):
        dist.exponencial_pdf(1.0, 0.0)


# ===========================================================================
# BINOMIAL
# ===========================================================================


@pytest.mark.parametrize("n,k", [(5, 0), (5, 2), (5, 5), (10, 3), (20, 10), (50, 25)])
def test_coeficiente_binomial_vs_math_comb(n, k):
    assert dist.coeficiente_binomial(n, k) == math.comb(n, k)


def test_coeficiente_binomial_fora_do_dominio():
    assert dist.coeficiente_binomial(5, 6) == 0
    assert dist.coeficiente_binomial(5, -1) == 0


@pytest.mark.parametrize("n,p", [(10, 0.5), (20, 0.3), (5, 0.9), (100, 0.07)])
def test_binomial_pmf_vs_scipy(n, p):
    for k in range(0, n + 1):
        quase_igual(dist.binomial_pmf(k, n, p),
                    float(scipy_stats.binom.pmf(k, n, p)),
                    contexto=f"binomial_pmf(k={k}, n={n}, p={p})")


@pytest.mark.parametrize("n,p", [(10, 0.5), (20, 0.3), (100, 0.07)])
def test_binomial_soma_das_probabilidades_e_um(n, p):
    total = sum(dist.binomial_pmf(k, n, p) for k in range(n + 1))
    quase_igual(total, 1.0, contexto=f"soma da pmf Binomial(n={n}, p={p})")


def test_binomial_p_invalido():
    with pytest.raises(ValueError, match="p deve estar em"):
        dist.binomial_pmf(1, 10, 1.5)


def test_estimar_binomial(coluna_numerica):
    """weathersit vai de 1 a 4; p estimado = media/n."""
    x = coluna_numerica("weathersit")
    p = dist.estimar_binomial(x)
    assert 0.0 <= p["p"] <= 1.0
    quase_igual(p["p"], float(np.mean(x)) / p["n"], contexto="p estimado")


# ===========================================================================
# POISSON
# ===========================================================================


@pytest.mark.parametrize("lam", [0.5, 1.0, 3.0, 10.0, 50.0, 189.0])
def test_poisson_pmf_vs_scipy(lam):
    """Inclui lambda = 189 (a media de 'cnt'): sem a escala logaritmica,
    lam**k estouraria o float e o teste falharia com OverflowError."""
    ks = [0, 1, 2, 5, 10, 50, 100, 189, 300]
    for k in ks:
        quase_igual(dist.poisson_pmf(k, lam),
                    float(scipy_stats.poisson.pmf(k, lam)),
                    contexto=f"poisson_pmf(k={k}, lam={lam})")


def test_poisson_lambda_grande_nao_estoura():
    """Prova de que a implementacao logaritmica resolve o overflow."""
    valor = dist.poisson_pmf(500, 500.0)
    assert math.isfinite(valor) and valor > 0
    quase_igual(valor, float(scipy_stats.poisson.pmf(500, 500.0)),
                contexto="poisson com lambda = 500")


@pytest.mark.parametrize("lam", [1.0, 5.0, 20.0])
def test_poisson_soma_converge_para_um(lam):
    total = sum(dist.poisson_pmf(k, lam) for k in range(0, 200))
    quase_igual(total, 1.0, tol=1e-9, contexto=f"soma da pmf Poisson(lam={lam})")


def test_poisson_negativo_e_zero():
    assert dist.poisson_pmf(-1, 5.0) == 0.0


def test_estimar_poisson(coluna_numerica):
    x = coluna_numerica("cnt")
    quase_igual(dist.estimar_poisson(x)["lam"], float(np.mean(x)),
                contexto="lambda estimado da Poisson")


def test_indice_dispersao_detecta_sobredispersao(coluna_numerica):
    """'cnt' e fortemente sobredisperso (variancia >> media), logo NAO segue
    uma Poisson. Este numero e uma das descobertas do Modulo 6."""
    x = coluna_numerica("cnt")
    id_ = dist.indice_dispersao(x)
    quase_igual(id_, float(np.var(x, ddof=1) / np.mean(x)),
                contexto="indice de dispersao")
    assert id_ > 5, "esperava-se forte sobredispersao em 'cnt'"


# ===========================================================================
# QUALIDADE DO AJUSTE
# ===========================================================================


def test_qualidade_ajuste_perfeito_da_uniforme():
    """Dados perfeitamente uniformes em [0,1] contra a densidade Uniforme:
    o qui-quadrado tem de ser praticamente zero."""
    from minhastats.frequencias import tabela_frequencias_continua

    n = 10000
    dados = [i / (n - 1) for i in range(n)]
    linhas = tabela_frequencias_continua(dados, k=10)
    r = dist.qualidade_ajuste(linhas, lambda x: dist.uniforme_pdf(x, 0.0, 1.0), n)
    assert r["qui_quadrado"] < 1.0


def test_qualidade_ajuste_normal_melhor_que_uniforme(amostras_aleatorias):
    """Para dados gerados de uma Normal, o ajuste Normal tem de ser
    MUITO melhor que o Uniforme -- e isso que a aplicacao usa para
    justificar a escolha da distribuicao candidata."""
    from minhastats.frequencias import tabela_frequencias_continua

    x = amostras_aleatorias["normal"]
    n = len(x)
    linhas = tabela_frequencias_continua(x, k=12)

    pn = dist.estimar_normal(x)
    pu = dist.estimar_uniforme(x)

    ajuste_normal = dist.qualidade_ajuste(
        linhas, lambda v: dist.normal_pdf(v, pn["mu"], pn["sigma"]), n
    )
    ajuste_uniforme = dist.qualidade_ajuste(
        linhas, lambda v: dist.uniforme_pdf(v, pu["a"], pu["b"]), n
    )
    assert ajuste_normal["qui_quadrado"] < ajuste_uniforme["qui_quadrado"]


def test_qualidade_ajuste_estrutura_do_retorno(coluna_numerica):
    from minhastats.frequencias import tabela_frequencias_continua

    x = coluna_numerica("temp")
    linhas = tabela_frequencias_continua(x, k=10)
    p = dist.estimar_normal(x)
    r = dist.qualidade_ajuste(linhas, lambda v: dist.normal_pdf(v, p["mu"], p["sigma"]), len(x))

    assert r["classes"] == 10
    assert len(r["detalhes"]) == 10
    assert r["qui_quadrado"] >= 0
    quase_igual(r["qui_quadrado_por_classe"], r["qui_quadrado"] / r["classes"],
                contexto="qui-quadrado por classe")
