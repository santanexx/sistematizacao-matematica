"""
minhastats.distribuicoes
========================

Distribuicoes teoricas de probabilidade implementadas a mao (Modulo 4),
com estimacao de parametros pelos dados e uma medida simples de qualidade
do ajuste.

Continuas : Normal, Uniforme, Exponencial  -> f(x) e densidade
Discretas : Binomial, Poisson              -> P(X = k) e probabilidade
"""

import math

from .descritiva import (
    _validar,
    media,
    minimo,
    maximo,
    desvio_padrao_amostral,
    variancia_amostral,
)

SQRT_2PI = math.sqrt(2.0 * math.pi)


# ---------------------------------------------------------------------------
# Normal
# ---------------------------------------------------------------------------


def normal_pdf(x, mu=0.0, sigma=1.0):
    r"""Densidade da Normal :math:`N(\mu, \sigma^2)`.

    .. math::

        f(x) = \frac{1}{\sigma\sqrt{2\pi}}
               \exp\!\left[-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2\right]
    """
    if sigma <= 0:
        raise ValueError("O desvio padrao sigma deve ser positivo.")
    z = (float(x) - mu) / sigma
    return math.exp(-0.5 * z * z) / (sigma * SQRT_2PI)


def normal_cdf(x, mu=0.0, sigma=1.0):
    r"""Funcao de distribuicao acumulada da Normal.

    .. math::

        F(x) = \frac{1}{2}\left[1 + \operatorname{erf}
               \!\left(\frac{x-\mu}{\sigma\sqrt{2}}\right)\right]

    Usamos ``math.erf`` (funcao matematica da biblioteca padrao, nao uma
    funcao estatistica) porque a integral da Normal nao tem primitiva
    elementar.
    """
    if sigma <= 0:
        raise ValueError("O desvio padrao sigma deve ser positivo.")
    return 0.5 * (1.0 + math.erf((float(x) - mu) / (sigma * math.sqrt(2.0))))


def estimar_normal(dados):
    r"""Estima :math:`\mu` e :math:`\sigma` por maxima verossimilhanca/momentos.

    .. math:: \hat{\mu} = \bar{x}, \qquad \hat{\sigma} = s
    """
    x = _validar(dados, minimo=2)
    return {"mu": media(x), "sigma": desvio_padrao_amostral(x)}


# ---------------------------------------------------------------------------
# Uniforme continua
# ---------------------------------------------------------------------------


def uniforme_pdf(x, a=0.0, b=1.0):
    r"""Densidade da Uniforme continua em :math:`[a, b]`.

    .. math::

        f(x) = \begin{cases}
            \frac{1}{b-a} & a \le x \le b \\
            0 & \text{caso contrario}
        \end{cases}
    """
    if b <= a:
        raise ValueError("O limite superior b deve ser maior que a.")
    return 1.0 / (b - a) if a <= float(x) <= b else 0.0


def estimar_uniforme(dados):
    r"""Estima os limites por :math:`\hat{a} = x_{min}`, :math:`\hat{b} = x_{max}`."""
    x = _validar(dados)
    return {"a": minimo(x), "b": maximo(x)}


# ---------------------------------------------------------------------------
# Exponencial
# ---------------------------------------------------------------------------


def exponencial_pdf(x, lam=1.0):
    r"""Densidade da Exponencial de taxa :math:`\lambda`.

    .. math::

        f(x) = \lambda e^{-\lambda x}, \quad x \ge 0
    """
    if lam <= 0:
        raise ValueError("A taxa lambda deve ser positiva.")
    xf = float(x)
    return lam * math.exp(-lam * xf) if xf >= 0 else 0.0


def estimar_exponencial(dados):
    r"""Estima a taxa por maxima verossimilhanca: :math:`\hat{\lambda} = 1/\bar{x}`."""
    x = _validar(dados)
    xbar = media(x)
    if xbar <= 0:
        raise ValueError(
            "A Exponencial exige media positiva; a variavel escolhida nao "
            "atende a esse requisito."
        )
    return {"lam": 1.0 / xbar}


# ---------------------------------------------------------------------------
# Binomial
# ---------------------------------------------------------------------------


def coeficiente_binomial(n, k):
    r"""Numero de combinacoes :math:`\binom{n}{k} = \frac{n!}{k!(n-k)!}`.

    Calculado pelo produto iterativo
    :math:`\prod_{i=1}^{k} \frac{n-k+i}{i}`, que evita construir fatoriais
    gigantes e mantem o resultado exato para os valores usados aqui.
    """
    n, k = int(n), int(k)
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)  # simetria: C(n,k) = C(n,n-k), reduz o numero de passos
    resultado = 1
    for i in range(1, k + 1):
        resultado = resultado * (n - k + i) // i
    return resultado


def binomial_pmf(k, n, p):
    r"""Probabilidade pontual da Binomial :math:`B(n, p)`.

    .. math:: P(X = k) = \binom{n}{k} p^k (1-p)^{n-k}
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError("A probabilidade p deve estar em [0, 1].")
    if n < 0:
        raise ValueError("O numero de ensaios n deve ser >= 0.")
    k = int(k)
    if k < 0 or k > n:
        return 0.0
    return coeficiente_binomial(n, k) * (p ** k) * ((1.0 - p) ** (n - k))


def estimar_binomial(dados, n=None):
    r"""Estima ``p`` pelo metodo dos momentos: :math:`\hat{p} = \bar{x}/n`.

    Se ``n`` nao for informado, usamos o maior valor observado como
    estimativa do numero de ensaios.
    """
    x = _validar(dados)
    if n is None:
        n = int(math.ceil(maximo(x)))
    if n <= 0:
        raise ValueError("Nao foi possivel estimar n para a Binomial.")
    p = media(x) / n
    p = max(0.0, min(1.0, p))
    return {"n": int(n), "p": p}


# ---------------------------------------------------------------------------
# Poisson
# ---------------------------------------------------------------------------


def poisson_pmf(k, lam):
    r"""Probabilidade pontual da Poisson de parametro :math:`\lambda`.

    .. math:: P(X = k) = \frac{e^{-\lambda} \lambda^k}{k!}

    Para :math:`\lambda` grande o calculo direto estoura (``lam ** k``
    excede o float). Por isso trabalhamos em escala LOGARITMICA:

    .. math::

        \ln P = -\lambda + k \ln \lambda - \ln(k!)

    com :math:`\ln(k!) = \ln \Gamma(k+1)` via ``math.lgamma``.
    """
    if lam <= 0:
        raise ValueError("O parametro lambda deve ser positivo.")
    k = int(k)
    if k < 0:
        return 0.0
    log_p = -lam + k * math.log(lam) - math.lgamma(k + 1.0)
    return math.exp(log_p)


def estimar_poisson(dados):
    r"""Estima :math:`\hat{\lambda} = \bar{x}` (media = variancia na Poisson)."""
    x = _validar(dados)
    lam = media(x)
    if lam <= 0:
        raise ValueError("A Poisson exige media positiva.")
    return {"lam": lam}


def indice_dispersao(dados):
    r"""Indice de dispersao :math:`ID = s^2 / \bar{x}`.

    Diagnostico rapido para a Poisson, na qual :math:`\sigma^2 = \mu` e
    portanto :math:`ID \approx 1`. ``ID`` muito acima de 1 indica
    SOBREDISPERSAO -- a Poisson nao serve.
    """
    x = _validar(dados, minimo=2)
    xbar = media(x)
    if xbar == 0:
        raise ValueError("Indice de dispersao indefinido: media zero.")
    return variancia_amostral(x) / xbar


# ---------------------------------------------------------------------------
# Qualidade do ajuste
# ---------------------------------------------------------------------------


def qualidade_ajuste(linhas_frequencia, funcao_densidade, n_total):
    r"""Compara frequencias observadas com as esperadas pelo modelo teorico.

    Para cada classe :math:`[l_i, l_s)` a frequencia esperada e aproximada
    por :math:`E_i \approx n \cdot f(\text{ponto medio}) \cdot h`, onde
    ``h`` e a amplitude da classe. Devolvemos a estatistica

    .. math:: \chi^2 = \sum_i \frac{(O_i - E_i)^2}{E_i}

    e o :math:`\chi^2` por classe, que permite comparar ajustes de
    tabelas com numeros diferentes de classes.

    ATENCAO: usamos este numero apenas como MEDIDA DESCRITIVA comparativa
    entre distribuicoes candidatas, e nao como teste de hipotese formal --
    nao calculamos p-valor nem corrigimos graus de liberdade pelos
    parametros estimados.
    """
    qui_quadrado = 0.0
    detalhes = []
    classes_validas = 0

    for linha in linhas_frequencia:
        h = linha["ls"] - linha["li"]
        esperado = n_total * funcao_densidade(linha["ponto_medio"]) * h
        observado = linha["fi"]

        if esperado > 1e-12:
            contribuicao = (observado - esperado) ** 2 / esperado
            qui_quadrado += contribuicao
            classes_validas += 1
        else:
            contribuicao = float("nan")

        detalhes.append(
            {
                "classe": linha["classe"],
                "observado": observado,
                "esperado": esperado,
                "contribuicao": contribuicao,
            }
        )

    return {
        "qui_quadrado": qui_quadrado,
        "classes": classes_validas,
        "qui_quadrado_por_classe": (
            qui_quadrado / classes_validas if classes_validas else float("nan")
        ),
        "detalhes": detalhes,
    }
