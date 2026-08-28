"""
minhastats.frequencias
======================

Tabelas de frequencia (variaveis categoricas e continuas), regra de
Sturges, deteccao de outliers pelo IQR e interpretacao textual
automatica -- o motor do Modulo 2.
"""

import math

from .descritiva import (
    _validar,
    _ordenar,
    media,
    mediana,
    moda,
    minimo,
    maximo,
    quartis,
    assimetria_pearson,
    curtose_momento,
    coeficiente_variacao,
    desvio_padrao_amostral,
)


# ---------------------------------------------------------------------------
# Variaveis categoricas / discretas
# ---------------------------------------------------------------------------


def tabela_frequencias_categorica(dados, ordenar_por="frequencia"):
    """Tabela de frequencias para variavel qualitativa ou discreta.

    Cada linha traz: categoria, frequencia absoluta (fi), relativa (fr),
    percentual (%), e as respectivas acumuladas (Fi, Fr%).

    ``ordenar_por`` aceita ``"frequencia"`` (decrescente, bom para grafico
    de barras) ou ``"categoria"`` (ordem natural do rotulo).
    """
    valores = [v for v in dados if v is not None and not _e_nan(v)]
    if not valores:
        raise ValueError("Nenhum valor valido para montar a tabela de frequencias.")

    contagem = {}
    for valor in valores:
        chave = str(valor)
        contagem[chave] = contagem.get(chave, 0) + 1

    itens = list(contagem.items())
    if ordenar_por == "frequencia":
        # decrescente por frequencia; empate resolvido pelo rotulo (estavel e reproduzivel)
        itens.sort(key=lambda par: (-par[1], par[0]))
    else:
        itens.sort(key=lambda par: par[0])

    n = len(valores)
    linhas = []
    acumulada = 0
    for categoria, fi in itens:
        acumulada += fi
        linhas.append(
            {
                "categoria": categoria,
                "fi": fi,
                "fr": fi / n,
                "percentual": 100.0 * fi / n,
                "Fi": acumulada,
                "Fr_percentual": 100.0 * acumulada / n,
            }
        )
    return linhas


def _e_nan(valor):
    """True se o valor for NaN (float ou numpy.float vindos do pandas)."""
    try:
        return math.isnan(float(valor))
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Variaveis continuas: classes
# ---------------------------------------------------------------------------


def regra_sturges(n):
    r"""Numero de classes pela regra de Sturges.

    .. math:: k = \lceil 1 + 3{,}322 \log_{10}(n) \rceil
              = \lceil 1 + \log_2(n) \rceil

    Limitamos k a no minimo 1. Para n muito grande (o nosso dataset tem
    17.379 registros) Sturges devolve k = 15, um numero razoavel de barras
    para o histograma.
    """
    if n < 1:
        raise ValueError("n deve ser positivo.")
    if n == 1:
        return 1
    return max(1, int(math.ceil(1 + math.log2(n))))


def tabela_frequencias_continua(dados, k=None):
    """Tabela de frequencias em classes para variavel continua.

    Se ``k`` nao for informado, usa a regra de Sturges. As classes sao de
    igual amplitude :math:`h = A / k`, com intervalos fechados a esquerda
    e abertos a direita ``[li, ls)``; a ULTIMA classe e fechada nos dois
    lados para que o valor maximo nao fique de fora.

    Cada linha traz limites, ponto medio, fi, fr, % e acumuladas.
    """
    x = _ordenar(_validar(dados))
    n = len(x)

    if k is None:
        k = regra_sturges(n)
    k = int(k)
    if k < 1:
        raise ValueError("O numero de classes deve ser >= 1.")

    li_global = minimo(x)
    ls_global = maximo(x)
    amplitude_total = ls_global - li_global

    if amplitude_total == 0:
        # Variavel constante: uma unica classe degenerada
        return [
            {
                "classe": f"[{li_global:.4g}; {ls_global:.4g}]",
                "li": li_global,
                "ls": ls_global,
                "ponto_medio": li_global,
                "fi": n,
                "fr": 1.0,
                "percentual": 100.0,
                "Fi": n,
                "Fr_percentual": 100.0,
            }
        ]

    h = amplitude_total / k

    # Bordas explicitas das classes. Calculamos li + i*h (e nao acumulamos
    # h somando repetidamente, o que propagaria o erro) e fixamos a ultima
    # borda no maximo exato -- mesma construcao do numpy.linspace.
    bordas = [li_global + i * h for i in range(k + 1)]
    bordas[k] = ls_global

    contagens = [0] * k
    for valor in x:
        # Chute inicial pela posicao relativa dentro da amplitude...
        indice = int((valor - li_global) / h)
        if indice < 0:
            indice = 0
        elif indice >= k:    # acontece exatamente com o valor maximo
            indice = k - 1

        # ...e correcao comparando com as BORDAS REAIS.
        #
        # Por que isso e necessario: em ponto flutuante, (valor - li)/h pode
        # cair do lado errado da fronteira. Exemplo real do nosso dataset,
        # na coluna 'hum' com k = 20: h = 0,05 e a borda da classe 17 vale
        # 0,8500000000000001 (nao 0,85, pois 0,05 nao tem representacao
        # binaria exata). O valor 0,85 e MENOR que essa borda, logo pertence
        # a classe 16 -- mas int(0,85 / 0,05) devolve 17. Sem esta correcao
        # cinco registros iam para a classe errada e a tabela divergia do
        # numpy.histogram. E exatamente a mesma correcao que o NumPy aplica
        # internamente em np.histogram.
        if indice > 0 and valor < bordas[indice]:
            indice -= 1
        elif indice < k - 1 and valor >= bordas[indice + 1]:
            indice += 1

        contagens[indice] += 1

    linhas = []
    acumulada = 0
    for i in range(k):
        li = bordas[i]
        ls = bordas[i + 1]
        acumulada += contagens[i]
        fecho = "]" if i == k - 1 else ")"
        linhas.append(
            {
                "classe": f"[{li:.4g}; {ls:.4g}{fecho}",
                "li": li,
                "ls": ls,
                "ponto_medio": (li + ls) / 2.0,
                "fi": contagens[i],
                "fr": contagens[i] / n,
                "percentual": 100.0 * contagens[i] / n,
                "Fi": acumulada,
                "Fr_percentual": 100.0 * acumulada / n,
            }
        )
    return linhas


# ---------------------------------------------------------------------------
# Outliers pela regra do IQR
# ---------------------------------------------------------------------------


def detectar_outliers_iqr(dados, fator=1.5):
    r"""Deteccao de outliers pela regra do boxplot de Tukey.

    .. math::

        LI = Q_1 - f \cdot IQR, \qquad LS = Q_3 + f \cdot IQR

    com :math:`f = 1{,}5` para outliers moderados e :math:`f = 3{,}0` para
    outliers extremos. Valores fora de :math:`[LI, LS]` sao sinalizados.

    Retorna um dicionario com os limites, a lista de outliers, quantos
    ficaram abaixo/acima e o percentual do total.
    """
    x = _validar(dados, minimo=2)
    q1, _, q3 = quartis(x)
    iqr = q3 - q1

    limite_inferior = q1 - fator * iqr
    limite_superior = q3 + fator * iqr

    abaixo = [v for v in x if v < limite_inferior]
    acima = [v for v in x if v > limite_superior]
    outliers = _ordenar(abaixo + acima)

    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "fator": fator,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "outliers": outliers,
        "n_outliers": len(outliers),
        "n_abaixo": len(abaixo),
        "n_acima": len(acima),
        "percentual": 100.0 * len(outliers) / len(x),
    }


# ---------------------------------------------------------------------------
# Interpretacao textual automatica (Modulo 2)
# ---------------------------------------------------------------------------


def interpretar_distribuicao(dados, nome_variavel="a variavel"):
    """Gera um paragrafo de leitura automatica da distribuicao.

    Combina quatro leituras: posicao relativa de media/mediana/moda
    (assimetria), grau de dispersao relativa (CV), achatamento (curtose) e
    presenca de outliers. E o texto que o Modulo 2 exibe abaixo dos
    graficos.
    """
    x = _validar(dados, minimo=2)
    xbar = media(x)
    md = mediana(x)
    modas = moda(x)
    assimetria = assimetria_pearson(x)
    curtose = curtose_momento(x)
    info_outliers = detectar_outliers_iqr(x)

    partes = []

    # --- 1. Assimetria -----------------------------------------------------
    if abs(assimetria) < 0.15:
        partes.append(
            f"A distribuição de {nome_variavel} é aproximadamente SIMÉTRICA "
            f"(coeficiente de assimetria de Pearson = {assimetria:.3f}): "
            f"média ({xbar:.3f}) e mediana ({md:.3f}) praticamente coincidem."
        )
    elif assimetria > 0:
        partes.append(
            f"A distribuição de {nome_variavel} é ASSIMÉTRICA À DIREITA "
            f"(assimetria de Pearson = {assimetria:.3f}): a média ({xbar:.3f}) "
            f"é maior que a mediana ({md:.3f}), sinal de uma cauda longa de "
            f"valores altos que puxa a média para cima. Nesse caso a MEDIANA "
            f"descreve melhor o valor típico do que a média."
        )
    else:
        partes.append(
            f"A distribuição de {nome_variavel} é ASSIMÉTRICA À ESQUERDA "
            f"(assimetria de Pearson = {assimetria:.3f}): a média ({xbar:.3f}) "
            f"é menor que a mediana ({md:.3f}), indicando uma cauda de valores "
            f"baixos."
        )

    if modas:
        rotulo = ", ".join(f"{m:.4g}" for m in modas[:3])
        if len(modas) == 1:
            partes.append(f"O valor mais frequente (moda) é {rotulo}.")
        else:
            partes.append(
                f"A distribuição é MULTIMODAL, com {len(modas)} valores de "
                f"frequência máxima (os primeiros: {rotulo})."
            )

    # --- 2. Dispersao relativa --------------------------------------------
    try:
        cv = coeficiente_variacao(x)
        if cv < 15:
            leitura = "BAIXA dispersão relativa: os dados são homogêneos"
        elif cv < 30:
            leitura = "dispersão relativa MODERADA"
        else:
            leitura = "ALTA dispersão relativa: os dados são heterogêneos"
        partes.append(
            f"O coeficiente de variação é {cv:.2f}%, o que indica {leitura} "
            f"(desvio padrão amostral = {desvio_padrao_amostral(x):.4g})."
        )
    except ValueError:
        partes.append(
            "O coeficiente de variação não pôde ser calculado porque a média "
            "da amostra é zero."
        )

    # --- 3. Curtose --------------------------------------------------------
    if curtose > 0.5:
        partes.append(
            f"O excesso de curtose é {curtose:.3f} (> 0): a curva é "
            f"LEPTOCÚRTICA, mais afilada no centro e com caudas mais pesadas "
            f"que a Normal."
        )
    elif curtose < -0.5:
        partes.append(
            f"O excesso de curtose é {curtose:.3f} (< 0): a curva é "
            f"PLATICÚRTICA, mais achatada que a Normal."
        )
    else:
        partes.append(
            f"O excesso de curtose é {curtose:.3f}, próximo de zero: o "
            f"achatamento é comparável ao da distribuição Normal "
            f"(MESOCÚRTICA)."
        )

    # --- 4. Outliers -------------------------------------------------------
    if info_outliers["n_outliers"] == 0:
        partes.append(
            f"Pela regra do IQR (limites {info_outliers['limite_inferior']:.4g} "
            f"e {info_outliers['limite_superior']:.4g}), NENHUM outlier foi "
            f"detectado."
        )
    else:
        partes.append(
            f"Pela regra do IQR foram detectados {info_outliers['n_outliers']} "
            f"outliers ({info_outliers['percentual']:.2f}% da amostra): "
            f"{info_outliers['n_abaixo']} abaixo de "
            f"{info_outliers['limite_inferior']:.4g} e "
            f"{info_outliers['n_acima']} acima de "
            f"{info_outliers['limite_superior']:.4g}."
        )

    return " ".join(partes)
