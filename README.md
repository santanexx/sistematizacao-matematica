# Laboratório Estatístico Interativo

> Sistematização — **Matemática e Estatística para Computação**
> Aplicação que carrega um conjunto de dados reais e permite explorá-lo por
> estatística descritiva, simulação de Monte Carlo, distribuições teóricas e
> regressão linear — com **todo o núcleo matemático implementado do zero**.

---

## Equipe

| Nome completo | Matrícula |
|---|---|
| Gustavo Santana | 72650214 |
| Pedro Oliveira Rocha | 72650213 |
| Pedro Falcão | 72650212 |

**Nome do grupo:** `[PREENCHER]`
**Repositório:** <https://github.com/santanexx/sistematizacao-matematica>

---

## O projeto em uma frase

Um laboratório estatístico interativo em que **nenhuma medida exibida ao
usuário vem de biblioteca pronta**: média, variância, quartis, correlação de
Pearson e os coeficientes da regressão são calculados por um pacote próprio
(`minhastats/`), escrito em Python puro e validado contra NumPy e SciPy por
**518 testes automatizados**.

### A regra de ouro

```
minhastats/   →  só importa `math` e `random` da biblioteca padrão.
                 Zero numpy, zero scipy, zero pandas, zero statistics.

pandas        →  apenas LÊ o CSV e monta o DataFrame.
matplotlib    →  apenas DESENHA. As classes do histograma e os quartis do
                 boxplot chegam prontos, calculados por minhastats.
numpy/scipy   →  aparecem exclusivamente em tests/, como referência.
```

---

## Dataset

**Bike Sharing Dataset** — *UCI Machine Learning Repository*

- **Link original:** <https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset>
- **Arquivo usado:** `hour.csv` (versionado em [`data/hour.csv`](data/hour.csv))
- **Registros:** 17.379 (exigência: ≥ 1.000)
- **Variáveis numéricas:** 10 disponíveis na aplicação (exigência: ≥ 4)
- **Variáveis categóricas:** 7 disponíveis na aplicação (exigência: ≥ 2)

Registros horários do sistema de bicicletas compartilhadas *Capital Bikeshare*
(Washington D.C., 2011–2012), com clima, calendário e contagem de aluguéis.

> As colunas meteorológicas vêm normalizadas entre 0 e 1 no arquivo original.
> A aplicação aplica a transformação inversa documentada pelos autores
> (`temp × 41`, `atemp × 50`, `hum × 100`, `windspeed × 67`) para exibir tudo
> em **°C, % e km/h** — dizer "a temperatura média é 0,497" não ajuda ninguém.

---

## Como executar do zero

Requisitos: **Python 3.10 ou superior** e `git`.

```bash
# 1. clonar o repositório
git clone https://github.com/santanexx/sistematizacao-matematica.git
cd sistematizacao-matematica

# 2. criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows (PowerShell)

# 3. instalar as dependências
pip install -r requirements.txt

# 4. rodar a aplicação
streamlit run app.py
```

A aplicação abre em <http://localhost:8501>. O dataset já está no repositório
(`data/hour.csv`), então **não é preciso baixar nada**.

### Rodar os testes de validação

```bash
pytest                    # a suíte completa (518 testes)
pytest tests/ -v          # com o nome de cada teste
pytest tests/test_descritiva.py::test_variancia_vs_numpy_dataset -v
```

Saída esperada:

```
518 passed
```

---

## A aplicação funcionando

### Módulo 0 — Dados Reais
Apresentação do dataset, conferência automática dos requisitos do enunciado,
dicionário de variáveis e distribuição das categóricas.

![Módulo 0](docs/imagens/modulo0_dados.png)

### Módulo 2 — Estatística Descritiva Interativa
Medidas de tendência central e dispersão, histograma, boxplot, tabela de
frequências por classes, detecção de outliers pelo IQR e interpretação textual
automática.

![Módulo 2 — medidas](docs/imagens/modulo2_descritiva_1.png)
![Módulo 2 — boxplot e outliers](docs/imagens/modulo2_descritiva_2.png)
![Módulo 2 — interpretação automática](docs/imagens/modulo2_descritiva_3.png)

### Módulo 3 — Probabilidade e Simulação
Lei dos Grandes Números (moeda, dado e estimativa de π) e Teorema Central do
Limite, com número de repetições e tamanho da amostra controlados pelo usuário.

![Módulo 3 — Lei dos Grandes Números](docs/imagens/modulo3_simulacao_1.png)
![Módulo 3 — convergência](docs/imagens/modulo3_simulacao_2.png)

### Módulo 4 — Distribuições Teóricas
Normal, Uniforme, Exponencial, Poisson e Binomial sobrepostas ao histograma,
com parâmetros estimados dos dados e χ² comparativo entre as candidatas.

![Módulo 4 — parâmetros estimados](docs/imagens/modulo4_distribuicoes_1.png)
![Módulo 4 — curva sobreposta](docs/imagens/modulo4_distribuicoes_2.png)

### Módulo 5 — Correlação e Regressão Linear
Dispersão, correlação de Pearson, reta por mínimos quadrados, R², predição
interativa, análise de resíduos e o alerta de causalidade.

![Módulo 5 — regressão](docs/imagens/modulo5_regressao_1.png)
![Módulo 5 — dispersão e predição](docs/imagens/modulo5_regressao_2.png)

### Módulo 6 — Descobertas
As três descobertas estatísticas do laboratório, com todos os números
**recalculados ao vivo** pelo núcleo.

![Módulo 6 — descobertas](docs/imagens/modulo6_descobertas_1.png)
![Módulo 6 — TCL](docs/imagens/modulo6_descobertas_2.png)

---

## Estrutura do repositório

```
sistematizacao/
├── app.py                       # ponto de entrada do Streamlit
│
├── minhastats/                  #  NÚCLEO ESTATÍSTICO PRÓPRIO (Python puro)
│   ├── __init__.py              #    exporta a API pública do pacote
│   ├── descritiva.py            #    média, mediana, moda, amplitude,
│   │                            #    variância e desvio padrão (amostral e
│   │                            #    populacional), percentis, quartis, IQR,
│   │                            #    coeficiente de variação, assimetria, curtose
│   ├── associacao.py            #    covariância, Pearson, mínimos quadrados,
│   │                            #    R², predição, resíduos
│   ├── frequencias.py           #    tabelas de frequência, regra de Sturges,
│   │                            #    outliers por IQR, interpretação automática
│   ├── distribuicoes.py         #    Normal, Uniforme, Exponencial, Binomial,
│   │                            #    Poisson, estimação e qualidade do ajuste
│   └── simulacao.py             #    Monte Carlo: LGN, TCL e estimativa de π
│
├── app/                         #  INTERFACE (não calcula nada)
│   ├── carregador.py            #    lê o CSV, desnormaliza, cataloga variáveis
│   ├── graficos.py              #    Matplotlib desenha o que o núcleo calculou
│   └── paginas/                 #    uma página por módulo
│       ├── m0_dados.py
│       ├── m2_descritiva.py
│       ├── m3_simulacao.py
│       ├── m4_distribuicoes.py
│       ├── m5_regressao.py
│       └── m6_descobertas.py
│
├── tests/                       #  VALIDAÇÃO contra NumPy/SciPy
│   ├── conftest.py              #    fixtures e a justificativa da tolerância
│   ├── test_descritiva.py       #    200 testes
│   ├── test_associacao.py       #     54 testes
│   ├── test_frequencias.py      #     63 testes
│   ├── test_distribuicoes.py    #    140 testes
│   ├── test_simulacao.py        #     28 testes
│   ├── test_regra_de_ouro.py    #     18 testes que LEEM o código-fonte e
│   │                            #        falham se alguém importar numpy no
│   │                            #        núcleo ou chamar .mean()/.corr()
│   │                            #        na interface
│   └── test_app.py              #     15 testes de ponta a ponta da interface
│
├── data/
│   ├── hour.csv                 # dataset (17.379 registros)
│   └── Readme_UCI.txt           # documentação original do UCI
│
├── docs/
│   ├── imagens/                 # capturas de tela usadas neste README
│   ├── capturar_telas.py        # script que gera as capturas
│   ├── roteiro_video.md         # roteiro do vídeo de demonstração
│   └── resumo_executivo.md      # resumo executivo (1 página) para o PDF
│
├── RELATORIO.md                 # relatório completo da atividade
├── requirements.txt
└── pytest.ini
```

---

## Como a validação funciona

Cada função de `minhastats` é comparada com a referência consolidada em **três
frentes**:

1. **Casos calculados à mão** — amostras pequenas com resultado conhecido, para
   garantir que a *fórmula* está certa, e não apenas "igual à de alguém";
2. **O dataset real** — as 17.379 linhas, onde erros de acumulação numérica
   apareceriam;
3. **Amostras aleatórias com semente fixa** — em escalas propositalmente
   hostis (valores de ordem 10⁶, de ordem 10⁻⁶, negativos, com muitos empates).

| Nossa função | Referência |
|---|---|
| `media`, `mediana` | `numpy.mean`, `numpy.median`, `statistics.median` |
| `moda` | `statistics.multimode` |
| `variancia_populacional` / `_amostral` | `numpy.var(ddof=0)` / `numpy.var(ddof=1)` |
| `percentil`, `quartis` | `numpy.percentile(method="linear")` |
| `assimetria_momento`, `curtose_momento` | `scipy.stats.skew/kurtosis(bias=True)` |
| `covariancia_amostral` | `numpy.cov(ddof=1)` |
| `correlacao_pearson` | `scipy.stats.pearsonr`, `numpy.corrcoef` |
| `regressao_linear` | `numpy.polyfit`, `scipy.stats.linregress` |
| `tabela_frequencias_continua` | `numpy.histogram` |
| `normal_pdf/cdf`, `poisson_pmf`, ... | `scipy.stats.norm/poisson/binom/expon/uniform` |

**Tolerância adotada: `rel = 1e-9`** — a justificativa completa está em
[`tests/conftest.py`](tests/conftest.py) e no [RELATORIO.md](RELATORIO.md).

### A regra de ouro é verificada automaticamente

[`tests/test_regra_de_ouro.py`](tests/test_regra_de_ouro.py) lê o código-fonte
com o módulo `ast` e **falha** se alguém, num ajuste de última hora:

- importar qualquer coisa além de `math` e `random` dentro de `minhastats/`;
- chamar `.mean()`, `.median()`, `.std()`, `.var()`, `.corr()`, `.cov()`,
  `.quantile()`, `.describe()`, `.skew()` ou `.percentile()` dentro de `app/`.

Há ainda um teste que importa `minhastats` num subprocesso com `numpy`, `scipy`,
`pandas` e `statistics` **bloqueados** — se o núcleo dependesse secretamente de
alguma delas, o teste quebraria.

---

## Documentos

- **[RELATORIO.md](RELATORIO.md)** — dataset e justificativa, fórmulas em
  notação matemática, decisões de implementação, resultados da validação,
  explicação de cada módulo e as 3 descobertas.
- **[docs/resumo_executivo.md](docs/resumo_executivo.md)** — resumo de 1 página
  para o PDF de entrega.
- **[docs/roteiro_video.md](docs/roteiro_video.md)** — roteiro do vídeo de
  demonstração.

## Vídeo de demonstração

`[PREENCHER: link do YouTube não listado ou do Google Drive com acesso liberado]`

---

## Referência do dataset

> Fanaee-T, H. & Gama, J. (2013). *Event labeling combining ensemble detectors
> and background knowledge*. Progress in Artificial Intelligence, 2(2–3),
> 113–127. Springer.
> Disponível no UCI Machine Learning Repository:
> <https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset>
