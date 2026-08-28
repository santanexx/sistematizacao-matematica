"""
Validacao do modulo minhastats.frequencias.

Referencias usadas:
    contagem de categorias  -> collections.Counter
    classes do histograma   -> numpy.histogram
    limites de outliers     -> numpy.percentile (regra de Tukey)
"""

import math
from collections import Counter

import numpy as np
import pytest

from minhastats import frequencias as f
from conftest import TOL, quase_igual


# ===========================================================================
# REGRA DE STURGES
# ===========================================================================


@pytest.mark.parametrize(
    "n,esperado",
    [
        (1, 1),
        (2, 2),      # ceil(1 + log2(2))  = ceil(2)     = 2
        (10, 5),     # ceil(1 + 3.3219)   = ceil(4.32)  = 5
        (100, 8),    # ceil(1 + 6.6439)   = ceil(7.64)  = 8
        (1000, 11),  # ceil(1 + 9.9658)   = ceil(10.97) = 11
        (17379, 16), # ceil(1 + 14.0851)  = ceil(15.09) = 16 (nosso dataset)
    ],
)
def test_regra_sturges_valores_conhecidos(n, esperado):
    assert f.regra_sturges(n) == esperado


def test_sturges_bate_com_numpy(coluna_numerica):
    """numpy.histogram_bin_edges com bins='sturges' usa a mesma regra."""
    x = coluna_numerica("temp")
    bordas = np.histogram_bin_edges(x, bins="sturges")
    assert f.regra_sturges(len(x)) == len(bordas) - 1


def test_sturges_n_invalido():
    with pytest.raises(ValueError, match="n deve ser positivo"):
        f.regra_sturges(0)


# ===========================================================================
# TABELA DE FREQUENCIAS CATEGORICA
# ===========================================================================


def test_tabela_categorica_caso_manual():
    dados = ["a", "b", "a", "c", "a", "b"]
    linhas = f.tabela_frequencias_categorica(dados)

    assert linhas[0]["categoria"] == "a"
    assert linhas[0]["fi"] == 3
    assert linhas[0]["percentual"] == pytest.approx(50.0, rel=TOL)
    # a acumulada da ultima linha tem de fechar em 100%
    assert linhas[-1]["Fi"] == 6
    assert linhas[-1]["Fr_percentual"] == pytest.approx(100.0, rel=TOL)


@pytest.mark.parametrize("coluna", ["season", "weathersit", "weekday", "workingday", "holiday"])
def test_tabela_categorica_vs_counter(dataset, coluna):
    """As contagens tem de bater exatamente com collections.Counter."""
    valores = dataset[coluna]
    linhas = f.tabela_frequencias_categorica(valores)
    referencia = Counter(valores)

    assert len(linhas) == len(referencia)
    for linha in linhas:
        assert linha["fi"] == referencia[linha["categoria"]], (
            f"frequencia divergente na categoria {linha['categoria']}"
        )


@pytest.mark.parametrize("coluna", ["season", "weathersit", "weekday"])
def test_frequencias_relativas_somam_um(dataset, coluna):
    linhas = f.tabela_frequencias_categorica(dataset[coluna])
    quase_igual(sum(l["fr"] for l in linhas), 1.0, contexto=f"soma fr [{coluna}]")
    quase_igual(sum(l["percentual"] for l in linhas), 100.0,
                contexto=f"soma % [{coluna}]")


def test_ordenacao_por_frequencia_e_decrescente(dataset):
    linhas = f.tabela_frequencias_categorica(dataset["weathersit"],
                                             ordenar_por="frequencia")
    frequencias = [l["fi"] for l in linhas]
    assert frequencias == sorted(frequencias, reverse=True)


def test_ordenacao_por_categoria(dataset):
    linhas = f.tabela_frequencias_categorica(dataset["season"],
                                             ordenar_por="categoria")
    rotulos = [l["categoria"] for l in linhas]
    assert rotulos == sorted(rotulos)


def test_tabela_categorica_vazia_levanta_erro():
    with pytest.raises(ValueError, match="Nenhum valor valido"):
        f.tabela_frequencias_categorica([])


# ===========================================================================
# TABELA DE FREQUENCIAS EM CLASSES (CONTINUA)
# ===========================================================================


@pytest.mark.parametrize("coluna", ["temp", "atemp", "hum", "windspeed", "cnt"])
@pytest.mark.parametrize("k", [5, 10, 16, 20])
def test_classes_vs_numpy_histogram(coluna_numerica, coluna, k):
    """As contagens por classe tem de bater com numpy.histogram usando o
    mesmo numero de bins de igual amplitude. Este e o teste mais duro do
    modulo: qualquer erro de arredondamento nas bordas apareceria aqui."""
    x = coluna_numerica(coluna)
    linhas = f.tabela_frequencias_continua(x, k=k)
    contagens_np, _ = np.histogram(x, bins=k)

    assert len(linhas) == k
    obtidas = [l["fi"] for l in linhas]
    assert obtidas == list(contagens_np), (
        f"[{coluna}, k={k}]\n  minhastats: {obtidas}\n  numpy     : {list(contagens_np)}"
    )


@pytest.mark.parametrize("coluna", ["temp", "hum", "cnt"])
def test_bordas_das_classes_vs_numpy(coluna_numerica, coluna):
    x = coluna_numerica(coluna)
    linhas = f.tabela_frequencias_continua(x, k=10)
    _, bordas_np = np.histogram(x, bins=10)

    for i, linha in enumerate(linhas):
        quase_igual(linha["li"], float(bordas_np[i]), contexto=f"li classe {i}")
        quase_igual(linha["ls"], float(bordas_np[i + 1]), contexto=f"ls classe {i}")


@pytest.mark.parametrize("coluna", ["temp", "hum", "cnt", "casual"])
def test_soma_das_frequencias_e_n(coluna_numerica, coluna):
    """Nenhum valor pode ficar de fora -- em especial o maximo, que cai
    exatamente na borda superior da ultima classe."""
    x = coluna_numerica(coluna)
    linhas = f.tabela_frequencias_continua(x)
    assert sum(l["fi"] for l in linhas) == len(x)
    quase_igual(linhas[-1]["Fr_percentual"], 100.0, contexto="acumulada final")


def test_classes_usam_sturges_por_padrao(coluna_numerica):
    x = coluna_numerica("temp")
    assert len(f.tabela_frequencias_continua(x)) == f.regra_sturges(len(x))


def test_ponto_medio_das_classes():
    dados = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    linhas = f.tabela_frequencias_continua(dados, k=2)
    # amplitude 10, k=2 -> h=5 -> classes [0;5) e [5;10]
    assert linhas[0]["ponto_medio"] == pytest.approx(2.5, rel=TOL)
    assert linhas[1]["ponto_medio"] == pytest.approx(7.5, rel=TOL)


def test_variavel_constante_gera_classe_unica():
    """Caso degenerado: amplitude zero. Nao pode dividir por zero."""
    linhas = f.tabela_frequencias_continua([5.0] * 20)
    assert len(linhas) == 1
    assert linhas[0]["fi"] == 20


def test_numero_de_classes_invalido():
    with pytest.raises(ValueError, match="numero de classes"):
        f.tabela_frequencias_continua([1.0, 2.0, 3.0], k=0)


# ===========================================================================
# OUTLIERS PELA REGRA DO IQR
# ===========================================================================


def test_outliers_caso_manual():
    """[1..10] mais o valor 100. Q1=3, Q3=8 (metodo linear com n=11),
    IQR=5, LS = 8 + 7.5 = 15.5 -> so o 100 e outlier."""
    dados = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 100.0]
    r = f.detectar_outliers_iqr(dados)
    assert r["outliers"] == [100.0]
    assert r["n_acima"] == 1
    assert r["n_abaixo"] == 0


@pytest.mark.parametrize("coluna", ["temp", "hum", "windspeed", "casual", "cnt"])
def test_limites_de_outliers_vs_numpy(coluna_numerica, coluna):
    """Os limites de Tukey calculados pelo nosso nucleo tem de coincidir com
    os obtidos via numpy.percentile."""
    x = coluna_numerica(coluna)
    r = f.detectar_outliers_iqr(x)

    q1_np = float(np.percentile(x, 25))
    q3_np = float(np.percentile(x, 75))
    iqr_np = q3_np - q1_np

    quase_igual(r["q1"], q1_np, contexto=f"Q1 [{coluna}]")
    quase_igual(r["q3"], q3_np, contexto=f"Q3 [{coluna}]")
    quase_igual(r["iqr"], iqr_np, contexto=f"IQR [{coluna}]")
    quase_igual(r["limite_inferior"], q1_np - 1.5 * iqr_np, contexto=f"LI [{coluna}]")
    quase_igual(r["limite_superior"], q3_np + 1.5 * iqr_np, contexto=f"LS [{coluna}]")

    # a contagem de outliers tem de bater com a mascara feita em numpy
    arr = np.array(x)
    esperado = int(np.sum((arr < r["limite_inferior"]) | (arr > r["limite_superior"])))
    assert r["n_outliers"] == esperado


def test_fator_3_detecta_menos_outliers(coluna_numerica):
    """Outliers EXTREMOS (f=3) sao um subconjunto dos moderados (f=1.5)."""
    x = coluna_numerica("casual")
    moderados = f.detectar_outliers_iqr(x, fator=1.5)
    extremos = f.detectar_outliers_iqr(x, fator=3.0)
    assert extremos["n_outliers"] <= moderados["n_outliers"]


def test_distribuicao_simetrica_sem_outliers():
    """Dados uniformes bem comportados nao devem acusar outliers."""
    dados = [float(i) for i in range(1, 101)]
    assert f.detectar_outliers_iqr(dados)["n_outliers"] == 0


# ===========================================================================
# INTERPRETACAO TEXTUAL AUTOMATICA
# ===========================================================================


def test_interpretacao_detecta_assimetria_a_direita(coluna_numerica):
    """A coluna 'casual' e claramente assimetrica a direita."""
    texto = f.interpretar_distribuicao(coluna_numerica("casual"), "casual")
    assert "ASSIMÉTRICA À DIREITA" in texto
    assert "MEDIANA" in texto  # deve recomendar a mediana como valor tipico


def test_interpretacao_detecta_simetria():
    """Amostra construida simetrica: media = mediana."""
    dados = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    texto = f.interpretar_distribuicao(dados, "x")
    # "aproximadamente SIMÉTRICA" e nao apenas "SIMÉTRICA", que tambem casaria
    # com "ASSIMÉTRICA" e tornaria o teste inutil
    assert "aproximadamente SIMÉTRICA" in texto


def test_interpretacao_menciona_outliers(coluna_numerica):
    texto = f.interpretar_distribuicao(coluna_numerica("casual"), "casual")
    assert "outliers" in texto.lower()
    assert "IQR" in texto


def test_interpretacao_menciona_curtose_e_cv(coluna_numerica):
    texto = f.interpretar_distribuicao(coluna_numerica("temp"), "temp")
    assert "curtose" in texto.lower()
    assert "coeficiente de variação" in texto.lower()
