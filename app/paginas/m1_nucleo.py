"""
Modulo 1 -- Nucleo Estatistico Proprio.

O Modulo 1 e uma BIBLIOTECA (minhastats/), nao uma tela. Esta pagina e
uma janela para dentro dela: o que implementa, o codigo-fonte de cada
funcao, um calculo ao vivo e a execucao da validacao contra NumPy/SciPy.

Regra de ouro preservada: esta pagina NAO importa numpy nem scipy. A
comparacao com as bibliotecas de referencia acontece dentro dos testes
automatizados, que a pagina executa em subprocesso e cujo resultado exibe.
"""

import ast
import inspect
import os
import subprocess
import sys

import pandas as pd
import streamlit as st

import minhastats
from app import carregador
from minhastats import associacao as ma
from minhastats import descritiva as md

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Medidas exigidas pelo enunciado -> funcao que a implementa -> formula
MEDIDAS_EXIGIDAS = [
    ("Média", "media", r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i"),
    ("Mediana", "mediana",
     r"Md = x_{(\frac{n+1}{2})} \text{ (n ímpar)} \quad\text{ou}\quad "
     r"\tfrac{1}{2}\left[x_{(\frac{n}{2})} + x_{(\frac{n}{2}+1)}\right] \text{ (n par)}"),
    ("Moda", "moda", r"Mo = \arg\max_x f(x)"),
    ("Amplitude", "amplitude", r"A = x_{\max} - x_{\min}"),
    ("Variância populacional", "variancia_populacional",
     r"\sigma^2 = \frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2"),
    ("Variância amostral", "variancia_amostral",
     r"s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2"),
    ("Desvio padrão populacional", "desvio_padrao_populacional", r"\sigma = \sqrt{\sigma^2}"),
    ("Desvio padrão amostral", "desvio_padrao_amostral", r"s = \sqrt{s^2}"),
    ("Percentil / quartis", "percentil",
     r"h = \tfrac{p}{100}(n-1), \quad P_p = x_{(\lfloor h\rfloor)} + (h - \lfloor h\rfloor)"
     r"\left[x_{(\lfloor h\rfloor+1)} - x_{(\lfloor h\rfloor)}\right]"),
    ("Coeficiente de variação", "coeficiente_variacao", r"CV = \frac{s}{|\bar{x}|}\times 100\%"),
    ("Covariância", "covariancia_amostral",
     r"s_{xy} = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})"),
    ("Correlação de Pearson", "correlacao_pearson",
     r"r = \frac{\sum (x_i-\bar{x})(y_i-\bar{y})}"
     r"{\sqrt{\sum (x_i-\bar{x})^2}\sqrt{\sum (y_i-\bar{y})^2}}"),
]

ARQUIVOS_TESTE_NUCLEO = [
    "tests/test_descritiva.py",
    "tests/test_associacao.py",
    "tests/test_frequencias.py",
    "tests/test_distribuicoes.py",
    "tests/test_simulacao.py",
    "tests/test_regra_de_ouro.py",
]


def _imports_do_nucleo():
    """Le os arquivos de minhastats/ e devolve os modulos que eles importam.

    E a mesma verificacao que tests/test_regra_de_ouro.py faz -- aqui ela
    aparece na tela, para o usuario conferir com os proprios olhos.
    """
    pasta = os.path.join(RAIZ, "minhastats")
    resultado = {}
    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".py"):
            continue
        with open(os.path.join(pasta, nome), encoding="utf-8") as f:
            arvore = ast.parse(f.read())
        modulos = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                modulos.update(a.name.split(".")[0] for a in no.names)
            elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
                modulos.add(no.module.split(".")[0])
        resultado[nome] = sorted(modulos) or ["(nenhum)"]
    return resultado


def _funcoes_publicas():
    """Todas as funcoes exportadas pelo pacote, agrupadas por modulo."""
    grupos = {}
    for nome in minhastats.__all__:
        obj = getattr(minhastats, nome)
        modulo = obj.__module__.split(".")[-1]
        grupos.setdefault(modulo, []).append(nome)
    return grupos


def renderizar(df):
    st.header("Módulo 1 — Núcleo Estatístico Próprio")

    st.markdown(
        """
O Módulo 1 não é uma tela: é a **biblioteca** `minhastats/`, que alimenta todos
os outros módulos. Esta página é uma janela para dentro dela — o que implementa,
o código de cada função, um cálculo ao vivo e a validação contra NumPy/SciPy.
"""
    )

    # --- Regra de ouro, verificada ao vivo ---------------------------------
    st.markdown("### Regra de ouro: o que o núcleo importa")
    st.caption(
        "Lido agora do código-fonte com o módulo `ast`. Se aparecesse `numpy`, "
        "`scipy`, `pandas` ou `statistics` aqui, a regra estaria quebrada."
    )
    imports = _imports_do_nucleo()
    st.dataframe(
        pd.DataFrame(
            [{"Arquivo": f"minhastats/{arq}", "Importa": ", ".join(mods)}
             for arq, mods in imports.items()]
        ),
        width="stretch", hide_index=True,
    )
    externos = {m for mods in imports.values() for m in mods} - {"math", "random", "(nenhum)"}
    if externos:
        st.error(f"Dependência externa encontrada no núcleo: {sorted(externos)}")
    else:
        st.success("Apenas `math` e `random` da biblioteca padrão. Nenhuma dependência externa.")

    # --- Medidas exigidas ---------------------------------------------------
    st.markdown("### As medidas exigidas pelo enunciado e suas fórmulas")

    grupos = _funcoes_publicas()
    total = sum(len(v) for v in grupos.values())
    st.caption(
        f"O pacote exporta {total} funções em {len(grupos)} módulos. "
        f"Abaixo, as exigidas explicitamente pelo enunciado."
    )

    for rotulo, funcao, formula in MEDIDAS_EXIGIDAS:
        c1, c2 = st.columns([1, 2.2])
        with c1:
            st.markdown(f"**{rotulo}**  \n`minhastats.{funcao}()`")
        with c2:
            st.latex(formula)

    with st.expander(f"Ver todas as {total} funções do pacote, por módulo"):
        for modulo, nomes in grupos.items():
            st.markdown(f"**`{modulo}.py`** — " + ", ".join(f"`{n}`" for n in nomes))

    # --- Calculo ao vivo ----------------------------------------------------
    st.markdown("### Cálculo ao vivo")
    st.caption("Cada linha chama a função correspondente diretamente — sem passar por nenhum resumo.")

    c1, c2 = st.columns(2)
    with c1:
        var_x = st.selectbox(
            "Variável X", list(carregador.VARIAVEIS_NUMERICAS.keys()),
            index=list(carregador.VARIAVEIS_NUMERICAS.keys()).index("temp_c"),
            format_func=carregador.rotulo, key="m1_x",
        )
    with c2:
        var_y = st.selectbox(
            "Variável Y (para covariância e correlação)",
            list(carregador.VARIAVEIS_NUMERICAS.keys()),
            index=list(carregador.VARIAVEIS_NUMERICAS.keys()).index("cnt"),
            format_func=carregador.rotulo, key="m1_y",
        )

    x = carregador.coluna_como_lista(df, var_x)
    y = carregador.coluna_como_lista(df, var_y)

    def _fmt(v):
        if isinstance(v, list):
            return ", ".join(f"{m:.6g}" for m in v[:5]) or "amodal"
        return f"{v:.10g}"

    linhas = [
        ("media(x)", md.media(x)),
        ("mediana(x)", md.mediana(x)),
        ("moda(x)", md.moda(x)),
        ("amplitude(x)", md.amplitude(x)),
        ("variancia_populacional(x)", md.variancia_populacional(x)),
        ("variancia_amostral(x)", md.variancia_amostral(x)),
        ("desvio_padrao_populacional(x)", md.desvio_padrao_populacional(x)),
        ("desvio_padrao_amostral(x)", md.desvio_padrao_amostral(x)),
        ("percentil(x, 25)  — Q1", md.percentil(x, 25)),
        ("percentil(x, 50)  — Q2", md.percentil(x, 50)),
        ("percentil(x, 75)  — Q3", md.percentil(x, 75)),
        ("coeficiente_variacao(x)  [%]", md.coeficiente_variacao(x)),
        ("covariancia_amostral(x, y)", ma.covariancia_amostral(x, y)),
        ("correlacao_pearson(x, y)", ma.correlacao_pearson(x, y)),
    ]
    st.dataframe(
        pd.DataFrame([{"Chamada": f"minhastats.{c}", "Resultado": _fmt(v)} for c, v in linhas]),
        width="stretch", hide_index=True,
    )

    # --- Codigo-fonte -------------------------------------------------------
    st.markdown("### Código-fonte")
    st.caption("O código real que produziu os números acima, lido do pacote com `inspect.getsource`.")

    todas = [n for nomes in grupos.values() for n in nomes]
    escolhida = st.selectbox(
        "Função", todas,
        index=todas.index("variancia_amostral"),
        key="m1_fonte",
    )
    fonte = inspect.getsource(getattr(minhastats, escolhida))
    modulo_origem = getattr(minhastats, escolhida).__module__.replace(".", "/") + ".py"
    st.caption(f"`{modulo_origem}`")
    st.code(fonte, language="python", line_numbers=True)

    # --- Validacao ----------------------------------------------------------
    st.markdown("### Validação contra NumPy, SciPy e `statistics`")
    st.markdown(
        """
Cada função é comparada com a referência em três frentes — casos calculados à
mão, o dataset real e amostras aleatórias com semente fixa — com **tolerância
relativa de 10⁻⁹**. A justificativa numérica está em `tests/conftest.py`: o
erro acumulado esperado com n = 17.379 é da ordem de 10⁻¹², e o NumPy usa
somatório pareado (ordem de operações diferente da nossa), enquanto um erro de
fórmula apareceria já na segunda casa decimal.

A comparação acontece **dentro dos testes**, não nesta página — assim a
aplicação continua sem importar `numpy`. O botão abaixo executa a suíte do
núcleo em um processo separado e mostra o resultado.
"""
    )

    if st.button("Rodar os testes de validação agora", key="m1_rodar"):
        with st.spinner("Executando pytest..."):
            comando = [
                sys.executable, "-m", "pytest", *ARQUIVOS_TESTE_NUCLEO,
                "-q", "--no-header", "-p", "no:cacheprovider",
            ]
            try:
                proc = subprocess.run(
                    comando, cwd=RAIZ, capture_output=True, text=True, timeout=180
                )
                saida = proc.stdout + proc.stderr
                resumo = [l for l in saida.splitlines() if "passed" in l or "failed" in l]
                if proc.returncode == 0:
                    st.success(resumo[-1] if resumo else "Todos os testes passaram.")
                else:
                    st.error(resumo[-1] if resumo else "Houve falhas.")
                with st.expander("Saída completa do pytest"):
                    st.code(saida, language="text")
            except subprocess.TimeoutExpired:
                st.error("A execução excedeu 180 s.")
            except FileNotFoundError:
                st.error("pytest não encontrado no interpretador atual.")
