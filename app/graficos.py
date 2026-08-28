"""
app.graficos
============

Funcoes de desenho com Matplotlib.

Ponto importante para o criterio da "regra de ouro": NAO usamos
``ax.hist`` nem ``ax.boxplot`` com os dados crus, porque essas funcoes
calculariam elas mesmas as classes e os quartis. Em vez disso:

- o histograma e desenhado com ``ax.bar``, a partir da tabela de classes
  produzida por ``minhastats.frequencias``;
- o boxplot e desenhado com ``ax.bxp``, alimentado com os quartis, os
  limites e os outliers ja calculados por ``minhastats``.

Ou seja: o Matplotlib so pinta; quem calcula e o nosso nucleo.
"""

import matplotlib

matplotlib.use("Agg")  # backend sem interface grafica, exigido pelo Streamlit

import matplotlib.pyplot as plt

# Paleta unica do projeto, para os graficos parecerem um sistema so
COR_PRIMARIA = "#2E6F9E"
COR_SECUNDARIA = "#E07A3F"
COR_DESTAQUE = "#C0392B"
COR_APOIO = "#7F8C8D"
COR_TERCIARIA = "#5B9279"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    }
)


def nova_figura(largura=8, altura=4.2):
    """Cria figura e eixo com o tamanho padrao do projeto."""
    fig, ax = plt.subplots(figsize=(largura, altura))
    return fig, ax


def histograma(linhas_classes, titulo, rotulo_x, curva=None, rotulo_curva=None):
    """Histograma desenhado a partir da NOSSA tabela de classes.

    ``linhas_classes`` e a saida de
    ``minhastats.frequencias.tabela_frequencias_continua``.

    ``curva`` (opcional) e uma tupla ``(xs, ys)`` ja em escala de
    frequencia, usada no Modulo 4 para sobrepor a distribuicao teorica.
    """
    fig, ax = nova_figura()

    centros = [linha["ponto_medio"] for linha in linhas_classes]
    alturas = [linha["fi"] for linha in linhas_classes]
    larguras = [(linha["ls"] - linha["li"]) * 0.97 for linha in linhas_classes]

    ax.bar(centros, alturas, width=larguras, color=COR_PRIMARIA,
           edgecolor="white", linewidth=0.6, label="Frequência observada")

    if curva is not None:
        xs, ys = curva
        ax.plot(xs, ys, color=COR_DESTAQUE, linewidth=2.4,
                label=rotulo_curva or "Distribuição teórica")

    ax.set_title(titulo)
    ax.set_xlabel(rotulo_x)
    ax.set_ylabel("Frequência absoluta")
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def boxplot(info_outliers, mediana_valor, titulo, rotulo_x):
    """Boxplot construido com os quartis calculados pelo nosso nucleo.

    ``ax.bxp`` recebe um dicionario de estatisticas PRONTAS -- e por isso
    que o Matplotlib nao calcula nada aqui. Os bigodes sao os limites de
    Tukey e os pontos alem deles sao os outliers detectados por
    ``detectar_outliers_iqr``.
    """
    fig, ax = nova_figura(altura=2.8)

    estatisticas = [
        {
            "label": rotulo_x,
            "med": mediana_valor,
            "q1": info_outliers["q1"],
            "q3": info_outliers["q3"],
            "whislo": info_outliers["limite_inferior"],
            "whishi": info_outliers["limite_superior"],
            "fliers": info_outliers["outliers"],
        }
    ]

    estilo = {
        "showfliers": True,
        "patch_artist": True,
        "boxprops": {"facecolor": COR_PRIMARIA, "alpha": 0.65},
        "medianprops": {"color": COR_DESTAQUE, "linewidth": 2},
        "flierprops": {"marker": "o", "markersize": 3, "alpha": 0.25,
                       "markerfacecolor": COR_SECUNDARIA,
                       "markeredgecolor": "none"},
    }
    # O parametro `vert` foi substituido por `orientation` no Matplotlib 3.11.
    # Tentamos o novo e caimos no antigo para continuar rodando em versoes
    # anteriores.
    try:
        ax.bxp(estatisticas, orientation="horizontal", **estilo)
    except TypeError:
        ax.bxp(estatisticas, vert=False, **estilo)
    ax.set_title(titulo)
    ax.set_xlabel(rotulo_x)
    fig.tight_layout()
    return fig


def barras_categorica(linhas, titulo, horizontal=True):
    """Grafico de barras para variavel qualitativa."""
    categorias = [linha["categoria"] for linha in linhas]
    valores = [linha["fi"] for linha in linhas]

    altura = max(2.6, 0.45 * len(categorias) + 1.4)
    fig, ax = nova_figura(altura=altura if horizontal else 4.2)

    if horizontal:
        posicoes = range(len(categorias))
        ax.barh(list(posicoes), valores, color=COR_PRIMARIA)
        ax.set_yticks(list(posicoes))
        ax.set_yticklabels(categorias)
        ax.invert_yaxis()
        ax.set_xlabel("Frequência absoluta")
    else:
        ax.bar(categorias, valores, color=COR_PRIMARIA)
        ax.set_ylabel("Frequência absoluta")
        ax.tick_params(axis="x", rotation=45)

    ax.set_title(titulo)
    fig.tight_layout()
    return fig


def pizza_categorica(linhas, titulo, limite_fatias=8):
    """Grafico de pizza; categorias pequenas viram uma fatia 'Outras'.

    Acima de ~8 fatias a pizza fica ilegivel -- agrupar e uma decisao de
    LEITURA, nao de calculo (as frequencias continuam vindo do nucleo).
    """
    if len(linhas) > limite_fatias:
        principais = linhas[: limite_fatias - 1]
        resto = sum(linha["fi"] for linha in linhas[limite_fatias - 1:])
        rotulos = [linha["categoria"] for linha in principais] + ["Outras"]
        valores = [linha["fi"] for linha in principais] + [resto]
    else:
        rotulos = [linha["categoria"] for linha in linhas]
        valores = [linha["fi"] for linha in linhas]

    fig, ax = nova_figura(largura=6, altura=5)
    ax.pie(valores, labels=rotulos, autopct="%1.1f%%", startangle=90,
           counterclock=False, textprops={"fontsize": 9},
           wedgeprops={"edgecolor": "white", "linewidth": 1})
    ax.set_title(titulo)
    ax.axis("equal")
    fig.tight_layout()
    return fig


def dispersao_com_reta(x, y, modelo, titulo, rotulo_x, rotulo_y, ponto_previsto=None):
    """Diagrama de dispersao com a reta de minimos quadrados sobreposta."""
    fig, ax = nova_figura(altura=4.8)

    ax.scatter(x, y, s=8, alpha=0.18, color=COR_PRIMARIA,
               edgecolors="none", label="Observações")

    x_min, x_max = min(x), max(x)
    xs = [x_min, x_max]
    ys = [modelo["a"] + modelo["b"] * v for v in xs]
    ax.plot(xs, ys, color=COR_DESTAQUE, linewidth=2.6,
            label=f"Reta ajustada: {modelo['equacao']}")

    if ponto_previsto is not None:
        px, py = ponto_previsto
        ax.scatter([px], [py], s=140, color=COR_SECUNDARIA, zorder=5,
                   marker="X", edgecolors="black", linewidths=0.8,
                   label=f"Predição: X={px:.4g} → Ŷ={py:.4g}")

    ax.set_title(titulo)
    ax.set_xlabel(rotulo_x)
    ax.set_ylabel(rotulo_y)
    ax.legend(frameon=False, loc="best", fontsize=9)
    fig.tight_layout()
    return fig


def grafico_residuos(x, res, rotulo_x):
    """Residuos contra X: se o modelo linear e adequado, nao deve haver padrao."""
    fig, ax = nova_figura(altura=3.2)
    ax.scatter(x, res, s=8, alpha=0.18, color=COR_TERCIARIA, edgecolors="none")
    ax.axhline(0, color=COR_DESTAQUE, linewidth=1.6)
    ax.set_title("Resíduos da regressão (e = y - ŷ)")
    ax.set_xlabel(rotulo_x)
    ax.set_ylabel("Resíduo")
    fig.tight_layout()
    return fig


def convergencia(series, valor_teorico, titulo, rotulo_y, escala_log=True):
    """Grafico de convergencia da Lei dos Grandes Numeros.

    O eixo X e logaritmico porque a convergencia e da ordem de
    1/sqrt(n): em escala linear os primeiros lancamentos -- justamente os
    mais instaveis e mais interessantes -- ficariam espremidos na origem.
    """
    fig, ax = nova_figura(altura=4.2)

    ns = list(range(1, len(series) + 1))
    ax.plot(ns, series, color=COR_PRIMARIA, linewidth=1.2,
            label="Estimativa acumulada")
    ax.axhline(valor_teorico, color=COR_DESTAQUE, linestyle="--", linewidth=2,
               label=f"Valor teórico = {valor_teorico:.6g}")

    if escala_log:
        ax.set_xscale("log")
        ax.set_xlabel("Número de repetições (escala logarítmica)")
    else:
        ax.set_xlabel("Número de repetições")

    ax.set_title(titulo)
    ax.set_ylabel(rotulo_y)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def barras_comparativas(categorias, observado, esperado, titulo, rotulo_y):
    """Barras lado a lado: frequencia observada contra a esperada pela teoria."""
    fig, ax = nova_figura()
    posicoes = list(range(len(categorias)))
    largura = 0.4

    ax.bar([p - largura / 2 for p in posicoes], observado, largura,
           label="Observado (simulação)", color=COR_PRIMARIA)
    ax.bar([p + largura / 2 for p in posicoes], esperado, largura,
           label="Esperado (teoria)", color=COR_SECUNDARIA)

    ax.set_xticks(posicoes)
    ax.set_xticklabels(categorias)
    ax.set_title(titulo)
    ax.set_ylabel(rotulo_y)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def dispersao_pi(px, py, dentro, estimativa):
    """Visualizacao do Monte Carlo de pi: pontos dentro e fora do quarto de circulo."""
    import math

    fig, ax = nova_figura(largura=5, altura=5)

    dx = [v for v, d in zip(px, dentro) if d]
    dy = [v for v, d in zip(py, dentro) if d]
    fx = [v for v, d in zip(px, dentro) if not d]
    fy = [v for v, d in zip(py, dentro) if not d]

    ax.scatter(dx, dy, s=4, color=COR_PRIMARIA, alpha=0.5, label="Dentro")
    ax.scatter(fx, fy, s=4, color=COR_SECUNDARIA, alpha=0.5, label="Fora")

    arco_x = [i / 200 for i in range(201)]
    arco_y = [math.sqrt(max(0.0, 1 - v * v)) for v in arco_x]
    ax.plot(arco_x, arco_y, color=COR_DESTAQUE, linewidth=2)

    ax.set_title(f"Estimativa de π = {estimativa:.6f}")
    ax.set_aspect("equal")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    fig.tight_layout()
    return fig
