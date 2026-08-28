"""
Validacao do modulo minhastats.descritiva contra NumPy / statistics.

Referencias usadas:
    media                      -> numpy.mean
    mediana                    -> numpy.median / statistics.median
    moda                       -> statistics.multimode
    variancia populacional     -> numpy.var(ddof=0)
    variancia amostral         -> numpy.var(ddof=1) / statistics.variance
    desvio padrao              -> numpy.std(ddof=0 e ddof=1)
    percentis                  -> numpy.percentile (method="linear")
    assimetria de momento      -> scipy.stats.skew(bias=True)
    curtose                    -> scipy.stats.kurtosis(fisher=True, bias=True)
"""

import math
import statistics

import numpy as np
import pytest
from scipy import stats as scipy_stats

from minhastats import descritiva as d
from conftest import TOL, quase_igual

# Colunas numericas do dataset usadas na validacao contra dados reais
COLUNAS = ["temp", "atemp", "hum", "windspeed", "casual", "registered", "cnt"]


# ===========================================================================
# MEDIA
# ===========================================================================


def test_media_caso_manual(casos_fixos):
    """Caso conferido a mao: (2+4+4+4+5+5+7+9)/8 = 40/8 = 5."""
    assert d.media(casos_fixos["manual"]) == 5.0


@pytest.mark.parametrize("cenario", ["normal", "grande_escala", "pequena_escala",
                                     "assimetrica", "discreta", "mista"])
def test_media_vs_numpy_sintetico(amostras_aleatorias, cenario):
    x = amostras_aleatorias[cenario]
    quase_igual(d.media(x), float(np.mean(x)), contexto=f"media [{cenario}]")


@pytest.mark.parametrize("coluna", COLUNAS)
def test_media_vs_numpy_dataset(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    quase_igual(d.media(x), float(np.mean(x)), contexto=f"media [dataset.{coluna}]")


# ===========================================================================
# MEDIANA
# ===========================================================================


def test_mediana_n_impar(casos_fixos):
    """n impar: a mediana e o elemento central, 5."""
    assert d.mediana(casos_fixos["impar"]) == 5.0


def test_mediana_n_par(casos_fixos):
    """n par: media dos dois centrais, (20+30)/2 = 25."""
    assert d.mediana(casos_fixos["par"]) == 25.0


@pytest.mark.parametrize("cenario", ["normal", "assimetrica", "discreta", "mista"])
def test_mediana_vs_numpy_sintetico(amostras_aleatorias, cenario):
    x = amostras_aleatorias[cenario]
    quase_igual(d.mediana(x), float(np.median(x)), contexto=f"mediana [{cenario}]")
    quase_igual(d.mediana(x), statistics.median(x), contexto=f"mediana/statistics [{cenario}]")


@pytest.mark.parametrize("coluna", COLUNAS)
def test_mediana_vs_numpy_dataset(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    quase_igual(d.mediana(x), float(np.median(x)), contexto=f"mediana [dataset.{coluna}]")


# ===========================================================================
# MODA
# ===========================================================================


def test_moda_unimodal(casos_fixos):
    assert d.moda(casos_fixos["manual"]) == [4.0]


def test_moda_bimodal(casos_fixos):
    """Distribuicao bimodal: nossa funcao devolve TODAS as modas."""
    assert d.moda(casos_fixos["bimodal"]) == [1.0, 3.0]


def test_moda_amodal(casos_fixos):
    """Sem repeticoes -> amodal -> lista vazia."""
    assert d.moda(casos_fixos["amodal"]) == []


@pytest.mark.parametrize("cenario", ["discreta"])
def test_moda_vs_statistics_multimode(amostras_aleatorias, cenario):
    """statistics.multimode tambem devolve todas as modas -- comparacao direta."""
    x = amostras_aleatorias[cenario]
    assert d.moda(x) == sorted(statistics.multimode(x))


@pytest.mark.parametrize("coluna", ["weathersit", "hr", "weekday", "season"])
def test_moda_vs_statistics_dataset(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    assert d.moda(x) == sorted(statistics.multimode(x))


# ===========================================================================
# AMPLITUDE, MINIMO, MAXIMO
# ===========================================================================


def test_amplitude_caso_manual(casos_fixos):
    """9 - 2 = 7."""
    assert d.amplitude(casos_fixos["manual"]) == 7.0


@pytest.mark.parametrize("coluna", COLUNAS)
def test_amplitude_vs_numpy_dataset(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    quase_igual(d.amplitude(x), float(np.ptp(x)), contexto=f"amplitude [{coluna}]")
    quase_igual(d.minimo(x), float(np.min(x)), contexto=f"minimo [{coluna}]")
    quase_igual(d.maximo(x), float(np.max(x)), contexto=f"maximo [{coluna}]")


# ===========================================================================
# VARIANCIA E DESVIO PADRAO
# ===========================================================================


def test_variancia_caso_manual(casos_fixos):
    """Somatorio dos desvios ao quadrado = 32; N=8 -> pop 4.0; n-1=7 -> am 32/7."""
    x = casos_fixos["manual"]
    assert d.variancia_populacional(x) == pytest.approx(4.0, rel=TOL)
    assert d.variancia_amostral(x) == pytest.approx(32.0 / 7.0, rel=TOL)


def test_variancia_de_constante_e_zero(casos_fixos):
    x = casos_fixos["constante"]
    assert d.variancia_populacional(x) == 0.0
    assert d.variancia_amostral(x) == 0.0


@pytest.mark.parametrize("cenario", ["normal", "grande_escala", "pequena_escala",
                                     "assimetrica", "discreta", "mista"])
def test_variancia_vs_numpy_sintetico(amostras_aleatorias, cenario):
    """O cenario 'grande_escala' e o teste critico da estabilidade numerica:
    valores ~1e6 com desvio ~1e4. A formula ingenua (soma de quadrados menos
    n vezes media ao quadrado) perderia precisao aqui; a nossa, em dois
    passos, nao."""
    x = amostras_aleatorias[cenario]
    quase_igual(d.variancia_populacional(x), float(np.var(x, ddof=0)),
                contexto=f"var_pop [{cenario}]")
    quase_igual(d.variancia_amostral(x), float(np.var(x, ddof=1)),
                contexto=f"var_am [{cenario}]")
    quase_igual(d.desvio_padrao_populacional(x), float(np.std(x, ddof=0)),
                contexto=f"dp_pop [{cenario}]")
    quase_igual(d.desvio_padrao_amostral(x), float(np.std(x, ddof=1)),
                contexto=f"dp_am [{cenario}]")


@pytest.mark.parametrize("coluna", COLUNAS)
def test_variancia_vs_numpy_dataset(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    quase_igual(d.variancia_populacional(x), float(np.var(x, ddof=0)),
                contexto=f"var_pop [dataset.{coluna}]")
    quase_igual(d.variancia_amostral(x), float(np.var(x, ddof=1)),
                contexto=f"var_am [dataset.{coluna}]")
    quase_igual(d.desvio_padrao_amostral(x), float(np.std(x, ddof=1)),
                contexto=f"dp_am [dataset.{coluna}]")


def test_variancia_amostral_vs_statistics(amostras_aleatorias):
    x = amostras_aleatorias["normal"]
    quase_igual(d.variancia_amostral(x), statistics.variance(x),
                contexto="var_am vs statistics.variance")
    quase_igual(d.variancia_populacional(x), statistics.pvariance(x),
                contexto="var_pop vs statistics.pvariance")


def test_relacao_variancia_amostral_e_populacional(amostras_aleatorias):
    """Identidade algebrica: s^2 = sigma^2 * n / (n-1)."""
    x = amostras_aleatorias["normal"]
    n = len(x)
    quase_igual(d.variancia_amostral(x),
                d.variancia_populacional(x) * n / (n - 1),
                contexto="relacao s^2 = sigma^2 * n/(n-1)")


# ===========================================================================
# COEFICIENTE DE VARIACAO
# ===========================================================================


@pytest.mark.parametrize("coluna", ["temp", "hum", "cnt", "registered"])
def test_coeficiente_variacao_vs_numpy(coluna_numerica, coluna):
    """CV = s / media * 100."""
    x = coluna_numerica(coluna)
    esperado = float(np.std(x, ddof=1) / abs(np.mean(x)) * 100.0)
    quase_igual(d.coeficiente_variacao(x), esperado, contexto=f"CV [{coluna}]")


def test_coeficiente_variacao_media_zero_levanta_erro():
    with pytest.raises(ValueError, match="media da amostra e zero"):
        d.coeficiente_variacao([-1.0, 0.0, 1.0])


def test_erro_padrao_media(amostras_aleatorias):
    x = amostras_aleatorias["normal"]
    esperado = float(np.std(x, ddof=1) / math.sqrt(len(x)))
    quase_igual(d.erro_padrao_media(x), esperado, contexto="erro padrao da media")


# ===========================================================================
# PERCENTIS E QUARTIS
# ===========================================================================


@pytest.mark.parametrize("p", [0, 1, 5, 10, 25, 33.3, 50, 66.7, 75, 90, 95, 99, 100])
@pytest.mark.parametrize("cenario", ["normal", "assimetrica", "discreta", "mista"])
def test_percentil_vs_numpy_sintetico(amostras_aleatorias, cenario, p):
    """numpy.percentile usa por padrao o metodo 'linear' (tipo 7), o mesmo
    que implementamos."""
    x = amostras_aleatorias[cenario]
    quase_igual(d.percentil(x, p), float(np.percentile(x, p, method="linear")),
                contexto=f"P{p} [{cenario}]")


@pytest.mark.parametrize("p", [0, 25, 50, 75, 90, 99, 100])
@pytest.mark.parametrize("coluna", COLUNAS)
def test_percentil_vs_numpy_dataset(coluna_numerica, coluna, p):
    x = coluna_numerica(coluna)
    quase_igual(d.percentil(x, p), float(np.percentile(x, p, method="linear")),
                contexto=f"P{p} [dataset.{coluna}]")


def test_quartil_2_e_a_mediana(amostras_aleatorias):
    """Q2 tem de coincidir com a mediana -- consistencia interna do nucleo."""
    for cenario, x in amostras_aleatorias.items():
        if len(x) >= 2:
            quase_igual(d.quartil(x, 2), d.mediana(x), contexto=f"Q2 = Md [{cenario}]")


def test_quartis_e_iqr_vs_numpy(coluna_numerica):
    x = coluna_numerica("cnt")
    q1, q2, q3 = d.quartis(x)
    quase_igual(q1, float(np.percentile(x, 25)), contexto="Q1 [cnt]")
    quase_igual(q2, float(np.percentile(x, 50)), contexto="Q2 [cnt]")
    quase_igual(q3, float(np.percentile(x, 75)), contexto="Q3 [cnt]")
    quase_igual(d.amplitude_interquartil(x),
                float(np.percentile(x, 75) - np.percentile(x, 25)),
                contexto="IQR [cnt]")


def test_percentil_fora_do_intervalo_levanta_erro():
    with pytest.raises(ValueError, match="entre 0 e 100"):
        d.percentil([1.0, 2.0, 3.0], 101)
    with pytest.raises(ValueError, match="entre 0 e 100"):
        d.percentil([1.0, 2.0, 3.0], -1)


def test_quartil_invalido_levanta_erro():
    with pytest.raises(ValueError, match="deve ser 1, 2 ou 3"):
        d.quartil([1.0, 2.0, 3.0], 4)


# ===========================================================================
# FORMA: ASSIMETRIA E CURTOSE
# ===========================================================================


@pytest.mark.parametrize("cenario", ["normal", "assimetrica", "discreta", "mista"])
def test_assimetria_momento_vs_scipy(amostras_aleatorias, cenario):
    """scipy.stats.skew(bias=True) usa exatamente o terceiro momento
    padronizado com divisor n que implementamos."""
    x = amostras_aleatorias[cenario]
    quase_igual(d.assimetria_momento(x), float(scipy_stats.skew(x, bias=True)),
                contexto=f"assimetria de momento [{cenario}]")


@pytest.mark.parametrize("coluna", COLUNAS)
def test_assimetria_momento_vs_scipy_dataset(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    quase_igual(d.assimetria_momento(x), float(scipy_stats.skew(x, bias=True)),
                contexto=f"assimetria [dataset.{coluna}]")


@pytest.mark.parametrize("cenario", ["normal", "assimetrica", "discreta", "mista"])
def test_curtose_vs_scipy(amostras_aleatorias, cenario):
    """scipy.stats.kurtosis(fisher=True, bias=True) = excesso de curtose."""
    x = amostras_aleatorias[cenario]
    quase_igual(d.curtose_momento(x),
                float(scipy_stats.kurtosis(x, fisher=True, bias=True)),
                contexto=f"curtose [{cenario}]")


@pytest.mark.parametrize("coluna", COLUNAS)
def test_curtose_vs_scipy_dataset(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    quase_igual(d.curtose_momento(x),
                float(scipy_stats.kurtosis(x, fisher=True, bias=True)),
                contexto=f"curtose [dataset.{coluna}]")


def test_assimetria_pearson_sinal_coerente(coluna_numerica):
    """A coluna 'casual' e fortemente assimetrica a direita: media > mediana,
    logo o coeficiente de Pearson tem de ser positivo, assim como o de
    momento."""
    x = coluna_numerica("casual")
    assert d.assimetria_pearson(x) > 0
    assert d.assimetria_momento(x) > 0
    assert d.media(x) > d.mediana(x)


def test_assimetria_de_constante_e_zero(casos_fixos):
    """Distribuicao degenerada: desvio padrao zero -> retornamos 0, sem
    divisao por zero."""
    x = casos_fixos["constante"]
    assert d.assimetria_pearson(x) == 0.0
    assert d.assimetria_momento(x) == 0.0
    assert d.curtose_momento(x) == 0.0


# ===========================================================================
# TRATAMENTO DE ENTRADAS INVALIDAS
# ===========================================================================


def test_amostra_vazia_levanta_erro():
    with pytest.raises(ValueError, match="Amostra insuficiente"):
        d.media([])


def test_variancia_amostral_exige_dois_valores():
    with pytest.raises(ValueError, match="Amostra insuficiente"):
        d.variancia_amostral([5.0])


def test_nan_e_descartado():
    """NaN nao pode contaminar o resultado: [1, NaN, 3] tem media 2."""
    assert d.media([1.0, float("nan"), 3.0]) == 2.0
    assert d.mediana([1.0, float("nan"), 3.0]) == 2.0


def test_valores_nao_numericos_sao_descartados():
    assert d.media([1.0, "texto", 3.0, None]) == 2.0


# ===========================================================================
# RESUMO CONSOLIDADO (usado pela interface)
# ===========================================================================


def test_resumo_bate_com_numpy_em_todos_os_campos(coluna_numerica):
    """Este teste amarra o contrato entre o nucleo e a interface: e este
    dicionario que o Modulo 2 exibe na tela."""
    x = coluna_numerica("temp")
    r = d.resumo(x)

    assert r["n"] == len(x)
    quase_igual(r["media"], float(np.mean(x)), contexto="resumo.media")
    quase_igual(r["mediana"], float(np.median(x)), contexto="resumo.mediana")
    quase_igual(r["minimo"], float(np.min(x)), contexto="resumo.minimo")
    quase_igual(r["maximo"], float(np.max(x)), contexto="resumo.maximo")
    quase_igual(r["amplitude"], float(np.ptp(x)), contexto="resumo.amplitude")
    quase_igual(r["q1"], float(np.percentile(x, 25)), contexto="resumo.q1")
    quase_igual(r["q3"], float(np.percentile(x, 75)), contexto="resumo.q3")
    quase_igual(r["iqr"], float(np.percentile(x, 75) - np.percentile(x, 25)),
                contexto="resumo.iqr")
    quase_igual(r["variancia_amostral"], float(np.var(x, ddof=1)),
                contexto="resumo.variancia_amostral")
    quase_igual(r["desvio_padrao_amostral"], float(np.std(x, ddof=1)),
                contexto="resumo.desvio_padrao_amostral")
    quase_igual(r["assimetria_momento"], float(scipy_stats.skew(x, bias=True)),
                contexto="resumo.assimetria_momento")
    quase_igual(r["curtose"], float(scipy_stats.kurtosis(x, fisher=True, bias=True)),
                contexto="resumo.curtose")
