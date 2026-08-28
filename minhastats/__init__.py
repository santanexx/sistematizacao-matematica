"""
minhastats -- nucleo estatistico proprio
========================================

Biblioteca de estatistica escrita "na unha" para a Sistematizacao de
Matematica e Estatistica para Computacao.

REGRA DE OURO: nenhum modulo deste pacote importa numpy, scipy, pandas ou
statistics. So a biblioteca padrao (``math``, ``random``). NumPy e SciPy
aparecem exclusivamente em ``tests/``, onde servem de referencia para
validar cada funcao daqui.

Organizacao
-----------
- ``descritiva``   : tendencia central, dispersao, separatrizes, forma
- ``associacao``   : covariancia, correlacao de Pearson, minimos quadrados
- ``frequencias``  : tabelas de frequencia, Sturges, outliers pelo IQR
- ``distribuicoes``: Normal, Uniforme, Exponencial, Binomial, Poisson
- ``simulacao``    : Monte Carlo (Lei dos Grandes Numeros e TCL)
"""

from .descritiva import (
    media,
    mediana,
    moda,
    amplitude,
    minimo,
    maximo,
    variancia_amostral,
    variancia_populacional,
    desvio_padrao_amostral,
    desvio_padrao_populacional,
    coeficiente_variacao,
    erro_padrao_media,
    percentil,
    quartil,
    quartis,
    amplitude_interquartil,
    assimetria_pearson,
    assimetria_momento,
    curtose_momento,
    resumo,
)
from .associacao import (
    covariancia_amostral,
    covariancia_populacional,
    correlacao_pearson,
    interpretar_correlacao,
    regressao_linear,
    prever,
    residuos,
)
from .frequencias import (
    tabela_frequencias_categorica,
    tabela_frequencias_continua,
    regra_sturges,
    detectar_outliers_iqr,
    interpretar_distribuicao,
)
from .distribuicoes import (
    normal_pdf,
    normal_cdf,
    uniforme_pdf,
    exponencial_pdf,
    binomial_pmf,
    poisson_pmf,
    coeficiente_binomial,
    estimar_normal,
    estimar_uniforme,
    estimar_exponencial,
    estimar_binomial,
    estimar_poisson,
    indice_dispersao,
    qualidade_ajuste,
)
from .simulacao import (
    simular_moeda,
    simular_dado,
    simular_tcl,
    convergencia_lgn,
    estimar_pi_monte_carlo,
)

__version__ = "1.0.0"

__all__ = [
    "media", "mediana", "moda", "amplitude", "minimo", "maximo",
    "variancia_amostral", "variancia_populacional",
    "desvio_padrao_amostral", "desvio_padrao_populacional",
    "coeficiente_variacao", "erro_padrao_media",
    "percentil", "quartil", "quartis", "amplitude_interquartil",
    "assimetria_pearson", "assimetria_momento", "curtose_momento", "resumo",
    "covariancia_amostral", "covariancia_populacional", "correlacao_pearson",
    "interpretar_correlacao", "regressao_linear", "prever", "residuos",
    "tabela_frequencias_categorica", "tabela_frequencias_continua",
    "regra_sturges", "detectar_outliers_iqr", "interpretar_distribuicao",
    "normal_pdf", "normal_cdf", "uniforme_pdf", "exponencial_pdf",
    "binomial_pmf", "poisson_pmf", "coeficiente_binomial",
    "estimar_normal", "estimar_uniforme", "estimar_exponencial",
    "estimar_binomial", "estimar_poisson", "indice_dispersao",
    "qualidade_ajuste",
    "simular_moeda", "simular_dado", "simular_tcl", "convergencia_lgn",
    "estimar_pi_monte_carlo",
]
