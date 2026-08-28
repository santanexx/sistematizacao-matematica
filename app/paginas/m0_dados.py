"""Modulo 0 -- Dados Reais: apresentacao e conferencia do dataset."""

import pandas as pd
import streamlit as st

from app import carregador
from minhastats import frequencias as mf


def renderizar(df):
    st.header("📦 Módulo 0 — Dados Reais")

    st.markdown(
        f"""
**Dataset:** Bike Sharing Dataset — *UCI Machine Learning Repository*
**Fonte original:** [{carregador.URL_DATASET}]({carregador.URL_DATASET})
**Arquivo utilizado:** `hour.csv` (registros horários de 2011 e 2012 do
sistema de bicicletas compartilhadas Capital Bikeshare, Washington D.C.)
"""
    )

    # --- Conferencia dos requisitos do enunciado --------------------------
    numericas = [c for c in carregador.VARIAVEIS_NUMERICAS if c in df.columns]
    categoricas = [c for c in carregador.VARIAVEIS_CATEGORICAS if c in df.columns]

    c1, c2, c3 = st.columns(3)
    c1.metric("Registros", f"{len(df):,}".replace(",", "."),
              help="Exigência do enunciado: pelo menos 1.000")
    c2.metric("Variáveis numéricas", len(numericas),
              help="Exigência do enunciado: pelo menos 4")
    c3.metric("Variáveis categóricas", len(categoricas),
              help="Exigência do enunciado: pelo menos 2")

    requisitos = [
        ("Pelo menos 1.000 registros", len(df) >= 1000, f"{len(df)} registros"),
        ("Pelo menos 4 variáveis numéricas", len(numericas) >= 4,
         f"{len(numericas)} disponíveis"),
        ("Pelo menos 2 variáveis categóricas", len(categoricas) >= 2,
         f"{len(categoricas)} disponíveis"),
        ("Fonte pública e citável", True, "UCI ML Repository"),
    ]
    st.markdown("#### Conferência dos requisitos do Módulo 0")
    for texto, ok, detalhe in requisitos:
        st.markdown(f"- {'✅' if ok else '❌'} **{texto}** — {detalhe}")

    # --- Amostra dos dados -------------------------------------------------
    st.markdown("#### Amostra dos dados")
    st.caption(
        "As colunas em unidades reais (°C, %, km/h) são derivadas das colunas "
        "originais normalizadas — a transformação está documentada em "
        "`app/carregador.py`."
    )
    colunas_exibidas = [
        "dteday", "hr", "estacao", "clima", "periodo", "dia_util",
        "temp_c", "hum_pct", "windspeed_kmh", "casual", "registered", "cnt",
    ]
    st.dataframe(df[colunas_exibidas].head(50), width="stretch",
                 hide_index=True)

    # --- Dicionario de variaveis ------------------------------------------
    st.markdown("#### Dicionário de variáveis")

    aba_num, aba_cat = st.tabs(["Numéricas", "Categóricas"])

    with aba_num:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Coluna": nome,
                        "Rótulo": info["rotulo"],
                        "Unidade": info["unidade"] or "—",
                        "Descrição": info["descricao"],
                    }
                    for nome, info in carregador.VARIAVEIS_NUMERICAS.items()
                ]
            ),
            width="stretch", hide_index=True,
        )

    with aba_cat:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Coluna": nome,
                        "Rótulo": info["rotulo"],
                        "Categorias": df[nome].nunique(),
                        "Descrição": info["descricao"],
                    }
                    for nome, info in carregador.VARIAVEIS_CATEGORICAS.items()
                ]
            ),
            width="stretch", hide_index=True,
        )

    # --- Integridade -------------------------------------------------------
    st.markdown("#### Integridade dos dados")
    faltantes = int(df.isna().sum().sum())
    if faltantes == 0:
        st.success(
            "Nenhum valor ausente no dataset. Ainda assim, todas as funções de "
            "`minhastats` descartam NaN por segurança — ver `_validar()` em "
            "`minhastats/descritiva.py`."
        )
    else:
        st.warning(f"{faltantes} valores ausentes encontrados e descartados nos cálculos.")

    # --- Distribuicao das categoricas -------------------------------------
    st.markdown("#### Distribuição das variáveis categóricas")
    st.caption("Frequências calculadas por `minhastats.frequencias.tabela_frequencias_categorica`.")

    escolha = st.selectbox(
        "Variável categórica",
        categoricas,
        format_func=carregador.rotulo,
        key="m0_categorica",
    )
    linhas = mf.tabela_frequencias_categorica(df[escolha].tolist(), ordenar_por="categoria")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Categoria": l["categoria"],
                    "fi": l["fi"],
                    "fr": round(l["fr"], 6),
                    "%": round(l["percentual"], 2),
                }
                for l in linhas
            ]
        ),
        width="stretch", hide_index=True,
    )
