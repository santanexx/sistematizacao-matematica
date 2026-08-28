"""
app.carregador
==============

Carregamento e catalogo do dataset. E a UNICA parte da aplicacao que fala
com o pandas -- e mesmo aqui o pandas so LE e ORGANIZA os dados: nenhuma
medida estatistica exibida ao usuario passa por ele.

Dataset: Bike Sharing Dataset (UCI Machine Learning Repository)
https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
"""

import os

import pandas as pd
import streamlit as st

CAMINHO_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hour.csv"
)

URL_DATASET = "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset"

# ---------------------------------------------------------------------------
# Catalogo das variaveis
# ---------------------------------------------------------------------------
#
# O dataset original vem com as variaveis meteorologicas NORMALIZADAS entre
# 0 e 1. Isso e comodo para modelos, mas pessimo para interpretar: dizer
# que "a temperatura media e 0,497" nao significa nada para quem le o
# relatorio. Por isso criamos versoes em unidades reais aplicando a
# transformacao inversa documentada pelos autores do dataset:
#
#     temp      = t / 41       ->  t      = temp * 41        (graus Celsius)
#     atemp     = t / 50       ->  t      = atemp * 50       (graus Celsius)
#     hum       = h / 100      ->  h      = hum * 100        (percentual)
#     windspeed = v / 67       ->  v      = windspeed * 67   (km/h)
#
# As colunas originais continuam disponiveis -- as derivadas sao apenas
# uma reescala LINEAR, entao correlacao e R^2 sao identicos nas duas.

VARIAVEIS_NUMERICAS = {
    "temp_c": {
        "rotulo": "Temperatura (°C)",
        "descricao": "Temperatura do ar em graus Celsius (temp x 41).",
        "unidade": "°C",
    },
    "atemp_c": {
        "rotulo": "Sensação térmica (°C)",
        "descricao": "Temperatura aparente em graus Celsius (atemp x 50).",
        "unidade": "°C",
    },
    "hum_pct": {
        "rotulo": "Umidade relativa (%)",
        "descricao": "Umidade relativa do ar em percentual (hum x 100).",
        "unidade": "%",
    },
    "windspeed_kmh": {
        "rotulo": "Velocidade do vento (km/h)",
        "descricao": "Velocidade do vento em km/h (windspeed x 67).",
        "unidade": "km/h",
    },
    "casual": {
        "rotulo": "Aluguéis de usuários casuais",
        "descricao": "Número de aluguéis por usuários não cadastrados na hora.",
        "unidade": "aluguéis/h",
    },
    "registered": {
        "rotulo": "Aluguéis de usuários registrados",
        "descricao": "Número de aluguéis por usuários cadastrados na hora.",
        "unidade": "aluguéis/h",
    },
    "cnt": {
        "rotulo": "Total de aluguéis",
        "descricao": "Total de bicicletas alugadas na hora (casual + registered).",
        "unidade": "aluguéis/h",
    },
    "hr": {
        "rotulo": "Hora do dia (0-23)",
        "descricao": "Hora do registro, de 0 a 23.",
        "unidade": "h",
    },
    "temp": {
        "rotulo": "Temperatura normalizada (0-1)",
        "descricao": "Coluna original do dataset, normalizada entre 0 e 1.",
        "unidade": "",
    },
    "hum": {
        "rotulo": "Umidade normalizada (0-1)",
        "descricao": "Coluna original do dataset, normalizada entre 0 e 1.",
        "unidade": "",
    },
}

VARIAVEIS_CATEGORICAS = {
    "estacao": {
        "rotulo": "Estação do ano",
        "descricao": "Inverno, Primavera, Verão ou Outono.",
    },
    "clima": {
        "rotulo": "Condição climática",
        "descricao": "De céu limpo a chuva/neve forte.",
    },
    "dia_semana": {
        "rotulo": "Dia da semana",
        "descricao": "De domingo a sábado.",
    },
    "dia_util": {
        "rotulo": "Dia útil",
        "descricao": "Se o dia é útil (não é fim de semana nem feriado).",
    },
    "feriado": {
        "rotulo": "Feriado",
        "descricao": "Se a data é feriado.",
    },
    "ano": {
        "rotulo": "Ano",
        "descricao": "2011 ou 2012.",
    },
    "periodo": {
        "rotulo": "Período do dia",
        "descricao": "Madrugada, manhã, tarde ou noite (derivado da hora).",
    },
}

# Dicionarios de decodificacao, conforme o Readme oficial do dataset
MAPA_ESTACAO = {1: "1-Inverno", 2: "2-Primavera", 3: "3-Verão", 4: "4-Outono"}
MAPA_CLIMA = {
    1: "1-Céu limpo/poucas nuvens",
    2: "2-Névoa/nublado",
    3: "3-Chuva ou neve leve",
    4: "4-Chuva forte/tempestade",
}
MAPA_DIA_SEMANA = {
    0: "0-Domingo", 1: "1-Segunda", 2: "2-Terça", 3: "3-Quarta",
    4: "4-Quinta", 5: "5-Sexta", 6: "6-Sábado",
}
MAPA_SIM_NAO = {0: "Não", 1: "Sim"}
MAPA_ANO = {0: "2011", 1: "2012"}


def _classificar_periodo(hora):
    """Deriva o periodo do dia a partir da hora -- 5a variavel categorica."""
    if 0 <= hora < 6:
        return "1-Madrugada (0h-5h)"
    if 6 <= hora < 12:
        return "2-Manhã (6h-11h)"
    if 12 <= hora < 18:
        return "3-Tarde (12h-17h)"
    return "4-Noite (18h-23h)"


@st.cache_data(show_spinner="Carregando o dataset...")
def carregar_dados():
    """Le o CSV e devolve o DataFrame ja com as colunas derivadas.

    O cache do Streamlit evita reler os 17.379 registros a cada interacao
    do usuario com um slider.
    """
    if not os.path.exists(CAMINHO_CSV):
        raise FileNotFoundError(
            f"Dataset nao encontrado em {CAMINHO_CSV}. "
            f"Baixe-o de {URL_DATASET} e salve hour.csv em data/."
        )

    df = pd.read_csv(CAMINHO_CSV)

    # Desnormalizacao para unidades reais (ver comentario no topo do arquivo)
    df["temp_c"] = df["temp"] * 41.0
    df["atemp_c"] = df["atemp"] * 50.0
    df["hum_pct"] = df["hum"] * 100.0
    df["windspeed_kmh"] = df["windspeed"] * 67.0

    # Decodificacao das categoricas para rotulos legiveis
    df["estacao"] = df["season"].map(MAPA_ESTACAO)
    df["clima"] = df["weathersit"].map(MAPA_CLIMA)
    df["dia_semana"] = df["weekday"].map(MAPA_DIA_SEMANA)
    df["dia_util"] = df["workingday"].map(MAPA_SIM_NAO)
    df["feriado"] = df["holiday"].map(MAPA_SIM_NAO)
    df["ano"] = df["yr"].map(MAPA_ANO)
    df["periodo"] = df["hr"].apply(_classificar_periodo)

    return df


def coluna_como_lista(df, nome):
    """Converte uma coluna do DataFrame em ``list[float]`` pura.

    Esta e a FRONTEIRA do projeto: a partir daqui os dados sao listas
    Python comuns, e todo calculo e feito por ``minhastats``. Nenhum
    metodo estatistico do pandas atravessa esta linha.
    """
    return [float(v) for v in df[nome].tolist()]


def rotulo(nome):
    """Nome amigavel de uma variavel, para exibir nos graficos e tabelas."""
    if nome in VARIAVEIS_NUMERICAS:
        return VARIAVEIS_NUMERICAS[nome]["rotulo"]
    if nome in VARIAVEIS_CATEGORICAS:
        return VARIAVEIS_CATEGORICAS[nome]["rotulo"]
    return nome


def unidade(nome):
    """Unidade de medida da variavel (string vazia se nao tiver)."""
    return VARIAVEIS_NUMERICAS.get(nome, {}).get("unidade", "")


def eixo(nome):
    """Rotulo pronto para o eixo de um grafico.

    Acrescenta a unidade entre colchetes SO se o rotulo ja nao a contiver
    -- caso contrario sairia "Temperatura (°C) [°C]".
    """
    texto = rotulo(nome)
    medida = unidade(nome)
    if medida and medida not in texto:
        return f"{texto} [{medida}]"
    return texto


def descricao(nome):
    """Descricao textual da variavel."""
    if nome in VARIAVEIS_NUMERICAS:
        return VARIAVEIS_NUMERICAS[nome]["descricao"]
    if nome in VARIAVEIS_CATEGORICAS:
        return VARIAVEIS_CATEGORICAS[nome]["descricao"]
    return ""
