"""
Modulo 2 -- Estatistica Descritiva Interativa.

O usuario escolhe uma variavel e recebe tabela de frequencias, medidas de
tendencia central e dispersao, graficos adequados ao tipo da variavel,
deteccao de outliers pelo IQR e interpretacao textual automatica.

TODOS os numeros desta pagina vem de `minhastats`.
"""

import pandas as pd
import streamlit as st

from app import carregador, graficos
from minhastats import descritiva as md
from minhastats import frequencias as mf


def _formatar(valor, casas=4):
    """Formata numeros para exibicao, sem notacao cientifica desnecessaria."""
    if isinstance(valor, list):
        return ", ".join(f"{v:.{casas}g}" for v in valor[:5]) or "amodal"
    if isinstance(valor, int):
        return str(valor)
    return f"{valor:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def renderizar(df):
    st.header("📊 Módulo 2 — Estatística Descritiva Interativa")

    tipo = st.radio(
        "Tipo de variável",
        ["Numérica (contínua/discreta)", "Categórica (qualitativa)"],
        horizontal=True,
        key="m2_tipo",
    )

    if tipo.startswith("Numérica"):
        _numerica(df)
    else:
        _categorica(df)


# ---------------------------------------------------------------------------
# Variavel numerica
# ---------------------------------------------------------------------------


def _numerica(df):
    coluna_esq, coluna_dir = st.columns([2, 1])

    with coluna_esq:
        variavel = st.selectbox(
            "Variável",
            list(carregador.VARIAVEIS_NUMERICAS.keys()),
            format_func=carregador.rotulo,
            key="m2_var_num",
        )
    with coluna_dir:
        n_sugerido = mf.regra_sturges(len(df))
        k = st.slider(
            "Número de classes do histograma",
            min_value=3, max_value=40, value=n_sugerido,
            help=f"A regra de Sturges sugere k = ⌈1 + log₂(n)⌉ = {n_sugerido} para n = {len(df)}.",
            key="m2_k",
        )

    dados = carregador.coluna_como_lista(df, variavel)
    nome = carregador.rotulo(variavel)

    st.caption(carregador.descricao(variavel))

    # --- Medidas ----------------------------------------------------------
    resumo = md.resumo(dados)

    st.markdown("### Medidas de tendência central e dispersão")
    st.caption("Todos os valores calculados por `minhastats.descritiva.resumo()`.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("n", f"{resumo['n']:,}".replace(",", "."))
    c2.metric("Média", _formatar(resumo["media"]))
    c3.metric("Mediana", _formatar(resumo["mediana"]))
    c4.metric("Moda", _formatar(resumo["moda"]))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mínimo", _formatar(resumo["minimo"]))
    c2.metric("Máximo", _formatar(resumo["maximo"]))
    c3.metric("Amplitude", _formatar(resumo["amplitude"]))
    c4.metric("IQR (Q3 − Q1)", _formatar(resumo["iqr"]))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Variância amostral s²", _formatar(resumo["variancia_amostral"]))
    c2.metric("Desvio padrão s", _formatar(resumo["desvio_padrao_amostral"]))
    c3.metric("Desvio padrão σ", _formatar(resumo["desvio_padrao_populacional"]))
    c4.metric("Coef. de variação", f"{resumo['coeficiente_variacao']:.2f}%")

    with st.expander("Ver todas as medidas em tabela (amostral × populacional)"):
        st.dataframe(
            pd.DataFrame(
                [
                    {"Medida": "Tamanho da amostra (n)", "Valor": _formatar(resumo["n"])},
                    {"Medida": "Média (x̄)", "Valor": _formatar(resumo["media"], 6)},
                    {"Medida": "Mediana (Md)", "Valor": _formatar(resumo["mediana"], 6)},
                    {"Medida": "Moda (Mo)", "Valor": _formatar(resumo["moda"], 6)},
                    {"Medida": "Mínimo", "Valor": _formatar(resumo["minimo"], 6)},
                    {"Medida": "Q1 (percentil 25)", "Valor": _formatar(resumo["q1"], 6)},
                    {"Medida": "Q2 (percentil 50)", "Valor": _formatar(resumo["q2"], 6)},
                    {"Medida": "Q3 (percentil 75)", "Valor": _formatar(resumo["q3"], 6)},
                    {"Medida": "Máximo", "Valor": _formatar(resumo["maximo"], 6)},
                    {"Medida": "Amplitude (A)", "Valor": _formatar(resumo["amplitude"], 6)},
                    {"Medida": "Amplitude interquartil (IQR)", "Valor": _formatar(resumo["iqr"], 6)},
                    {"Medida": "Variância populacional (σ²)", "Valor": _formatar(resumo["variancia_populacional"], 6)},
                    {"Medida": "Variância amostral (s²)", "Valor": _formatar(resumo["variancia_amostral"], 6)},
                    {"Medida": "Desvio padrão populacional (σ)", "Valor": _formatar(resumo["desvio_padrao_populacional"], 6)},
                    {"Medida": "Desvio padrão amostral (s)", "Valor": _formatar(resumo["desvio_padrao_amostral"], 6)},
                    {"Medida": "Coeficiente de variação (CV)", "Valor": f"{resumo['coeficiente_variacao']:.4f}%"},
                    {"Medida": "Erro padrão da média (s/√n)", "Valor": _formatar(resumo["erro_padrao"], 6)},
                    {"Medida": "Assimetria de Pearson", "Valor": _formatar(resumo["assimetria_pearson"], 6)},
                    {"Medida": "Assimetria de momento (g₁)", "Valor": _formatar(resumo["assimetria_momento"], 6)},
                    {"Medida": "Excesso de curtose (g₂)", "Valor": _formatar(resumo["curtose"], 6)},
                ]
            ),
            width="stretch", hide_index=True,
        )

    # --- Graficos ---------------------------------------------------------
    st.markdown("### Gráficos")

    linhas = mf.tabela_frequencias_continua(dados, k=k)
    eixo_x = carregador.eixo(variavel)

    st.pyplot(
        graficos.histograma(linhas, f"Histograma de {nome} (k = {k} classes)", eixo_x)
    )

    info_outliers = mf.detectar_outliers_iqr(dados)
    st.pyplot(
        graficos.boxplot(info_outliers, resumo["mediana"], f"Boxplot de {nome}", eixo_x)
    )
    st.caption(
        "O boxplot é desenhado com `ax.bxp`, alimentado pelos quartis, limites e "
        "outliers já calculados por `minhastats` — o Matplotlib não recalcula nada."
    )

    # --- Tabela de frequencias -------------------------------------------
    st.markdown("### Tabela de frequências por classes")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Classe": l["classe"],
                    "Ponto médio": round(l["ponto_medio"], 4),
                    "fi": l["fi"],
                    "fr": round(l["fr"], 6),
                    "%": round(l["percentual"], 2),
                    "Fi (acum.)": l["Fi"],
                    "% acum.": round(l["Fr_percentual"], 2),
                }
                for l in linhas
            ]
        ),
        width="stretch", hide_index=True,
    )

    # --- Outliers ---------------------------------------------------------
    st.markdown("### Detecção de outliers pela regra do IQR")
    st.latex(r"LI = Q_1 - 1{,}5 \cdot IQR \qquad LS = Q_3 + 1{,}5 \cdot IQR")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Limite inferior", _formatar(info_outliers["limite_inferior"]))
    c2.metric("Limite superior", _formatar(info_outliers["limite_superior"]))
    c3.metric("Outliers", info_outliers["n_outliers"])
    c4.metric("% da amostra", f"{info_outliers['percentual']:.2f}%")

    if info_outliers["n_outliers"] > 0:
        st.info(
            f"{info_outliers['n_abaixo']} valores abaixo do limite inferior e "
            f"{info_outliers['n_acima']} acima do superior. Valores extremos "
            f"observados: {', '.join(f'{v:.4g}' for v in info_outliers['outliers'][:10])}"
            + (" ..." if info_outliers["n_outliers"] > 10 else "")
        )
    else:
        st.success("Nenhum outlier detectado pela regra do IQR.")

    # --- Interpretacao automatica -----------------------------------------
    st.markdown("### 🧠 Interpretação automática")
    st.info(mf.interpretar_distribuicao(dados, nome))


# ---------------------------------------------------------------------------
# Variavel categorica
# ---------------------------------------------------------------------------


def _categorica(df):
    c1, c2 = st.columns([2, 1])
    with c1:
        variavel = st.selectbox(
            "Variável",
            list(carregador.VARIAVEIS_CATEGORICAS.keys()),
            format_func=carregador.rotulo,
            key="m2_var_cat",
        )
    with c2:
        ordem = st.selectbox(
            "Ordenar por", ["frequencia", "categoria"],
            format_func=lambda v: "Frequência (decrescente)" if v == "frequencia" else "Categoria",
            key="m2_ordem",
        )

    nome = carregador.rotulo(variavel)
    st.caption(carregador.descricao(variavel))

    linhas = mf.tabela_frequencias_categorica(df[variavel].tolist(), ordenar_por=ordem)
    n = sum(l["fi"] for l in linhas)

    st.markdown("### Tabela de frequências")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Categoria": l["categoria"],
                    "fi": l["fi"],
                    "fr": round(l["fr"], 6),
                    "%": round(l["percentual"], 2),
                    "Fi (acum.)": l["Fi"],
                    "% acum.": round(l["Fr_percentual"], 2),
                }
                for l in linhas
            ]
        ),
        width="stretch", hide_index=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Categorias distintas", len(linhas))
    c2.metric("Categoria modal", linhas[0]["categoria"] if ordem == "frequencia"
              else max(linhas, key=lambda l: l["fi"])["categoria"])
    c3.metric("n", f"{n:,}".replace(",", "."))

    st.markdown("### Gráficos")
    aba_barras, aba_pizza = st.tabs(["Barras", "Pizza"])
    with aba_barras:
        st.pyplot(graficos.barras_categorica(linhas, f"Frequência de {nome}"))
    with aba_pizza:
        st.pyplot(graficos.pizza_categorica(linhas, f"Composição de {nome}"))

    # --- Interpretacao ----------------------------------------------------
    st.markdown("### 🧠 Interpretação automática")
    modal = max(linhas, key=lambda l: l["fi"])
    menor = min(linhas, key=lambda l: l["fi"])
    razao = modal["fi"] / menor["fi"] if menor["fi"] else float("inf")

    if razao > 10:
        equilibrio = (
            "A distribuição é MUITO DESEQUILIBRADA: a categoria mais frequente "
            f"aparece {razao:.1f} vezes mais que a menos frequente."
        )
    elif razao > 3:
        equilibrio = (
            f"A distribuição é DESEQUILIBRADA (razão de {razao:.1f}× entre a "
            "categoria mais e a menos frequente)."
        )
    else:
        equilibrio = (
            f"A distribuição é razoavelmente EQUILIBRADA entre as categorias "
            f"(razão de apenas {razao:.1f}× entre os extremos)."
        )

    st.info(
        f"A variável **{nome}** possui {len(linhas)} categorias. A categoria modal é "
        f"**{modal['categoria']}**, com {modal['fi']} ocorrências "
        f"({modal['percentual']:.2f}% do total). A menos frequente é "
        f"**{menor['categoria']}**, com {menor['fi']} ocorrências "
        f"({menor['percentual']:.2f}%). {equilibrio}"
    )

    # --- Cruzamento com uma numerica --------------------------------------
    st.markdown("### Comparação de uma variável numérica entre as categorias")
    st.caption(
        "Média, mediana e desvio padrão calculados separadamente em cada "
        "categoria — sempre por `minhastats`, nunca por `groupby().mean()`."
    )

    numerica = st.selectbox(
        "Variável numérica a comparar",
        list(carregador.VARIAVEIS_NUMERICAS.keys()),
        index=list(carregador.VARIAVEIS_NUMERICAS.keys()).index("cnt"),
        format_func=carregador.rotulo,
        key="m2_cruzamento",
    )

    comparacao = []
    for l in sorted(linhas, key=lambda item: item["categoria"]):
        subconjunto = df[df[variavel].astype(str) == l["categoria"]][numerica]
        valores = [float(v) for v in subconjunto.tolist()]
        if len(valores) < 2:
            continue
        comparacao.append(
            {
                "Categoria": l["categoria"],
                "n": len(valores),
                "Média": round(md.media(valores), 3),
                "Mediana": round(md.mediana(valores), 3),
                "Desvio padrão": round(md.desvio_padrao_amostral(valores), 3),
                "CV (%)": round(md.coeficiente_variacao(valores), 2),
            }
        )

    if comparacao:
        st.dataframe(pd.DataFrame(comparacao), width="stretch", hide_index=True)
        maior = max(comparacao, key=lambda item: item["Média"])
        menor_cat = min(comparacao, key=lambda item: item["Média"])
        diferenca = (
            (maior["Média"] / menor_cat["Média"] - 1) * 100
            if menor_cat["Média"] else float("inf")
        )
        st.info(
            f"A média de **{carregador.rotulo(numerica)}** é maior em "
            f"**{maior['Categoria']}** ({maior['Média']:.2f}) e menor em "
            f"**{menor_cat['Categoria']}** ({menor_cat['Média']:.2f}) — "
            f"uma diferença de {diferenca:.1f}%."
        )
