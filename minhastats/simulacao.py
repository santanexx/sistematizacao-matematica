"""
minhastats.simulacao
====================

Experimentos de Monte Carlo do Modulo 3:

(a) Lei dos Grandes Numeros -- a frequencia relativa converge para a
    probabilidade teorica conforme o numero de repeticoes cresce;
(b) Teorema Central do Limite -- a distribuicao das medias amostrais
    tende a Normal conforme o tamanho da amostra cresce, mesmo partindo
    de uma populacao fortemente assimetrica.

Usamos ``random`` da biblioteca padrao apenas como GERADOR DE NUMEROS
ALEATORIOS (nao e uma funcao estatistica); toda medida calculada sobre os
resultados vem do nosso proprio ``minhastats``. Todas as funcoes aceitam
``semente`` para que os resultados sejam reproduzíveis.
"""

import math
import random

from .descritiva import media, desvio_padrao_amostral, variancia_amostral


# ---------------------------------------------------------------------------
# (a) Lei dos Grandes Numeros
# ---------------------------------------------------------------------------


def simular_moeda(n_lancamentos, p_cara=0.5, semente=None):
    r"""Lanca uma moeda ``n`` vezes e acompanha a frequencia relativa de caras.

    A Lei dos Grandes Numeros garante que

    .. math::

        \hat{p}_n = \frac{1}{n}\sum_{i=1}^{n} X_i
        \;\xrightarrow[n \to \infty]{}\; p

    onde :math:`X_i \sim \text{Bernoulli}(p)`.

    Retorna as frequencias relativas ACUMULADAS passo a passo, que e o que
    o grafico de convergencia precisa plotar.
    """
    if n_lancamentos < 1:
        raise ValueError("O numero de lancamentos deve ser >= 1.")
    if not 0.0 <= p_cara <= 1.0:
        raise ValueError("p_cara deve estar em [0, 1].")

    rng = random.Random(semente)

    caras = 0
    frequencias = []
    for i in range(1, n_lancamentos + 1):
        if rng.random() < p_cara:
            caras += 1
        frequencias.append(caras / i)

    return {
        "frequencias_acumuladas": frequencias,
        "frequencia_final": frequencias[-1],
        "valor_teorico": p_cara,
        "erro_final": abs(frequencias[-1] - p_cara),
        "n": n_lancamentos,
        "sucessos": caras,
    }


def simular_dado(n_lancamentos, faces=6, semente=None):
    r"""Lanca um dado honesto ``n`` vezes e acompanha a media acumulada.

    Para um dado honesto de ``f`` faces o valor esperado e

    .. math:: E[X] = \frac{f + 1}{2}

    e a LGN diz que a media amostral converge para ele. Devolvemos tambem
    a frequencia relativa acumulada de cada face -- todas devem convergir
    para :math:`1/f`.
    """
    if n_lancamentos < 1:
        raise ValueError("O numero de lancamentos deve ser >= 1.")
    if faces < 2:
        raise ValueError("O dado deve ter ao menos 2 faces.")

    rng = random.Random(semente)

    contagem = [0] * faces
    soma = 0
    medias = []
    resultados = []
    for i in range(1, n_lancamentos + 1):
        valor = rng.randint(1, faces)
        resultados.append(valor)
        contagem[valor - 1] += 1
        soma += valor
        medias.append(soma / i)

    esperanca = (faces + 1) / 2.0
    return {
        "resultados": resultados,
        "medias_acumuladas": medias,
        "media_final": medias[-1],
        "esperanca_teorica": esperanca,
        "erro_final": abs(medias[-1] - esperanca),
        "frequencias_relativas": [c / n_lancamentos for c in contagem],
        "frequencia_teorica": 1.0 / faces,
        "contagem_faces": contagem,
        "n": n_lancamentos,
    }


def convergencia_lgn(frequencias, valor_teorico, marcos=(10, 100, 1000, 10000)):
    """Tabela do erro |estimativa - teorico| em marcos de n.

    Deixa numerico o que o grafico mostra visualmente: o erro cai na ordem
    de :math:`1/\\sqrt{n}`, e nao linearmente.
    """
    linhas = []
    for n in marcos:
        if n <= len(frequencias):
            estimativa = frequencias[n - 1]
            linhas.append(
                {
                    "n": n,
                    "estimativa": estimativa,
                    "teorico": valor_teorico,
                    "erro_absoluto": abs(estimativa - valor_teorico),
                    "erro_esperado_1_sobre_raiz_n": 1.0 / math.sqrt(n),
                }
            )
    return linhas


# ---------------------------------------------------------------------------
# (b) Teorema Central do Limite
# ---------------------------------------------------------------------------


def simular_tcl(populacao, tamanho_amostra, n_repeticoes, semente=None, com_reposicao=True):
    r"""Sorteia amostras repetidas e devolve a distribuicao das medias.

    O TCL afirma que, para :math:`X_i` i.i.d. com media :math:`\mu` e
    variancia :math:`\sigma^2` finitas,

    .. math::

        \bar{X}_n \;\xrightarrow{d}\;
        N\!\left(\mu, \frac{\sigma^2}{n}\right)
        \quad \text{quando } n \to \infty

    independentemente da forma da distribuicao original. E exatamente isso
    que a aplicacao demonstra: partimos de uma variavel assimetrica do
    dataset e mostramos o histograma das medias virando um sino.

    Retorna as medias amostrais, os parametros teoricos previstos pelo TCL
    e os parametros efetivamente observados na simulacao.
    """
    x = [float(v) for v in populacao if not _e_nan(v)]
    if len(x) < 2:
        raise ValueError("A populacao precisa de ao menos 2 valores validos.")
    if tamanho_amostra < 1:
        raise ValueError("O tamanho da amostra deve ser >= 1.")
    if n_repeticoes < 1:
        raise ValueError("O numero de repeticoes deve ser >= 1.")
    if not com_reposicao and tamanho_amostra > len(x):
        raise ValueError(
            "Sem reposicao, o tamanho da amostra nao pode exceder a populacao."
        )

    rng = random.Random(semente)

    medias_amostrais = []
    for _ in range(n_repeticoes):
        if com_reposicao:
            amostra = [x[rng.randrange(len(x))] for _ in range(tamanho_amostra)]
        else:
            amostra = rng.sample(x, tamanho_amostra)
        medias_amostrais.append(media(amostra))

    # Parametros da populacao (calculados pelo nosso proprio nucleo)
    mu = media(x)
    sigma = desvio_padrao_amostral(x)

    # Previsao do TCL contra o que a simulacao de fato produziu
    erro_padrao_teorico = sigma / math.sqrt(tamanho_amostra)
    media_observada = media(medias_amostrais)
    desvio_observado = (
        desvio_padrao_amostral(medias_amostrais) if n_repeticoes > 1 else float("nan")
    )

    return {
        "medias_amostrais": medias_amostrais,
        "mu_populacao": mu,
        "sigma_populacao": sigma,
        "media_das_medias": media_observada,
        "erro_padrao_teorico": erro_padrao_teorico,
        "erro_padrao_observado": desvio_observado,
        "variancia_das_medias": (
            variancia_amostral(medias_amostrais) if n_repeticoes > 1 else float("nan")
        ),
        "tamanho_amostra": tamanho_amostra,
        "n_repeticoes": n_repeticoes,
    }


def _e_nan(valor):
    """True se o valor nao for um numero utilizavel."""
    try:
        return math.isnan(float(valor))
    except (TypeError, ValueError):
        return True


def estimar_pi_monte_carlo(n_pontos, semente=None):
    r"""Bonus classico de Monte Carlo: estimativa de :math:`\pi`.

    Sorteando pontos uniformes no quadrado :math:`[0,1]^2`, a proporcao
    que cai dentro do quarto de circulo de raio 1 estima :math:`\pi/4`:

    .. math:: \hat{\pi} = 4 \cdot \frac{\text{pontos dentro}}{n}

    Serve como segunda ilustracao da LGN, agora com um valor teorico que
    todo mundo reconhece.
    """
    if n_pontos < 1:
        raise ValueError("O numero de pontos deve ser >= 1.")

    rng = random.Random(semente)

    dentro = 0
    estimativas = []
    pontos_x, pontos_y, dentro_flags = [], [], []
    for i in range(1, n_pontos + 1):
        px = rng.random()
        py = rng.random()
        esta_dentro = (px * px + py * py) <= 1.0
        if esta_dentro:
            dentro += 1
        estimativas.append(4.0 * dentro / i)
        # guardamos os pontos so quando cabem no grafico de dispersao
        if i <= 3000:
            pontos_x.append(px)
            pontos_y.append(py)
            dentro_flags.append(esta_dentro)

    return {
        "estimativas_acumuladas": estimativas,
        "pi_estimado": estimativas[-1],
        "pi_teorico": math.pi,
        "erro": abs(estimativas[-1] - math.pi),
        "pontos_x": pontos_x,
        "pontos_y": pontos_y,
        "dentro": dentro_flags,
        "n": n_pontos,
    }
