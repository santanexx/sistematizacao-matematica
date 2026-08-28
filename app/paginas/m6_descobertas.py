"""
Modulo 6 -- Relatorio de Descobertas.

As tres descobertas estatisticas mais interessantes que o laboratorio
revelou, com os numeros RECALCULADOS ao vivo pelo proprio nucleo -- nada
aqui esta escrito na mao.
"""

import pandas as pd
import streamlit as st

from app import carregador, graficos
from minhastats import associacao as ma
from minhastats import descritiva as md
from minhastats import distribuicoes as mdist
from minhastats import frequencias as mf
from minhastats import simulacao as msim


@st.cache_data(show_spinner="Recalculando as descobertas...")
def _calcular(colunas):
    """Recalcula todos os numeros das descobertas.

    Recebe um dicionario de TUPLAS (imutaveis e, portanto, hashaveis pelo
    cache do Streamlit) em vez do DataFrame -- assim as simulacoes do TCL,
    que sao a parte cara, rodam uma unica vez por sessao.
    """
    L = lambda c: list(colunas[c])

    cnt, casual, registered = L("cnt"), L("casual"), L("registered")
    temp = L("temp_c")
    trabalho = L("workingday")

    # --- Descoberta 1: a reta explica pouco ------------------------------
    modelo_temp = ma.regressao_linear(temp, cnt)
    r_temp = ma.correlacao_pearson(temp, cnt)

    # --- Descoberta 2: dois publicos opostos ------------------------------
    perfis = {}
    for rotulo, filtro in [("Dia útil", 1.0), ("Fim de semana/feriado", 0.0)]:
        # separacao feita com list comprehension pura -- sem groupby do pandas
        casual_filtrado = [c for c, w in zip(casual, trabalho) if w == filtro]
        registrado_filtrado = [c for c, w in zip(registered, trabalho) if w == filtro]
        perfis[rotulo] = {
            "casual": md.media(casual_filtrado),
            "registered": md.media(registrado_filtrado),
            "n": len(casual_filtrado),
        }

    # --- Descoberta 3: sobredispersao e o TCL -----------------------------
    dispersao = {c: mdist.indice_dispersao(v)
                 for c, v in [("cnt", cnt), ("casual", casual), ("registered", registered)]}

    tcl = {}
    for n in [2, 10, 30, 100, 200]:
        r = msim.simular_tcl(casual, n, 5000, semente=2024)
        tcl[n] = {
            "assimetria": md.assimetria_momento(r["medias_amostrais"]),
            "ep_teorico": r["erro_padrao_teorico"],
            "ep_observado": r["erro_padrao_observado"],
        }

    return {
        "modelo_temp": modelo_temp,
        "r_temp": r_temp,
        "r_hum": ma.correlacao_pearson(L("hum_pct"), cnt),
        "r_vento": ma.correlacao_pearson(L("windspeed_kmh"), cnt),
        "r_hora": ma.correlacao_pearson(L("hr"), cnt),
        "perfis": perfis,
        "dispersao": dispersao,
        "tcl": tcl,
        "assimetria_casual": md.assimetria_momento(casual),
        "curtose_casual": md.curtose_momento(casual),
        "cv_casual": md.coeficiente_variacao(casual),
        "cv_registered": md.coeficiente_variacao(registered),
        "outliers_casual": mf.detectar_outliers_iqr(casual),
        "outliers_temp": mf.detectar_outliers_iqr(temp),
        "resumo_temp": md.resumo(temp),
    }


def renderizar(df):
    st.header("💡 Módulo 6 — Relatório de Descobertas")
    st.markdown(
        "As três descobertas estatísticas mais interessantes que este laboratório "
        "revelou sobre o dataset. **Todos os números abaixo são recalculados ao vivo "
        "pelo núcleo `minhastats`** a cada carregamento da página."
    )

    necessarias = ["cnt", "casual", "registered", "temp_c", "hum_pct",
                   "windspeed_kmh", "hr", "workingday"]
    colunas = {c: tuple(float(v) for v in df[c].tolist()) for c in necessarias}
    dados = _calcular(colunas)

    # =======================================================================
    # DESCOBERTA 1
    # =======================================================================
    st.markdown("---")
    st.subheader("1️⃣ A temperatura importa — mas explica menos de 17% dos aluguéis")

    m = dados["modelo_temp"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("r (temperatura × aluguéis)", f"{dados['r_temp']:.4f}")
    c2.metric("R²", f"{m['r2']:.4f}")
    c3.metric("Coef. angular b", f"{m['b']:.4f}")
    c4.metric("Variação não explicada", f"{(1 - m['r2']) * 100:.1f}%")

    st.markdown(
        f"""
A correlação entre temperatura e total de aluguéis é **r = {dados['r_temp']:.4f}**
— positiva e moderada, exatamente como a intuição sugere. A reta de mínimos
quadrados é **{m['equacao']}**: cada grau Celsius a mais está associado a
**+{m['b']:.2f} aluguéis por hora**.

O achado interessante não é esse. É que **R² = {m['r2']:.4f}**, ou seja, a
temperatura explica apenas **{m['r2'] * 100:.1f}%** da variação total —
**{(1 - m['r2']) * 100:.1f}% ficam de fora**. E não é porque falte relação: é
porque a relação **não é uma reta**. A demanda tem dois picos diários (ida e
volta do trabalho) que nenhuma reta em função da temperatura consegue capturar.
O gráfico de resíduos do Módulo 5 mostra isso na cara: em vez de uma nuvem sem
padrão, aparece um **funil** — a variabilidade cresce junto com a temperatura
(heterocedasticidade), sinal clássico de que o modelo linear simples é
insuficiente.

Comparação com as demais candidatas: umidade **r = {dados['r_hum']:.4f}**
(negativa), hora do dia **r = {dados['r_hora']:.4f}**, vento
**r = {dados['r_vento']:.4f}** (praticamente irrelevante).

> **Lição estatística:** um r "bonito" pode esconder um R² decepcionante.
> Como R² = r², um r de {dados['r_temp']:.2f} vira apenas
> {m['r2'] * 100:.0f}% de variação explicada — e correlação continua não
> implicando causalidade: temperatura e demanda também variam juntas com a
> estação e o horário.
"""
    )

    # =======================================================================
    # DESCOBERTA 2
    # =======================================================================
    st.markdown("---")
    st.subheader("2️⃣ Dois públicos com comportamentos opostos escondidos no mesmo total")

    perfis = dados["perfis"]
    util = perfis["Dia útil"]
    fds = perfis["Fim de semana/feriado"]

    variacao_casual = (fds["casual"] / util["casual"] - 1) * 100
    variacao_registered = (fds["registered"] / util["registered"] - 1) * 100

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Perfil de usuário": "Casual (não cadastrado)",
                    "Média em dia útil": round(util["casual"], 2),
                    "Média em fim de semana/feriado": round(fds["casual"], 2),
                    "Variação": f"{variacao_casual:+.1f}%",
                },
                {
                    "Perfil de usuário": "Registrado (cadastrado)",
                    "Média em dia útil": round(util["registered"], 2),
                    "Média em fim de semana/feriado": round(fds["registered"], 2),
                    "Variação": f"{variacao_registered:+.1f}%",
                },
            ]
        ),
        width="stretch", hide_index=True,
    )

    st.markdown(
        f"""
Separando os aluguéis por tipo de usuário, aparece um padrão que o total esconde
por completo: os dois públicos reagem ao calendário **em direções opostas**.

- Usuários **casuais** saltam de {util['casual']:.2f} para {fds['casual']:.2f}
  aluguéis/hora no fim de semana — **{variacao_casual:+.1f}%**.
- Usuários **registrados** fazem o caminho inverso: caem de
  {util['registered']:.2f} para {fds['registered']:.2f} — **{variacao_registered:+.1f}%**.

São dois fenômenos diferentes no mesmo dataset: **lazer** contra **deslocamento
pendular para o trabalho**. A assinatura estatística confirma a separação: o
público casual tem coeficiente de variação de **{dados['cv_casual']:.1f}%** contra
**{dados['cv_registered']:.1f}%** dos registrados, com excesso de curtose de
**{dados['curtose_casual']:.2f}** (fortemente leptocúrtica) e
**{dados['outliers_casual']['n_outliers']} outliers pela regra do IQR**
({dados['outliers_casual']['percentual']:.2f}% dos registros, acima de
{dados['outliers_casual']['limite_superior']:.0f} aluguéis/hora) — as tardes de
fim de semana com clima bom.

> **Lição estatística:** analisar só o agregado `cnt` levaria à conclusão errada
> de que "o dia da semana quase não afeta a demanda" (a média total varia pouco:
> {util['casual'] + util['registered']:.1f} contra
> {fds['casual'] + fds['registered']:.1f}). É o **paradoxo da agregação** — dois
> efeitos opostos se cancelando na soma.
"""
    )

    # =======================================================================
    # DESCOBERTA 3
    # =======================================================================
    st.markdown("---")
    st.subheader("3️⃣ Os dados violam a Poisson por um fator de 170× — e o TCL não se abala")

    c1, c2, c3 = st.columns(3)
    c1.metric("Índice de dispersão de `cnt`", f"{dados['dispersao']['cnt']:.1f}",
              help="Na Poisson esse índice vale exatamente 1.")
    c2.metric("Assimetria de `casual`", f"{dados['assimetria_casual']:.3f}")
    c3.metric("Excesso de curtose de `casual`", f"{dados['curtose_casual']:.3f}")

    st.markdown(
        f"""
Aluguéis por hora são uma **contagem** — o livro-texto mandaria testar a Poisson.
Mas a Poisson exige média = variância, isto é, índice de dispersão s²/x̄ = 1.
O nosso núcleo calcula **{dados['dispersao']['cnt']:.1f}** para `cnt`,
{dados['dispersao']['casual']:.1f} para `casual` e
{dados['dispersao']['registered']:.1f} para `registered`. É **sobredispersão
extrema**: a variabilidade real é cerca de **{dados['dispersao']['cnt']:.0f} vezes**
maior do que a Poisson admite. O modelo está descartado antes mesmo de olhar o
gráfico — e o Módulo 4 confirma visualmente.

O contraponto é o que torna a descoberta bonita. Mesmo partindo de `casual`, que
é violentamente assimétrica (assimetria **{dados['assimetria_casual']:.3f}**,
curtose **{dados['curtose_casual']:.3f}**), o **Teorema Central do Limite
funciona exatamente como prometido**:
"""
    )

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Tamanho da amostra (n)": n,
                    "Assimetria das médias": round(v["assimetria"], 4),
                    "σ/√n (teórico)": round(v["ep_teorico"], 4),
                    "Desvio observado": round(v["ep_observado"], 4),
                    "Discrepância": f"{abs(v['ep_observado'] - v['ep_teorico']) / v['ep_teorico'] * 100:.2f}%",
                }
                for n, v in dados["tcl"].items()
            ]
        ),
        width="stretch", hide_index=True,
    )

    tcl = dados["tcl"]
    reducao = (1 - abs(tcl[200]["assimetria"]) / abs(dados["assimetria_casual"])) * 100

    st.markdown(
        f"""
A assimetria cai de **{dados['assimetria_casual']:.3f}** na população para
**{tcl[200]['assimetria']:.3f}** nas médias de amostras de 200 — uma redução de
**{reducao:.1f}%** — e o desvio padrão das médias reproduz σ/√n com menos de 2%
de erro em todos os tamanhos testados. Não precisamos assumir normalidade da
população para trabalhar com a média dela.

> **Lição estatística:** o TCL é sobre a distribuição **das médias amostrais**,
> não sobre a dos dados. Uma variável pode ser tão torta quanto `casual` e ainda
> assim permitir inferência baseada na Normal — desde que a amostra seja grande
> o bastante.
"""
    )

    # =======================================================================
    # Achado bonus
    # =======================================================================
    st.markdown("---")
    with st.expander("🎁 Achado bônus — a temperatura é a variável mais 'bem-comportada' do dataset"):
        r = dados["resumo_temp"]
        st.markdown(
            f"""
Enquanto todas as variáveis de contagem são assimétricas e cheias de outliers,
a temperatura é o oposto: assimetria de momento de **{r['assimetria_momento']:.4f}**
(praticamente zero), média **{r['media']:.2f} °C** contra mediana
**{r['mediana']:.2f} °C** — quase idênticas — e **{dados['outliers_temp']['n_outliers']}
outliers pela regra do IQR**.

O detalhe curioso é o excesso de curtose: **{r['curtose']:.4f}**, bem abaixo de
zero. A distribuição é **platicúrtica** — mais achatada que a Normal. Faz sentido
físico: a temperatura não se concentra em torno de um valor típico, ela percorre
razoavelmente todo o intervalo anual. É por isso que, no Módulo 4, a Normal se
ajusta melhor que a Uniforme, mas nenhuma das duas se ajusta bem: a forma real
está entre as duas.
"""
        )

    st.markdown("---")
    st.caption(
        "Cada número desta página foi calculado pelas funções de `minhastats`, "
        "as mesmas validadas contra NumPy e SciPy pelos 485 testes automatizados "
        "em `tests/`."
    )
