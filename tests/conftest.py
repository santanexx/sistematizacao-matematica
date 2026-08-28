"""
Configuracao compartilhada dos testes de validacao.

Estrategia de validacao (Modulo 1, criterio 1 do barema)
--------------------------------------------------------
Cada funcao de ``minhastats`` e comparada com uma referencia consolidada
(NumPy, SciPy ou ``statistics``) em TRES frentes:

1. **Casos fixos**  -- amostras pequenas cujo resultado sabemos calcular a
   mao, garantindo que a formula esta certa e nao apenas "igual a de
   alguem".
2. **Dataset real** -- as proprias colunas do Bike Sharing, com 17.379
   registros, onde erros de acumulacao numerica apareceriam.
3. **Dados aleatorios** -- amostras geradas com semente fixa em varias
   escalas (valores minusculos, gigantes, negativos), para exercitar o
   comportamento de ponto flutuante.

Tolerancia numerica
-------------------
Adotamos ``rel=1e-9`` (nove casas significativas) nas comparacoes.

Justificativa: o ``float`` de 64 bits (IEEE 754) carrega ~15-16 digitos
decimais significativos, mas cada operacao introduz um erro relativo de
ate ``2**-53 ~ 1.1e-16``. Somando n = 17.379 parcelas, o erro acumulado
no pior caso cresce com n, chegando a ordem de ``1e-12``. Alem disso,
NumPy usa somatorio PAREADO (pairwise summation) e instrucoes vetoriais
SIMD, o que muda a ORDEM das operacoes -- e a soma em ponto flutuante nao
e associativa, entao um resultado ligeiramente diferente do nosso
somatorio sequencial e esperado e correto.

``1e-9`` fica confortavelmente acima do erro numerico esperado (~1e-12) e
muito abaixo de qualquer erro de FORMULA, que apareceria ja na segunda ou
terceira casa. Onde a tolerancia precisou ser diferente, o teste diz o
porque no proprio codigo.
"""

import csv
import math
import os
import random

import pytest

# Tolerancia relativa padrao de todo o projeto (ver justificativa acima)
TOL = 1e-9

CAMINHO_DADOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hour.csv"
)


@pytest.fixture(scope="session")
def dataset():
    """Carrega o hour.csv com o modulo csv da biblioteca padrao.

    Nao usamos pandas aqui de proposito: os testes devem depender do
    minimo possivel para que uma falha aponte para o nucleo, e nao para o
    carregamento.
    """
    colunas = {}
    with open(CAMINHO_DADOS, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for nome in leitor.fieldnames:
            colunas[nome] = []
        for linha in leitor:
            for nome, valor in linha.items():
                colunas[nome].append(valor)
    return colunas


@pytest.fixture(scope="session")
def coluna_numerica(dataset):
    """Devolve uma funcao que converte uma coluna do dataset em list[float]."""

    def _obter(nome):
        return [float(v) for v in dataset[nome]]

    return _obter


@pytest.fixture(scope="session")
def amostras_aleatorias():
    """Amostras sinteticas com semente fixa, em escalas bem diferentes.

    Cada cenario ataca um risco numerico distinto -- ver o comentario de
    cada entrada.
    """
    rng = random.Random(42)
    return {
        # caso base, bem comportado
        "normal": [rng.gauss(100, 15) for _ in range(1000)],
        # valores enormes: expoe cancelamento catastrofico na "formula de maquina"
        "grande_escala": [rng.gauss(1e6, 1e4) for _ in range(500)],
        # valores minusculos: expoe perda de precisao por underflow
        "pequena_escala": [rng.gauss(1e-6, 1e-8) for _ in range(500)],
        # assimetrica e estritamente positiva: usada tambem na Exponencial
        "assimetrica": [rng.expovariate(0.5) for _ in range(800)],
        # discreta com muitos empates: exercita moda e percentis
        "discreta": [float(rng.randint(0, 9)) for _ in range(600)],
        # negativos e positivos misturados
        "mista": [rng.uniform(-500, 500) for _ in range(400)],
        # amostra minima valida
        "minima": [3.0, 7.0],
    }


@pytest.fixture(scope="session")
def casos_fixos():
    """Amostras pequenas com resultados conferiveis a mao."""
    return {
        # media 5, mediana 4.5, moda 4, var_pop 4, var_am 32/7
        "manual": [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0],
        "impar": [1.0, 3.0, 5.0, 7.0, 9.0],
        "par": [10.0, 20.0, 30.0, 40.0],
        "constante": [7.0, 7.0, 7.0, 7.0, 7.0],
        "bimodal": [1.0, 1.0, 2.0, 3.0, 3.0, 4.0],
        "amodal": [1.0, 2.0, 3.0, 4.0, 5.0],
    }


def quase_igual(obtido, esperado, tol=TOL, contexto=""):
    """Assercao com mensagem de erro rica.

    Quando falha, mostra os dois valores e o erro relativo -- assim da
    para distinguir "errei a formula" (erro grande) de "acumulei ruido de
    ponto flutuante" (erro ~1e-15).
    """
    if math.isnan(esperado) and math.isnan(obtido):
        return
    assert obtido == pytest.approx(esperado, rel=tol, abs=1e-12), (
        f"{contexto}\n"
        f"  minhastats : {obtido!r}\n"
        f"  referencia : {esperado!r}\n"
        f"  erro rel.  : {abs(obtido - esperado) / abs(esperado) if esperado else float('inf'):.3e}\n"
        f"  tolerancia : {tol:.1e}"
    )
