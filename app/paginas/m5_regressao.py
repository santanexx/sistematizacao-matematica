"""
Modulo 5 -- Correlacao e Regressao Linear Simples.

Dispersao, correlacao de Pearson (da nossa biblioteca), reta de minimos
quadrados (implementada por nos), equacao, R^2 e predicao interativa.
"""

import math

import pandas as pd
import streamlit as st

from app import carregador, graficos
from minhastats import associacao as ma
from minhastats import descritiva as md


def renderizar(df):
    st.header("📈 Módulo 5 — Correlação e Regressão Linear")

    variaveis = list(carregador.VARIAVEIS_NUMERICAS.keys())

    c1, c2 = st.columns(2)
    with c1:
        var_x = st.selectbox(
            "Variável independente (X)", variaveis,
            index=variaveis.index("temp_c"),
            format_func=carregador.rotulo, key="m5_x",
        )
    with c2:
        var_y = st.selectbox(
            "Variável dependente (Y)", variaveis,
            index=variaveis.index("cnt"),
            format_func=carregador.rotulo, key="m5_y",
        )

    if var_x == var_y:
        st.error("Escolha duas variáveis diferentes: a regressão de X sobre si "
                 "mesmo é trivial (R² = 1).")
        return

    x = carregador.coluna_como_lista(df, var_x)
    y = carregador.coluna_como_lista(df, var_y)
    nome_x, nome_y = carregador.rotulo(var_x), carregador.rotulo(var_y)
    unidade_x, unidade_y = carregador.unidade(var_x), carregador.unidade(var_y)

    # --- Correlacao -------------------------------------------------------
    r = ma.correlacao_pearson(x, y)
    cov = ma.covariancia_amostral(x, y)
    modelo = ma.regressao_linear(x, y)

    st.markdown("### Correlação")
    st.latex(
        r"r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}"
        r"{\sqrt{\sum (x_i - \bar{x})^2}\sqrt{\sum (y_i - \bar{y})^2}}"
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Correlação de Pearson (r)", f"{r:.6f}")
    c2.metric("Coeficiente de determinação (R²)", f"{modelo['r2']:.6f}")
    c3.metric("Covariância amostral", f"{cov:,.4f}".replace(",", "."))
    c4.metric("n (pares)", f"{modelo['n']:,}".replace(",", "."))

    st.info(f"**Leitura de r = {r:.4f}:** {ma.interpretar_correlacao(r)}.")

    # --- Regressao --------------------------------------------------------
    st.markdown("### Regressão linear simples pelo método dos mínimos quadrados")
    st.latex(
        r"b = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}"
        r" \qquad a = \bar{y} - b\bar{x}"
    )

    st.success(f"### Equação da reta:  ŷ = {modelo['b']:.6f}·x "
               f"{'+' if modelo['a'] >= 0 else '−'} {abs(modelo['a']):.6f}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Intercepto (a)", f"{modelo['a']:.6f}")
    c2.metric("Coef. angular (b)", f"{modelo['b']:.6f}")
    c3.metric("R²", f"{modelo['r2']:.6f}")
    c4.metric("Erro padrão da estimativa", f"{modelo['erro_padrao_estimativa']:.4f}")

    # --- Grafico de dispersao com predicao --------------------------------
    st.markdown("### Diagrama de dispersão e reta ajustada")

    st.markdown("#### 🎯 Predição interativa")
    c1, c2 = st.columns([1, 2])
    with c1:
        x_min, x_max = md.minimo(x), md.maximo(x)
        valor_x = st.number_input(
            f"Digite um valor de X ({nome_x})",
            value=float(round((x_min + x_max) / 2, 4)),
            step=float(round((x_max - x_min) / 100, 4)) or 0.1,
            format="%.4f",
            key="m5_predicao",
        )
    y_previsto = ma.prever(modelo, valor_x)
    with c2:
        st.metric(
            f"Ŷ previsto ({nome_y})",
            f"{y_previsto:,.4f}".replace(",", "."),
            help="Valor calculado por minhastats.associacao.prever()",
        )
        if valor_x < x_min or valor_x > x_max:
            st.warning(
                f"⚠️ **Extrapolação.** O valor {valor_x:.4f} está fora da faixa "
                f"observada de X ([{x_min:.4f}; {x_max:.4f}]). A reta só foi "
                f"ajustada dentro dessa faixa — fora dela a previsão não tem "
                f"sustentação nos dados."
            )

    st.pyplot(
        graficos.dispersao_com_reta(
            x, y, modelo,
            f"{nome_y} em função de {nome_x}",
            carregador.eixo(var_x),
            carregador.eixo(var_y),
            ponto_previsto=(valor_x, y_previsto),
        )
    )

    # --- Interpretacao dos coeficientes -----------------------------------
    st.markdown("### 🧠 Interpretação dos coeficientes")

    passo_unidade = f" {unidade_x}" if unidade_x else " unidade"
    st.markdown(
        f"""
- **Coeficiente angular b = {modelo['b']:.6f}** — a cada aumento de 1{passo_unidade}
  em *{nome_x}*, o modelo prevê uma variação **{'de +' if modelo['b'] >= 0 else 'de '}{modelo['b']:.4f}**
  em *{nome_y}*{f' ({unidade_y})' if unidade_y else ''}.
- **Intercepto a = {modelo['a']:.6f}** — é o valor previsto de *{nome_y}* quando
  *{nome_x}* = 0. {"Como X = 0 está dentro da faixa observada, esse valor tem leitura direta."
  if x_min <= 0 <= x_max else
  f"⚠️ X = 0 está FORA da faixa observada ([{x_min:.4f}; {x_max:.4f}]), então o intercepto é apenas um parâmetro de ajuste da reta, sem significado prático."}
- **R² = {modelo['r2']:.6f}** — a variável *{nome_x}* explica
  **{modelo['r2'] * 100:.2f}%** da variação total de *{nome_y}*. Os
  {100 - modelo['r2'] * 100:.2f}% restantes se devem a outros fatores não
  incluídos no modelo.
- **Erro padrão da estimativa = {modelo['erro_padrao_estimativa']:.4f}** — é o
  desvio típico dos pontos em relação à reta, na mesma unidade de *{nome_y}*.
"""
    )

    st.error(
        "⚠️ **Correlação NÃO implica causalidade.** "
        f"Encontrar r = {r:.4f} entre *{nome_x}* e *{nome_y}* significa apenas que "
        "as duas variáveis se movem juntas nos dados observados. Não prova que uma "
        "cause a outra: a relação pode ser invertida, pode ser mediada por uma "
        "terceira variável (confundidora) ou pode ser inteiramente coincidência. "
        "No caso deste dataset, por exemplo, temperatura e aluguéis crescem juntos, "
        "mas ambos também variam com a estação do ano, o horário e o dia da semana — "
        "estabelecer causalidade exigiria um experimento controlado ou um modelo "
        "causal explícito, não uma reta de regressão."
    )

    # --- Decomposicao da variacao e residuos ------------------------------
    st.markdown("### Decomposição da variação e análise dos resíduos")
    st.latex(r"SQ_{tot} = SQ_{reg} + SQ_{res} \qquad R^2 = 1 - \frac{SQ_{res}}{SQ_{tot}}")

    st.dataframe(
        pd.DataFrame(
            [
                {"Fonte de variação": "Regressão (explicada)",
                 "Soma de quadrados": round(modelo["sq_regressao"], 4),
                 "% do total": round(100 * modelo["sq_regressao"] / modelo["sq_total"], 2)},
                {"Fonte de variação": "Resíduos (não explicada)",
                 "Soma de quadrados": round(modelo["sq_residuos"], 4),
                 "% do total": round(100 * modelo["sq_residuos"] / modelo["sq_total"], 2)},
                {"Fonte de variação": "Total",
                 "Soma de quadrados": round(modelo["sq_total"], 4),
                 "% do total": 100.0},
            ]
        ),
        width="stretch", hide_index=True,
    )

    res = ma.residuos(modelo, x, y)
    st.pyplot(graficos.grafico_residuos(x, res, nome_x))
    st.caption(
        "Se o modelo linear for adequado, os resíduos devem se espalhar sem "
        "padrão em torno de zero, com dispersão constante. Um formato de funil "
        "(heterocedasticidade) ou uma curva indicam que a reta não captura toda "
        "a estrutura dos dados."
    )

    media_res = md.media(res)
    dp_res = md.desvio_padrao_amostral(res)
    st.caption(
        f"Média dos resíduos = {media_res:.2e} (teoricamente zero — o desvio é "
        f"apenas erro de ponto flutuante) · Desvio padrão dos resíduos = {dp_res:.4f}"
    )

    # --- Matriz de correlacoes -------------------------------------------
    st.markdown("### Matriz de correlações entre todas as variáveis numéricas")
    st.caption("Todos os coeficientes calculados por `minhastats.associacao.correlacao_pearson`.")

    if st.checkbox("Calcular a matriz completa", key="m5_matriz"):
        colunas = [c for c in variaveis if c in df.columns]
        matriz = []
        for a in colunas:
            linha = {"Variável": carregador.rotulo(a)}
            xa = carregador.coluna_como_lista(df, a)
            for b in colunas:
                xb = carregador.coluna_como_lista(df, b)
                try:
                    linha[carregador.rotulo(b)] = round(ma.correlacao_pearson(xa, xb), 3)
                except ValueError:
                    linha[carregador.rotulo(b)] = None
            matriz.append(linha)

        st.dataframe(
            pd.DataFrame(matriz).style.background_gradient(
                cmap="RdBu", vmin=-1, vmax=1,
                subset=[carregador.rotulo(c) for c in colunas],
            ),
            width="stretch", hide_index=True,
        )
