"""
Laboratorio Estatistico Interativo
==================================

Ponto de entrada da aplicacao Streamlit.

    streamlit run app.py

Arquitetura (nucleo separado da interface):

    minhastats/   -> nucleo estatistico proprio, Python puro, sem dependencias
    app/          -> interface Streamlit; nao calcula nada, so exibe
    tests/        -> validacao de cada funcao do nucleo contra NumPy/SciPy

Este arquivo apenas monta a navegacao e delega para as paginas de cada
modulo em app/paginas/.
"""

import streamlit as st

st.set_page_config(
    page_title="Laboratório Estatístico Interativo",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app import carregador  # noqa: E402  (precisa vir depois de set_page_config)
from app.paginas import (  # noqa: E402
    m0_dados,
    m2_descritiva,
    m3_simulacao,
    m4_distribuicoes,
    m5_regressao,
    m6_descobertas,
)

MODULOS = {
    "Módulo 0 — Dados Reais": m0_dados,
    "Módulo 2 — Estatística Descritiva": m2_descritiva,
    "Módulo 3 — Probabilidade e Simulação": m3_simulacao,
    "Módulo 4 — Distribuições Teóricas": m4_distribuicoes,
    "Módulo 5 — Correlação e Regressão": m5_regressao,
    "Módulo 6 — Descobertas": m6_descobertas,
}


def main():
    st.sidebar.title("Laboratório Estatístico")
    st.sidebar.caption(
        "Matemática e Estatística para Computação — Sistematização"
    )

    escolha = st.sidebar.radio("Navegação", list(MODULOS.keys()), key="navegacao")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
### Regra de ouro

Todas as medidas exibidas vêm do pacote **`minhastats`**, escrito do zero
em Python puro (só `math` e `random`).

NumPy, SciPy e Pandas aparecem apenas para:
1. **carregar** o CSV (`pandas.read_csv`);
2. **validar** o núcleo nos testes automatizados.

**518 testes automatizados**: 485 comparam cada função nossa com a
referência das bibliotecas (tolerância relativa de 1e-9), 18 vigiam esta
regra lendo o código-fonte, e 15 executam a interface de ponta a ponta.

---

### Dataset

**Bike Sharing Dataset** — UCI ML Repository
17.379 registros horários (2011–2012)

[Fonte original]({carregador.URL_DATASET})
"""
    )

    try:
        df = carregador.carregar_dados()
    except FileNotFoundError as erro:
        st.error(str(erro))
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Registros carregados: {len(df):,}".replace(",", "."))

    MODULOS[escolha].renderizar(df)


if __name__ == "__main__":
    main()
