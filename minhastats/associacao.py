"""
minhastats.associacao
=====================

Covariancia, correlacao de Pearson e regressao linear simples pelo metodo
dos minimos quadrados -- tudo implementado a mao (Modulos 1 e 5).
"""

import math

from .descritiva import _validar, media, desvio_padrao_amostral


def _validar_pares(x, y):
    """Valida duas amostras emparelhadas.

    Percorre os dois vetores em paralelo e descarta o PAR inteiro quando
    qualquer um dos lados e invalido -- descartar so um lado quebraria o
    emparelhamento e produziria uma correlacao sem sentido.
    """
    if len(x) != len(y):
        raise ValueError(
            f"As amostras devem ter o mesmo tamanho: {len(x)} != {len(y)}."
        )

    xs, ys = [], []
    for a, b in zip(x, y):
        try:
            va, vb = float(a), float(b)
        except (TypeError, ValueError):
            continue
        if math.isnan(va) or math.isnan(vb):
            continue
        xs.append(va)
        ys.append(vb)

    if len(xs) < 2:
        raise ValueError(
            f"Sao necessarios ao menos 2 pares validos (encontrados: {len(xs)})."
        )
    return xs, ys


# ---------------------------------------------------------------------------
# Covariancia e correlacao
# ---------------------------------------------------------------------------


def covariancia_amostral(x, y):
    r"""Covariancia amostral (divisor :math:`n-1`).

    .. math::

        s_{xy} = \frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})(y_i - \bar{y})
    """
    xs, ys = _validar_pares(x, y)
    xbar, ybar = media(xs), media(ys)

    soma_produtos = 0.0
    for a, b in zip(xs, ys):
        soma_produtos += (a - xbar) * (b - ybar)
    return soma_produtos / (len(xs) - 1)


def covariancia_populacional(x, y):
    r"""Covariancia populacional (divisor :math:`N`).

    .. math::

        \sigma_{xy} = \frac{1}{N} \sum_{i=1}^{N} (x_i - \mu_x)(y_i - \mu_y)
    """
    xs, ys = _validar_pares(x, y)
    xbar, ybar = media(xs), media(ys)

    soma_produtos = 0.0
    for a, b in zip(xs, ys):
        soma_produtos += (a - xbar) * (b - ybar)
    return soma_produtos / len(xs)


def correlacao_pearson(x, y):
    r"""Coeficiente de correlacao linear de Pearson.

    .. math::

        r = \frac{s_{xy}}{s_x \, s_y}
          = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}
                 {\sqrt{\sum (x_i - \bar{x})^2} \sqrt{\sum (y_i - \bar{y})^2}}

    Note que o divisor :math:`n-1` de :math:`s_{xy}`, :math:`s_x` e
    :math:`s_y` se cancela -- por isso ``r`` e o mesmo usando a versao
    amostral ou a populacional.

    Retorna um valor em [-1, 1]. Fazemos o *clamp* explicito no final
    porque erro de arredondamento pode produzir 1.0000000000000002 e
    quebrar quem consumir o valor (ex.: ``math.acos``).
    """
    xs, ys = _validar_pares(x, y)
    xbar, ybar = media(xs), media(ys)

    soma_produtos = 0.0
    soma_qx = 0.0
    soma_qy = 0.0
    for a, b in zip(xs, ys):
        dx = a - xbar
        dy = b - ybar
        soma_produtos += dx * dy
        soma_qx += dx * dx
        soma_qy += dy * dy

    denominador = math.sqrt(soma_qx) * math.sqrt(soma_qy)
    if denominador == 0:
        raise ValueError(
            "Correlacao indefinida: ao menos uma das variaveis e constante "
            "(desvio padrao zero)."
        )

    r = soma_produtos / denominador
    return max(-1.0, min(1.0, r))


def interpretar_correlacao(r):
    """Traduz o valor de r para linguagem natural (Modulo 5).

    Classificacao por faixas de |r|, seguindo a escala usual de Cohen /
    Callegari-Jacques adotada em textos de estatistica aplicada.
    """
    forca_abs = abs(r)
    if forca_abs < 0.10:
        forca = "praticamente nula"
    elif forca_abs < 0.30:
        forca = "fraca"
    elif forca_abs < 0.50:
        forca = "moderada"
    elif forca_abs < 0.70:
        forca = "substancial"
    elif forca_abs < 0.90:
        forca = "forte"
    else:
        forca = "muito forte"

    if r > 0:
        sentido = "positiva (crescem juntas)"
    elif r < 0:
        sentido = "negativa (quando uma sobe, a outra tende a cair)"
    else:
        sentido = "nula"

    return f"correlação linear {forca} e {sentido}"


# ---------------------------------------------------------------------------
# Regressao linear simples (minimos quadrados)
# ---------------------------------------------------------------------------


def regressao_linear(x, y):
    r"""Ajusta :math:`\hat{y} = a + bx` pelo metodo dos minimos quadrados.

    Minimizamos a soma dos quadrados dos residuos
    :math:`SQ_{res} = \sum (y_i - a - b x_i)^2`. Derivando em relacao a
    ``a`` e ``b`` e igualando a zero chega-se as equacoes normais, cuja
    solucao e:

    .. math::

        b = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2},
        \qquad
        a = \bar{y} - b\,\bar{x}

    O coeficiente de determinacao vem da decomposicao da variacao total:

    .. math::

        SQ_{tot} = SQ_{reg} + SQ_{res}, \qquad
        R^2 = 1 - \frac{SQ_{res}}{SQ_{tot}}

    Na regressao linear SIMPLES vale ainda :math:`R^2 = r^2`, e os testes
    verificam essa identidade.

    Retorna um dicionario com os coeficientes, R^2, o erro padrao da
    estimativa e a equacao ja formatada para exibicao.
    """
    xs, ys = _validar_pares(x, y)
    n = len(xs)
    xbar, ybar = media(xs), media(ys)

    soma_produtos = 0.0   # Sxy
    soma_qx = 0.0         # Sxx
    for a, b in zip(xs, ys):
        dx = a - xbar
        soma_produtos += dx * (b - ybar)
        soma_qx += dx * dx

    if soma_qx == 0:
        raise ValueError(
            "Regressao impossivel: a variavel X e constante, nao ha reta "
            "definida (divisao por zero no coeficiente angular)."
        )

    b_angular = soma_produtos / soma_qx
    a_linear = ybar - b_angular * xbar

    # Decomposicao da variacao
    sq_residuos = 0.0
    sq_total = 0.0
    for xi, yi in zip(xs, ys):
        previsto = a_linear + b_angular * xi
        residuo = yi - previsto
        sq_residuos += residuo * residuo
        desvio = yi - ybar
        sq_total += desvio * desvio

    r2 = 1.0 - (sq_residuos / sq_total) if sq_total != 0 else 0.0

    # Erro padrao da estimativa: desvio tipico dos residuos em torno da reta.
    # Perde-se 2 graus de liberdade porque estimamos "a" e "b".
    erro_padrao_estimativa = math.sqrt(sq_residuos / (n - 2)) if n > 2 else float("nan")

    sinal = "+" if a_linear >= 0 else "-"
    equacao = f"y = {b_angular:.6g}x {sinal} {abs(a_linear):.6g}"

    return {
        "a": a_linear,                 # intercepto
        "b": b_angular,                # coeficiente angular (inclinacao)
        "r2": r2,
        "sq_residuos": sq_residuos,
        "sq_total": sq_total,
        "sq_regressao": sq_total - sq_residuos,
        "erro_padrao_estimativa": erro_padrao_estimativa,
        "n": n,
        "equacao": equacao,
    }


def prever(modelo, x_novo):
    r"""Aplica a reta ajustada: :math:`\hat{y} = a + b x`.

    ``modelo`` e o dicionario devolvido por :func:`regressao_linear`.
    Alimenta o campo de predicao interativa do Modulo 5.
    """
    return modelo["a"] + modelo["b"] * float(x_novo)


def residuos(modelo, x, y):
    """Lista dos residuos :math:`e_i = y_i - \\hat{y}_i`.

    Usada no grafico de residuos: se o modelo linear e adequado, os pontos
    devem se espalhar sem padrao em torno de zero.
    """
    xs, ys = _validar_pares(x, y)
    return [yi - prever(modelo, xi) for xi, yi in zip(xs, ys)]
