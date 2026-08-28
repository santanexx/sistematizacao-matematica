"""
Modulo 3 -- Probabilidade e Simulacao de Monte Carlo.

(a) Lei dos Grandes Numeros: moeda, dado e estimativa de pi.
(b) Teorema Central do Limite: medias amostrais de uma variavel do dataset.

Todos os parametros sao controlaveis pelo usuario, conforme o enunciado.
"""

import math

import pandas as pd
import streamlit as st

from app import carregador, graficos
from minhastats import descritiva as md
from minhastats import distribuicoes as mdist
from minhastats import frequencias as mf
from minhastats import simulacao as msim


def renderizar(df):
    st.header("🎲 Módulo 3 — Probabilidade e Simulação de Monte Carlo")

    aba_lgn, aba_tcl = st.tabs(
        ["(a) Lei dos Grandes Números", "(b) Teorema Central do Limite"]
    )
    with aba_lgn:
        _lei_dos_grandes_numeros()
    with aba_tcl:
        _teorema_central_do_limite(df)


# ---------------------------------------------------------------------------
# (a) Lei dos Grandes Numeros
# ---------------------------------------------------------------------------


def _lei_dos_grandes_numeros():
    st.markdown(
        """
A **Lei dos Grandes Números** garante que a frequência relativa de um evento
converge para a sua probabilidade teórica conforme o número de repetições
cresce:
"""
    )
    st.latex(
        r"\hat{p}_n = \frac{1}{n}\sum_{i=1}^{n} X_i "
        r"\;\xrightarrow[n \to \infty]{}\; p"
    )

    experimento = st.radio(
        "Experimento",
        ["Lançamento de moeda", "Lançamento de dado", "Estimativa de π"],
        horizontal=True,
        key="m3_experimento",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        n = st.select_slider(
            "Número de repetições (n)",
            options=[100, 500, 1000, 5000, 10000, 50000, 100000, 200000],
            value=10000,
            key="m3_n_lgn",
        )
    with c2:
        semente = st.number_input(
            "Semente aleatória", min_value=0, max_value=999999, value=42, step=1,
            help="Fixar a semente torna a simulação reproduzível.",
            key="m3_semente_lgn",
        )
    with c3:
        if experimento == "Lançamento de moeda":
            parametro = st.slider("Probabilidade de cara (p)", 0.0, 1.0, 0.5, 0.05,
                                  key="m3_p_moeda")
        elif experimento == "Lançamento de dado":
            parametro = st.slider("Número de faces", 2, 20, 6, key="m3_faces")
        else:
            parametro = None
            st.caption("π é estimado sorteando pontos no quadrado unitário.")

    if experimento == "Lançamento de moeda":
        _moeda(n, parametro, semente)
    elif experimento == "Lançamento de dado":
        _dado(n, parametro, semente)
    else:
        _pi(n, semente)


def _moeda(n, p, semente):
    r = msim.simular_moeda(n, p, semente=semente)

    c1, c2, c3 = st.columns(3)
    c1.metric("Frequência relativa observada", f"{r['frequencia_final']:.6f}")
    c2.metric("Probabilidade teórica", f"{r['valor_teorico']:.6f}")
    c3.metric("Erro absoluto", f"{r['erro_final']:.6f}")

    st.pyplot(
        graficos.convergencia(
            r["frequencias_acumuladas"], p,
            f"Convergência da frequência relativa de caras (n = {n:,})".replace(",", "."),
            "Frequência relativa acumulada",
        )
    )

    st.markdown("#### Erro em diferentes marcos de n")
    st.caption(
        "O erro não cai linearmente: ele decresce na ordem de 1/√n. "
        "Para reduzir o erro pela metade é preciso QUADRUPLICAR o número de repetições."
    )
    linhas = msim.convergencia_lgn(r["frequencias_acumuladas"], p)
    if linhas:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "n": l["n"],
                        "Estimativa": round(l["estimativa"], 6),
                        "Teórico": round(l["teorico"], 6),
                        "Erro absoluto": round(l["erro_absoluto"], 6),
                        "Ordem de 1/√n": round(l["erro_esperado_1_sobre_raiz_n"], 6),
                    }
                    for l in linhas
                ]
            ),
            width="stretch", hide_index=True,
        )

    # comparacao com a Binomial teorica
    st.markdown("#### Confronto com a distribuição Binomial teórica")
    esperado = n * p
    desvio = math.sqrt(n * p * (1 - p)) if 0 < p < 1 else 0.0
    st.info(
        f"O número de caras segue X ~ B(n={n}, p={p}). "
        f"O valor esperado é E[X] = n·p = **{esperado:.1f}** e o desvio padrão é "
        f"σ = √(n·p·(1−p)) = **{desvio:.2f}**. "
        f"A simulação obteve **{r['sucessos']}** caras — "
        f"{abs(r['sucessos'] - esperado) / desvio:.2f} desvios padrão do esperado."
        if desvio > 0 else
        f"Com p = {p} o resultado é determinístico: {r['sucessos']} caras."
    )


def _dado(n, faces, semente):
    r = msim.simular_dado(n, faces=faces, semente=semente)

    c1, c2, c3 = st.columns(3)
    c1.metric("Média observada", f"{r['media_final']:.6f}")
    c2.metric("Esperança teórica E[X]=(f+1)/2", f"{r['esperanca_teorica']:.6f}")
    c3.metric("Erro absoluto", f"{r['erro_final']:.6f}")

    st.pyplot(
        graficos.convergencia(
            r["medias_acumuladas"], r["esperanca_teorica"],
            f"Convergência da média de um dado de {faces} faces (n = {n:,})".replace(",", "."),
            "Média acumulada",
        )
    )

    st.markdown("#### Frequência relativa de cada face")
    st.caption(
        "Num dado honesto todas as faces devem convergir para 1/f. "
        "As barras observadas e esperadas se aproximam conforme n cresce."
    )
    st.pyplot(
        graficos.barras_comparativas(
            [str(i) for i in range(1, faces + 1)],
            r["frequencias_relativas"],
            [r["frequencia_teorica"]] * faces,
            "Frequência relativa por face: observado × teórico",
            "Frequência relativa",
        )
    )

    maior_desvio = max(
        abs(fr - r["frequencia_teorica"]) for fr in r["frequencias_relativas"]
    )
    st.info(
        f"O maior desvio entre a frequência observada de uma face e o valor "
        f"teórico 1/{faces} = {r['frequencia_teorica']:.6f} foi de "
        f"**{maior_desvio:.6f}**. A média acumulada calculada pelo nosso núcleo "
        f"é {r['media_final']:.6f} contra {r['esperanca_teorica']:.6f} previstos "
        f"pela teoria."
    )


def _pi(n, semente):
    r = msim.estimar_pi_monte_carlo(n, semente=semente)

    c1, c2, c3 = st.columns(3)
    c1.metric("π estimado", f"{r['pi_estimado']:.6f}")
    c2.metric("π verdadeiro", f"{r['pi_teorico']:.6f}")
    c3.metric("Erro absoluto", f"{r['erro']:.6f}")

    st.latex(r"\hat{\pi} = 4 \cdot \frac{\text{pontos dentro do quarto de círculo}}{n}")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.pyplot(graficos.dispersao_pi(r["pontos_x"], r["pontos_y"], r["dentro"],
                                        r["pi_estimado"]))
    with c2:
        st.pyplot(
            graficos.convergencia(
                r["estimativas_acumuladas"], r["pi_teorico"],
                "Convergência da estimativa de π", "Estimativa acumulada de π",
            )
        )
    st.caption("O gráfico de dispersão mostra os 3.000 primeiros pontos sorteados.")


# ---------------------------------------------------------------------------
# (b) Teorema Central do Limite
# ---------------------------------------------------------------------------


def _teorema_central_do_limite(df):
    st.markdown(
        """
O **Teorema Central do Limite** afirma que a distribuição das médias amostrais
se aproxima de uma Normal conforme o tamanho da amostra cresce — **qualquer que
seja a forma da distribuição original**:
"""
    )
    st.latex(
        r"\bar{X}_n \;\xrightarrow{d}\; N\!\left(\mu,\ \frac{\sigma^2}{n}\right)"
        r"\qquad \text{quando } n \to \infty"
    )
    st.caption(
        "Escolha uma variável bem assimétrica (como 'Aluguéis de usuários casuais') "
        "para ver o efeito de forma dramática."
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        variavel = st.selectbox(
            "Variável do dataset",
            list(carregador.VARIAVEIS_NUMERICAS.keys()),
            index=list(carregador.VARIAVEIS_NUMERICAS.keys()).index("casual"),
            format_func=carregador.rotulo,
            key="m3_var_tcl",
        )
    with c2:
        tamanho = st.select_slider(
            "Tamanho de cada amostra (n)",
            options=[2, 5, 10, 20, 30, 50, 100, 200, 500],
            value=30,
            key="m3_tamanho",
        )
    with c3:
        repeticoes = st.select_slider(
            "Número de repetições",
            options=[100, 500, 1000, 2000, 5000, 10000],
            value=2000,
            key="m3_repeticoes",
        )
    with c4:
        semente = st.number_input(
            "Semente aleatória", min_value=0, max_value=999999, value=2024, step=1,
            key="m3_semente_tcl",
        )

    dados = carregador.coluna_como_lista(df, variavel)
    nome = carregador.rotulo(variavel)

    resultado = msim.simular_tcl(dados, tamanho, repeticoes, semente=semente)
    medias = resultado["medias_amostrais"]

    # --- Comparacao teoria x simulacao ------------------------------------
    st.markdown("### Previsão do TCL × resultado da simulação")

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Grandeza": "Média",
                    "População (dataset)": round(resultado["mu_populacao"], 6),
                    "Previsto pelo TCL": round(resultado["mu_populacao"], 6),
                    "Observado na simulação": round(resultado["media_das_medias"], 6),
                },
                {
                    "Grandeza": "Desvio padrão",
                    "População (dataset)": round(resultado["sigma_populacao"], 6),
                    "Previsto pelo TCL": round(resultado["erro_padrao_teorico"], 6),
                    "Observado na simulação": round(resultado["erro_padrao_observado"], 6),
                },
            ]
        ),
        width="stretch", hide_index=True,
    )
    st.latex(r"\text{Erro padrão previsto} = \frac{\sigma}{\sqrt{n}} = "
             rf"\frac{{{resultado['sigma_populacao']:.4f}}}{{\sqrt{{{tamanho}}}}} = "
             rf"{resultado['erro_padrao_teorico']:.4f}")

    erro_relativo = (
        abs(resultado["erro_padrao_observado"] - resultado["erro_padrao_teorico"])
        / resultado["erro_padrao_teorico"] * 100
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Erro padrão teórico σ/√n", f"{resultado['erro_padrao_teorico']:.4f}")
    c2.metric("Erro padrão observado", f"{resultado['erro_padrao_observado']:.4f}")
    c3.metric("Discrepância", f"{erro_relativo:.2f}%")

    # --- Assimetria: populacao x medias amostrais -------------------------
    assimetria_populacao = md.assimetria_momento(dados)
    assimetria_medias = md.assimetria_momento(medias)
    curtose_medias = md.curtose_momento(medias)

    c1, c2, c3 = st.columns(3)
    c1.metric("Assimetria da população", f"{assimetria_populacao:.4f}")
    c2.metric("Assimetria das médias", f"{assimetria_medias:.4f}",
              delta=f"{assimetria_medias - assimetria_populacao:.4f}")
    c3.metric("Curtose das médias", f"{curtose_medias:.4f}")

    # --- Graficos ---------------------------------------------------------
    st.markdown("### Distribuição original × distribuição das médias amostrais")

    k = mf.regra_sturges(len(dados))
    st.pyplot(
        graficos.histograma(
            mf.tabela_frequencias_continua(dados, k=k),
            f"População: distribuição original de {nome} (n = {len(dados)})",
            nome,
        )
    )

    k_medias = mf.regra_sturges(len(medias))
    linhas_medias = mf.tabela_frequencias_continua(medias, k=k_medias)

    # Curva Normal teorica prevista pelo TCL, em escala de frequencia:
    # multiplicamos a densidade pela largura da classe e por n.
    largura = linhas_medias[0]["ls"] - linhas_medias[0]["li"]
    mu = resultado["mu_populacao"]
    sigma_medias = resultado["erro_padrao_teorico"]
    x_min = min(medias)
    x_max = max(medias)
    passo = (x_max - x_min) / 300 if x_max > x_min else 1.0
    xs = [x_min + i * passo for i in range(301)]
    ys = [mdist.normal_pdf(v, mu, sigma_medias) * largura * len(medias) for v in xs]

    st.pyplot(
        graficos.histograma(
            linhas_medias,
            f"Distribuição de {repeticoes} médias amostrais (cada uma de n = {tamanho})",
            f"Média amostral de {nome}",
            curva=(xs, ys),
            rotulo_curva=f"Normal teórica N({mu:.2f}, {sigma_medias:.2f}²) prevista pelo TCL",
        )
    )

    # --- Interpretacao automatica -----------------------------------------
    st.markdown("### 🧠 Interpretação automática")

    if abs(assimetria_medias) < 0.15:
        veredito = (
            "A distribuição das médias amostrais já é praticamente SIMÉTRICA — "
            "a aproximação Normal do TCL está válida com este tamanho de amostra."
        )
    elif abs(assimetria_medias) < abs(assimetria_populacao) / 2:
        veredito = (
            "A assimetria caiu bastante em relação à população, mas ainda é "
            "perceptível. Aumente o tamanho da amostra para ver a curva "
            "terminar de virar um sino."
        )
    else:
        veredito = (
            "Com este tamanho de amostra a assimetria original ainda domina. "
            "O TCL é um resultado ASSINTÓTICO: aumente n para ver o efeito."
        )

    reducao = (
        (1 - abs(assimetria_medias) / abs(assimetria_populacao)) * 100
        if assimetria_populacao else 0.0
    )

    st.info(
        f"A variável **{nome}** tem assimetria populacional de "
        f"{assimetria_populacao:.4f}. Sorteando {repeticoes} amostras de tamanho "
        f"{tamanho}, a assimetria da distribuição das médias caiu para "
        f"{assimetria_medias:.4f} — uma redução de {reducao:.1f}%. "
        f"O desvio padrão das médias observado ({resultado['erro_padrao_observado']:.4f}) "
        f"difere apenas {erro_relativo:.2f}% do valor σ/√n = "
        f"{resultado['erro_padrao_teorico']:.4f} previsto pelo teorema. {veredito}"
    )
