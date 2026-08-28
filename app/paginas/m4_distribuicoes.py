"""
Modulo 4 -- Distribuicoes Teoricas.

Sobrepoe ao histograma de uma variavel a curva de distribuicoes teoricas
candidatas, com os parametros estimados a partir dos proprios dados, e
compara a qualidade dos ajustes.
"""

import math

import pandas as pd
import streamlit as st

from app import carregador, graficos
from minhastats import descritiva as md
from minhastats import distribuicoes as mdist
from minhastats import frequencias as mf


def renderizar(df):
    st.header("📐 Módulo 4 — Distribuições Teóricas")

    st.markdown(
        "Escolha uma variável e sobreponha ao seu histograma a curva de uma ou "
        "mais distribuições teóricas, com **parâmetros estimados a partir dos "
        "próprios dados**."
    )

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        variavel = st.selectbox(
            "Variável",
            list(carregador.VARIAVEIS_NUMERICAS.keys()),
            index=list(carregador.VARIAVEIS_NUMERICAS.keys()).index("temp_c"),
            format_func=carregador.rotulo,
            key="m4_var",
        )
    with c2:
        k = st.slider("Classes do histograma", 5, 40,
                      mf.regra_sturges(len(df)), key="m4_k")
    with c3:
        st.caption(" ")
        st.caption(" ")

    dados = carregador.coluna_como_lista(df, variavel)
    nome = carregador.rotulo(variavel)

    candidatas = st.multiselect(
        "Distribuições candidatas",
        ["Normal", "Uniforme", "Exponencial", "Poisson", "Binomial"],
        default=["Normal", "Uniforme"],
        help="A Normal é obrigatória pelo enunciado; escolha ao menos mais uma.",
        key="m4_candidatas",
    )

    if not candidatas:
        st.warning("Selecione ao menos uma distribuição candidata.")
        return

    linhas = mf.tabela_frequencias_continua(dados, k=k)
    n = len(dados)
    largura = linhas[0]["ls"] - linhas[0]["li"]
    x_min, x_max = md.minimo(dados), md.maximo(dados)

    # --- Estimacao dos parametros -----------------------------------------
    st.markdown("### Parâmetros estimados a partir dos dados")

    ajustes = {}
    linhas_parametros = []

    for candidata in candidatas:
        try:
            if candidata == "Normal":
                p = mdist.estimar_normal(dados)
                funcao = lambda v, p=p: mdist.normal_pdf(v, p["mu"], p["sigma"])
                formula = r"\hat{\mu} = \bar{x},\quad \hat{\sigma} = s"
                texto = f"μ̂ = {p['mu']:.4f}   σ̂ = {p['sigma']:.4f}"
                discreta = False

            elif candidata == "Uniforme":
                p = mdist.estimar_uniforme(dados)
                funcao = lambda v, p=p: mdist.uniforme_pdf(v, p["a"], p["b"])
                formula = r"\hat{a} = x_{min},\quad \hat{b} = x_{max}"
                texto = f"â = {p['a']:.4f}   b̂ = {p['b']:.4f}"
                discreta = False

            elif candidata == "Exponencial":
                p = mdist.estimar_exponencial(dados)
                funcao = lambda v, p=p: mdist.exponencial_pdf(v, p["lam"])
                formula = r"\hat{\lambda} = 1/\bar{x}"
                texto = f"λ̂ = {p['lam']:.6f}   (média = {1/p['lam']:.4f})"
                discreta = False

            elif candidata == "Poisson":
                p = mdist.estimar_poisson(dados)
                # Para sobrepor uma pmf discreta a um histograma continuo,
                # avaliamos a pmf no inteiro mais proximo do ponto.
                funcao = lambda v, p=p: mdist.poisson_pmf(int(round(v)), p["lam"])
                formula = r"\hat{\lambda} = \bar{x}"
                texto = f"λ̂ = {p['lam']:.4f}"
                discreta = True

            else:  # Binomial
                p = mdist.estimar_binomial(dados)
                funcao = lambda v, p=p: mdist.binomial_pmf(int(round(v)), p["n"], p["p"])
                formula = r"\hat{n} = x_{max},\quad \hat{p} = \bar{x}/\hat{n}"
                texto = f"n̂ = {p['n']}   p̂ = {p['p']:.6f}"
                discreta = True

            qualidade = mdist.qualidade_ajuste(linhas, funcao, n)
            ajustes[candidata] = {
                "funcao": funcao,
                "parametros": texto,
                "formula": formula,
                "qualidade": qualidade,
                "discreta": discreta,
            }
            linhas_parametros.append(
                {
                    "Distribuição": candidata,
                    "Parâmetros estimados": texto,
                    "χ² total": round(qualidade["qui_quadrado"], 2),
                    "χ² por classe": round(qualidade["qui_quadrado_por_classe"], 2),
                }
            )
        except ValueError as erro:
            st.warning(f"**{candidata}** não pôde ser ajustada: {erro}")

    if not ajustes:
        return

    st.dataframe(pd.DataFrame(linhas_parametros), width="stretch",
                 hide_index=True)
    st.caption(
        "χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ, com Eᵢ ≈ n · f(ponto médio) · h. "
        "**Menor χ² = melhor ajuste.** Usamos este número apenas como medida "
        "descritiva comparativa entre as candidatas, não como teste de "
        "hipótese formal (não calculamos p-valor nem corrigimos os graus de "
        "liberdade pelos parâmetros estimados)."
    )

    # --- Graficos com a curva sobreposta ----------------------------------
    st.markdown("### Histograma com a curva teórica sobreposta")

    passo = (x_max - x_min) / 400 if x_max > x_min else 1.0
    xs = [x_min + i * passo for i in range(401)]
    eixo_x = carregador.eixo(variavel)

    abas = st.tabs(list(ajustes.keys()))
    for aba, (candidata, ajuste) in zip(abas, ajustes.items()):
        with aba:
            ys = [ajuste["funcao"](v) * largura * n for v in xs]
            st.pyplot(
                graficos.histograma(
                    linhas,
                    f"{nome} — ajuste {candidata}",
                    eixo_x,
                    curva=(xs, ys),
                    rotulo_curva=f"{candidata}: {ajuste['parametros']}",
                )
            )
            st.latex(ajuste["formula"])

            with st.expander("Tabela: frequência observada × esperada por classe"):
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Classe": d["classe"],
                                "Observado (Oᵢ)": d["observado"],
                                "Esperado (Eᵢ)": round(d["esperado"], 2),
                                "(O−E)²/E": round(d["contribuicao"], 3)
                                if not math.isnan(d["contribuicao"]) else "—",
                            }
                            for d in ajuste["qualidade"]["detalhes"]
                        ]
                    ),
                    width="stretch", hide_index=True,
                )

    # --- Diagnostico ------------------------------------------------------
    st.markdown("### 🧠 Discussão da qualidade do ajuste")

    melhor = min(ajustes.items(), key=lambda item: item[1]["qualidade"]["qui_quadrado"])
    pior = max(ajustes.items(), key=lambda item: item[1]["qualidade"]["qui_quadrado"])

    assimetria = md.assimetria_momento(dados)
    curtose = md.curtose_momento(dados)

    diagnostico = [
        f"Entre as candidatas testadas, a **{melhor[0]}** apresentou o melhor "
        f"ajuste (χ² = {melhor[1]['qualidade']['qui_quadrado']:.2f})"
    ]
    if len(ajustes) > 1:
        diagnostico.append(
            f", contra χ² = {pior[1]['qualidade']['qui_quadrado']:.2f} da "
            f"**{pior[0]}**, a pior do conjunto"
        )
    diagnostico.append(".")

    diagnostico.append(
        f" A variável tem assimetria de {assimetria:.4f} e excesso de curtose de "
        f"{curtose:.4f}."
    )

    if abs(assimetria) < 0.3 and abs(curtose) < 0.8:
        diagnostico.append(
            " Esses dois valores estão próximos dos da Normal (0 e 0), o que é "
            "coerente com um bom ajuste normal."
        )
    elif assimetria > 1.0:
        diagnostico.append(
            " A forte assimetria à direita explica por que a Normal — que é "
            "simétrica por construção — não consegue acompanhar a cauda longa: "
            "ela superestima a frequência à esquerda e subestima à direita. "
            "Distribuições assimétricas (Exponencial, Log-Normal, Gama) são "
            "candidatas mais plausíveis."
        )
    else:
        diagnostico.append(
            " A distribuição foge moderadamente da forma normal; observe no "
            "gráfico onde a curva se descola das barras."
        )

    # Diagnostico adicional para contagens
    try:
        indice = mdist.indice_dispersao(dados)
        if all(float(v).is_integer() for v in dados[:200]):
            diagnostico.append(
                f" Como esta é uma variável de CONTAGEM, vale checar o índice de "
                f"dispersão s²/x̄ = **{indice:.2f}**. Na Poisson esse índice vale "
                f"exatamente 1 (média = variância)."
            )
            if indice > 2:
                diagnostico.append(
                    f" Um valor de {indice:.2f} indica forte SOBREDISPERSÃO: a "
                    f"variabilidade real é muito maior do que a Poisson admite, "
                    f"logo a Poisson é inadequada aqui."
                )
    except ValueError:
        pass

    st.info("".join(diagnostico))

    st.warning(
        "**Nota metodológica:** um ajuste visualmente razoável não prova que a "
        "variável siga a distribuição teórica. Para uma conclusão formal seria "
        "necessário um teste de aderência (qui-quadrado com graus de liberdade "
        "corrigidos, Kolmogorov-Smirnov ou Anderson-Darling), fora do escopo "
        "deste módulo."
    )
