"""
minhastats.descritiva
=====================

Medidas de tendencia central, separatrizes e dispersao implementadas
"na unha", sem usar nenhuma funcao pronta de estatistica.

REGRA DE OURO DO PROJETO: este pacote so importa `math` da biblioteca
padrao. Nada de numpy, scipy ou statistics aqui dentro -- essas
bibliotecas aparecem apenas em tests/, para VALIDAR o que escrevemos.
"""

import math

# ---------------------------------------------------------------------------
# Utilitarios internos
# ---------------------------------------------------------------------------


def _validar(dados, minimo=1):
    """Converte a entrada para uma lista de floats e valida o tamanho.

    Aceita qualquer iteravel (list, tuple, pandas.Series, ...) porque a
    interface entrega os dados vindos de um DataFrame. Valores NaN sao
    descartados: no dataset real uma coluna pode ter buracos, e uma media
    contaminada por NaN se propaga silenciosamente por todo o relatorio.
    """
    limpos = []
    for valor in dados:
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            continue
        if math.isnan(numero):  # NaN != NaN, entao isnan e a unica checagem confiavel
            continue
        limpos.append(numero)

    if len(limpos) < minimo:
        raise ValueError(
            f"Amostra insuficiente: {len(limpos)} valor(es) validos, "
            f"mas o calculo exige pelo menos {minimo}."
        )
    return limpos


def _ordenar(valores):
    """Ordenacao crescente via merge sort (O(n log n)).

    Poderiamos usar sorted(), que nao e uma funcao estatistica e portanto
    seria permitido. Implementamos mesmo assim porque mediana e percentis
    dependem inteiramente da ordenacao -- e o professor pode perguntar.
    """
    if len(valores) <= 1:
        return list(valores)

    meio = len(valores) // 2
    esquerda = _ordenar(valores[:meio])
    direita = _ordenar(valores[meio:])

    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if esquerda[i] <= direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


# ---------------------------------------------------------------------------
# Tendencia central
# ---------------------------------------------------------------------------


def media(dados):
    r"""Media aritmetica.

    .. math:: \bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i
    """
    x = _validar(dados)
    soma = 0.0
    for valor in x:
        soma += valor
    return soma / len(x)


def mediana(dados):
    r"""Mediana: valor que divide a amostra ordenada em duas metades.

    .. math::

        Md = \begin{cases}
            x_{(\frac{n+1}{2})} & \text{se } n \text{ e impar} \\[4pt]
            \frac{x_{(\frac{n}{2})} + x_{(\frac{n}{2}+1)}}{2} & \text{se } n \text{ e par}
        \end{cases}
    """
    x = _ordenar(_validar(dados))
    n = len(x)
    meio = n // 2
    if n % 2 == 1:
        return x[meio]
    return (x[meio - 1] + x[meio]) / 2.0


def moda(dados):
    """Moda(s): o(s) valor(es) de maior frequencia absoluta.

    Retorna sempre uma LISTA ordenada, porque a distribuicao pode ser
    bimodal ou multimodal. Se todos os valores aparecem o mesmo numero de
    vezes, a amostra e amodal e devolvemos lista vazia.
    """
    x = _validar(dados)

    contagem = {}
    for valor in x:
        contagem[valor] = contagem.get(valor, 0) + 1

    frequencia_maxima = 0
    for freq in contagem.values():
        if freq > frequencia_maxima:
            frequencia_maxima = freq

    if frequencia_maxima == 1 and len(contagem) == len(x):
        return []  # amodal: nenhum valor se repete

    modas = [valor for valor, freq in contagem.items() if freq == frequencia_maxima]
    return _ordenar(modas)


# ---------------------------------------------------------------------------
# Dispersao
# ---------------------------------------------------------------------------


def amplitude(dados):
    r"""Amplitude total: :math:`A = x_{max} - x_{min}`."""
    x = _validar(dados)
    menor = maior = x[0]
    for valor in x:
        if valor < menor:
            menor = valor
        if valor > maior:
            maior = valor
    return maior - menor


def minimo(dados):
    """Menor valor da amostra."""
    x = _validar(dados)
    menor = x[0]
    for valor in x:
        if valor < menor:
            menor = valor
    return menor


def maximo(dados):
    """Maior valor da amostra."""
    x = _validar(dados)
    maior = x[0]
    for valor in x:
        if valor > maior:
            maior = valor
    return maior


def variancia_populacional(dados):
    r"""Variancia populacional (divisor :math:`N`).

    .. math:: \sigma^2 = \frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2
    """
    x = _validar(dados)
    mu = media(x)
    soma_quadrados = 0.0
    for valor in x:
        desvio = valor - mu
        soma_quadrados += desvio * desvio
    return soma_quadrados / len(x)


def variancia_amostral(dados):
    r"""Variancia amostral (divisor :math:`n-1`, correcao de Bessel).

    .. math:: s^2 = \frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})^2

    Usamos a formula em dois passos (media primeiro, desvios depois) e nao
    a "formula de maquina" :math:`\sum x^2 - n\bar{x}^2`, que sofre
    cancelamento catastrofico quando a media e grande frente ao desvio.
    """
    x = _validar(dados, minimo=2)
    xbar = media(x)
    soma_quadrados = 0.0
    for valor in x:
        desvio = valor - xbar
        soma_quadrados += desvio * desvio
    return soma_quadrados / (len(x) - 1)


def desvio_padrao_populacional(dados):
    r"""Desvio padrao populacional: :math:`\sigma = \sqrt{\sigma^2}`."""
    return math.sqrt(variancia_populacional(dados))


def desvio_padrao_amostral(dados):
    r"""Desvio padrao amostral: :math:`s = \sqrt{s^2}`."""
    return math.sqrt(variancia_amostral(dados))


def coeficiente_variacao(dados, amostral=True):
    r"""Coeficiente de variacao em PERCENTUAL.

    .. math:: CV = \frac{s}{\bar{x}} \times 100\%

    Medida de dispersao relativa: permite comparar a variabilidade de
    variaveis com unidades diferentes (ex.: umidade em % contra numero de
    alugueis). Nao faz sentido quando a media e zero -- nesse caso
    levantamos erro em vez de devolver infinito silenciosamente.
    """
    x = _validar(dados, minimo=2 if amostral else 1)
    xbar = media(x)
    if xbar == 0:
        raise ValueError(
            "Coeficiente de variacao indefinido: a media da amostra e zero."
        )
    s = desvio_padrao_amostral(x) if amostral else desvio_padrao_populacional(x)
    return (s / abs(xbar)) * 100.0


def erro_padrao_media(dados):
    r"""Erro padrao da media: :math:`EP = s / \sqrt{n}`.

    Usado no Modulo 3 para comparar a dispersao empirica das medias
    amostrais com a previsao teorica do Teorema Central do Limite.
    """
    x = _validar(dados, minimo=2)
    return desvio_padrao_amostral(x) / math.sqrt(len(x))


# ---------------------------------------------------------------------------
# Separatrizes
# ---------------------------------------------------------------------------


def percentil(dados, p):
    r"""Percentil de ordem ``p`` (0 a 100) por interpolacao linear.

    Metodo dos "postos" (o mesmo default de ``numpy.percentile``, chamado
    de interpolacao *linear* / tipo 7):

    .. math::

        h = \frac{p}{100}\,(n - 1), \qquad
        P_p = x_{(\lfloor h \rfloor)} + (h - \lfloor h \rfloor)
              \left( x_{(\lfloor h \rfloor + 1)} - x_{(\lfloor h \rfloor)} \right)

    com a amostra ordenada e indices comecando em zero. Escolhemos este
    metodo justamente para poder validar contra o NumPy sem ressalvas.
    """
    if not 0 <= p <= 100:
        raise ValueError(f"Percentil deve estar entre 0 e 100 (recebido: {p}).")

    x = _ordenar(_validar(dados))
    n = len(x)
    if n == 1:
        return x[0]

    posicao = (p / 100.0) * (n - 1)
    inferior = int(math.floor(posicao))
    fracao = posicao - inferior

    if inferior >= n - 1:
        return x[n - 1]
    return x[inferior] + fracao * (x[inferior + 1] - x[inferior])


def quartil(dados, k):
    """Quartil k (1, 2 ou 3). Q1 = P25, Q2 = P50 = mediana, Q3 = P75."""
    if k not in (1, 2, 3):
        raise ValueError(f"Quartil deve ser 1, 2 ou 3 (recebido: {k}).")
    return percentil(dados, 25.0 * k)


def quartis(dados):
    """Tupla (Q1, Q2, Q3) -- atalho usado pelo boxplot e pela regra do IQR."""
    x = _validar(dados)
    return (percentil(x, 25), percentil(x, 50), percentil(x, 75))


def amplitude_interquartil(dados):
    r"""Amplitude interquartil: :math:`IQR = Q_3 - Q_1`.

    Mede a dispersao dos 50% centrais e, por ignorar as caudas, e robusta
    a valores extremos -- por isso e a base da deteccao de outliers.
    """
    q1, _, q3 = quartis(dados)
    return q3 - q1


# ---------------------------------------------------------------------------
# Forma da distribuicao
# ---------------------------------------------------------------------------


def assimetria_pearson(dados):
    r"""Coeficiente de assimetria de Pearson (segundo coeficiente).

    .. math:: A_s = \frac{3(\bar{x} - Md)}{s}

    Interpretacao: :math:`A_s > 0` cauda a direita, :math:`A_s < 0` cauda
    a esquerda, :math:`A_s \approx 0` simetrica.
    """
    x = _validar(dados, minimo=2)
    s = desvio_padrao_amostral(x)
    if s == 0:
        return 0.0  # todos os valores iguais: distribuicao degenerada, mas simetrica
    return 3.0 * (media(x) - mediana(x)) / s


def assimetria_momento(dados):
    r"""Assimetria pelo terceiro momento padronizado (skewness populacional).

    .. math:: g_1 = \frac{\frac{1}{n}\sum (x_i - \bar{x})^3}{\sigma^3}

    E esta a definicao usada por ``scipy.stats.skew(bias=True)``, que e a
    referencia contra a qual validamos nos testes.
    """
    x = _validar(dados, minimo=2)
    xbar = media(x)
    n = len(x)

    soma_cubos = 0.0
    soma_quadrados = 0.0
    for valor in x:
        desvio = valor - xbar
        soma_quadrados += desvio * desvio
        soma_cubos += desvio * desvio * desvio

    sigma = math.sqrt(soma_quadrados / n)
    if sigma == 0:
        return 0.0
    return (soma_cubos / n) / (sigma ** 3)


def curtose_momento(dados):
    r"""Curtose (excesso) pelo quarto momento padronizado.

    .. math:: g_2 = \frac{\frac{1}{n}\sum (x_i - \bar{x})^4}{\sigma^4} - 3

    O ``-3`` torna a Normal a referencia zero, igual a
    ``scipy.stats.kurtosis(fisher=True, bias=True)``.
    """
    x = _validar(dados, minimo=2)
    xbar = media(x)
    n = len(x)

    soma_quartas = 0.0
    soma_quadrados = 0.0
    for valor in x:
        desvio = valor - xbar
        quadrado = desvio * desvio
        soma_quadrados += quadrado
        soma_quartas += quadrado * quadrado

    variancia = soma_quadrados / n
    if variancia == 0:
        return 0.0
    return (soma_quartas / n) / (variancia * variancia) - 3.0


# ---------------------------------------------------------------------------
# Resumo consolidado (consumido pela interface)
# ---------------------------------------------------------------------------


def resumo(dados):
    """Devolve um dicionario com todas as medidas de uma vez.

    A interface do Modulo 2 chama apenas esta funcao -- assim fica
    explicito que NENHUM numero exibido ao usuario vem do numpy/pandas.
    """
    x = _validar(dados, minimo=2)
    q1, q2, q3 = quartis(x)
    return {
        "n": len(x),
        "media": media(x),
        "mediana": mediana(x),
        "moda": moda(x),
        "minimo": minimo(x),
        "maximo": maximo(x),
        "amplitude": amplitude(x),
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "iqr": q3 - q1,
        "variancia_amostral": variancia_amostral(x),
        "variancia_populacional": variancia_populacional(x),
        "desvio_padrao_amostral": desvio_padrao_amostral(x),
        "desvio_padrao_populacional": desvio_padrao_populacional(x),
        "coeficiente_variacao": coeficiente_variacao(x),
        "erro_padrao": erro_padrao_media(x),
        "assimetria_pearson": assimetria_pearson(x),
        "assimetria_momento": assimetria_momento(x),
        "curtose": curtose_momento(x),
    }
