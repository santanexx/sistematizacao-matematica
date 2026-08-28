# Relatório da Sistematização
## Laboratório Estatístico Interativo — Matemática e Estatística para Computação

**Equipe:** Gustavo Santana (72650214) · Pedro Oliveira Rocha (72650213) · Pedro Falcão (72650212)
**Nome do grupo:** `[PREENCHER]`
**Repositório:** <https://github.com/santanexx/sistematizacao-matematica>
**Vídeo de demonstração:** `[PREENCHER: URL]`

---

## Sumário

1. [Dataset escolhido e justificativa](#1-dataset-escolhido-e-justificativa)
2. [Arquitetura da solução](#2-arquitetura-da-solução)
3. [Módulo 1 — O núcleo estatístico e suas fórmulas](#3-módulo-1--o-núcleo-estatístico-e-suas-fórmulas)
4. [Decisões de implementação](#4-decisões-de-implementação-e-o-que-elas-custaram)
5. [Validação contra NumPy e SciPy](#5-validação-contra-numpy-e-scipy)
6. [Módulo 2 — Estatística descritiva interativa](#6-módulo-2--estatística-descritiva-interativa)
7. [Módulo 3 — Probabilidade e simulação](#7-módulo-3--probabilidade-e-simulação)
8. [Módulo 4 — Distribuições teóricas](#8-módulo-4--distribuições-teóricas)
9. [Módulo 5 — Correlação e regressão linear](#9-módulo-5--correlação-e-regressão-linear)
10. [Módulo 6 — As três descobertas](#10-módulo-6--as-três-descobertas)
11. [Limitações reconhecidas](#11-limitações-reconhecidas)

---

## 1. Dataset escolhido e justificativa

**Bike Sharing Dataset** — UCI Machine Learning Repository
<https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset>

Registros horários do sistema de bicicletas compartilhadas *Capital Bikeshare*
(Washington D.C.) entre 2011 e 2012, combinando calendário, clima e contagem de
aluguéis.

| Requisito do enunciado | Exigido | Dataset |
|---|---|---|
| Registros | ≥ 1.000 | **17.379** |
| Variáveis numéricas | ≥ 4 | **10** disponíveis na aplicação |
| Variáveis categóricas | ≥ 2 | **7** disponíveis na aplicação |
| Fonte pública e citável | — | UCI ML Repository |

### Por que este dataset

Escolhemos por três razões práticas, não por tema:

1. **Ele tem todos os "tipos estatísticos" ao mesmo tempo.** Variáveis
   aproximadamente simétricas (`temp`, `hum`), fortemente assimétricas
   (`casual`, `cnt`), contagens discretas, cíclicas (`hr`) e categóricas com
   número diferente de níveis (2, 4 e 7). Isso permite exercitar **todos** os
   módulos com dados reais, em vez de forçar um único tipo de análise.
2. **A relação entre variáveis é interessante *porque é imperfeita*.** Existe
   uma correlação clara entre temperatura e aluguéis, mas ela não é linear — o
   que transforma o Módulo 5 numa discussão honesta sobre os limites do modelo,
   e não numa reta bonita e vazia.
3. **Reprodutibilidade sem atrito.** Download direto por URL, sem login nem
   chave de API (diferente do Kaggle). O CSV tem 1,1 MB e está versionado no
   próprio repositório, então `git clone` + `pip install` + `streamlit run`
   basta para rodar.

### Desnormalização das variáveis meteorológicas

O arquivo original traz as variáveis de clima **normalizadas em [0, 1]**. Isso é
conveniente para modelos, mas ilegível num relatório: dizer que "a temperatura
média é 0,497" não comunica nada. Aplicamos a transformação inversa documentada
pelos autores do dataset:

$$
t_{°C} = \text{temp} \times 41 \qquad
t^{ap}_{°C} = \text{atemp} \times 50 \qquad
h_{\%} = \text{hum} \times 100 \qquad
v_{km/h} = \text{windspeed} \times 67
$$

Como são transformações **lineares**, correlação, $R^2$ e coeficiente de
variação são idênticos nas duas escalas — só a leitura melhora. As colunas
originais continuam disponíveis na aplicação para conferência.

---

## 2. Arquitetura da solução

O ponto central do projeto é a separação entre **quem calcula** e **quem exibe**:

```
┌──────────────────────────────────────────────────────────────┐
│  app/ (interface Streamlit)                                  │
│  ────────────────────────────────────────────────────────    │
│  carregador.py  →  pandas.read_csv, desnormalização,         │
│                    catálogo de variáveis                     │
│  graficos.py    →  matplotlib DESENHA o que já foi calculado │
│  paginas/       →  uma página por módulo                     │
└───────────────────────────┬──────────────────────────────────┘
                            │  list[float] (fronteira do projeto)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  minhastats/ (núcleo próprio)                                │
│  ────────────────────────────────────────────────────────    │
│  descritiva · associacao · frequencias                       │
│  distribuicoes · simulacao                                   │
│                                                              │
│  IMPORTA APENAS: math, random                                │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  tests/ (validação)  →  numpy, scipy, statistics             │
└──────────────────────────────────────────────────────────────┘
```

A fronteira é a função `carregador.coluna_como_lista()`: dali em diante os dados
são **listas Python comuns** e nenhum método estatístico do pandas atravessa a
linha. Não existe `df.mean()`, `df.corr()`, `df.describe()` nem
`groupby().mean()` em lugar nenhum da aplicação.

### O detalhe que quase escapou: os gráficos também calculam

`matplotlib.pyplot.hist()` **calcula as classes** e `boxplot()` **calcula os
quartis**. Usá-los violaria a regra de ouro de forma silenciosa — os números na
tela viriam do Matplotlib, não de `minhastats`. Por isso:

- o histograma é desenhado com **`ax.bar()`**, alimentado pela nossa
  `tabela_frequencias_continua()`;
- o boxplot é desenhado com **`ax.bxp()`**, que recebe um dicionário de
  estatísticas **prontas** — os quartis, os limites de Tukey e a lista de
  outliers, todos vindos de `minhastats`.

---

## 3. Módulo 1 — O núcleo estatístico e suas fórmulas

### 3.1 Tendência central

**Média aritmética** — `descritiva.media`

$$\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i$$

**Mediana** — `descritiva.mediana` (sobre a amostra ordenada $x_{(1)} \le \dots \le x_{(n)}$)

$$
Md = \begin{cases}
x_{\left(\frac{n+1}{2}\right)} & \text{se } n \text{ é ímpar} \\[8pt]
\dfrac{x_{\left(\frac{n}{2}\right)} + x_{\left(\frac{n}{2}+1\right)}}{2} & \text{se } n \text{ é par}
\end{cases}
$$

**Moda** — `descritiva.moda`: o conjunto dos valores de frequência absoluta
máxima. Retornamos uma **lista**, porque a distribuição pode ser bimodal ou
multimodal; se nenhum valor se repete, a amostra é amodal e devolvemos lista
vazia.

### 3.2 Dispersão

**Amplitude total** — `descritiva.amplitude`

$$A = x_{\max} - x_{\min}$$

**Variância populacional** — `descritiva.variancia_populacional`

$$\sigma^2 = \frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2$$

**Variância amostral** (correção de Bessel) — `descritiva.variancia_amostral`

$$s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2$$

**Desvios padrão**: $\sigma = \sqrt{\sigma^2}$ e $s = \sqrt{s^2}$.

**Coeficiente de variação** — `descritiva.coeficiente_variacao`

$$CV = \frac{s}{|\bar{x}|} \times 100\%$$

**Erro padrão da média** — `descritiva.erro_padrao_media`

$$EP = \frac{s}{\sqrt{n}}$$

### 3.3 Separatrizes

**Percentil de ordem $p$** — `descritiva.percentil` (interpolação linear, o
método *tipo 7*, que é o padrão do `numpy.percentile`):

$$
h = \frac{p}{100}(n-1), \qquad
P_p = x_{(\lfloor h \rfloor)} + \left(h - \lfloor h \rfloor\right)
      \left[x_{(\lfloor h \rfloor + 1)} - x_{(\lfloor h \rfloor)}\right]
$$

com índices começando em zero. **Quartis:** $Q_1 = P_{25}$, $Q_2 = P_{50} = Md$,
$Q_3 = P_{75}$. **Amplitude interquartil:** $IQR = Q_3 - Q_1$.

### 3.4 Forma da distribuição

**Assimetria de Pearson (2º coeficiente)** — `descritiva.assimetria_pearson`

$$A_s = \frac{3(\bar{x} - Md)}{s}$$

**Assimetria pelo 3º momento** — `descritiva.assimetria_momento`

$$g_1 = \frac{\frac{1}{n}\sum (x_i - \bar{x})^3}{\sigma^3}$$

**Excesso de curtose** — `descritiva.curtose_momento`

$$g_2 = \frac{\frac{1}{n}\sum (x_i - \bar{x})^4}{\sigma^4} - 3$$

O $-3$ coloca a Normal na referência zero.

### 3.5 Associação entre duas variáveis

**Covariância amostral** — `associacao.covariancia_amostral`

$$s_{xy} = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})$$

**Correlação de Pearson** — `associacao.correlacao_pearson`

$$
r = \frac{s_{xy}}{s_x s_y}
  = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}
         {\sqrt{\sum (x_i - \bar{x})^2}\sqrt{\sum (y_i - \bar{y})^2}}
$$

O divisor $n-1$ se cancela entre numerador e denominador — por isso $r$ é o
mesmo usando a versão amostral ou a populacional.

### 3.6 Regressão linear pelo método dos mínimos quadrados

Queremos a reta $\hat{y} = a + bx$ que minimiza a soma dos quadrados dos
resíduos:

$$SQ_{res}(a,b) = \sum_{i=1}^{n}\left(y_i - a - bx_i\right)^2$$

Derivando em relação a $a$ e a $b$ e igualando a zero, obtemos as **equações
normais**, cuja solução é:

$$
b = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}
\qquad\qquad
a = \bar{y} - b\bar{x}
$$

A segunda equação mostra um fato que usamos como teste: **a reta sempre passa
pelo ponto $(\bar{x}, \bar{y})$**.

**Decomposição da variação e coeficiente de determinação:**

$$
\underbrace{\sum (y_i - \bar{y})^2}_{SQ_{tot}} =
\underbrace{\sum (\hat{y}_i - \bar{y})^2}_{SQ_{reg}} +
\underbrace{\sum (y_i - \hat{y}_i)^2}_{SQ_{res}}
\qquad
R^2 = 1 - \frac{SQ_{res}}{SQ_{tot}}
$$

Na regressão linear **simples** vale ainda a identidade $R^2 = r^2$ — que também
virou teste automatizado.

**Erro padrão da estimativa:**

$$s_e = \sqrt{\frac{SQ_{res}}{n-2}}$$

(perdem-se 2 graus de liberdade porque estimamos $a$ e $b$).

### 3.7 Tabelas de frequência

**Regra de Sturges** para o número de classes:

$$k = \lceil 1 + 3{,}322\log_{10} n \rceil = \lceil 1 + \log_2 n \rceil$$

Para $n = 17.379$ isso dá $k = \lceil 15{,}085 \rceil = \mathbf{16}$ classes.

**Amplitude de cada classe:** $h = A/k$, com intervalos $[l_i, l_s)$ fechados à
esquerda; a última classe é fechada nos dois lados para que $x_{\max}$ não fique
de fora.

### 3.8 Detecção de outliers — regra de Tukey

$$LI = Q_1 - f \cdot IQR \qquad LS = Q_3 + f \cdot IQR$$

com $f = 1{,}5$ (outliers moderados) ou $f = 3{,}0$ (extremos). A regra usa
quartis, e não média e desvio padrão, justamente porque quartis são **robustos**:
um valor absurdo não desloca $Q_1$ e $Q_3$, mas envenena $\bar{x}$ e $s$.

### 3.9 Distribuições teóricas

| Distribuição | Função | Estimador usado |
|---|---|---|
| Normal | $f(x) = \dfrac{1}{\sigma\sqrt{2\pi}}e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$ | $\hat\mu = \bar{x}$, $\hat\sigma = s$ |
| Normal (acumulada) | $F(x) = \frac{1}{2}\left[1 + \operatorname{erf}\left(\frac{x-\mu}{\sigma\sqrt{2}}\right)\right]$ | — |
| Uniforme | $f(x) = \dfrac{1}{b-a}$, $a \le x \le b$ | $\hat a = x_{\min}$, $\hat b = x_{\max}$ |
| Exponencial | $f(x) = \lambda e^{-\lambda x}$, $x \ge 0$ | $\hat\lambda = 1/\bar{x}$ (máx. verossimilhança) |
| Binomial | $P(X=k) = \binom{n}{k}p^k(1-p)^{n-k}$ | $\hat n = x_{\max}$, $\hat p = \bar{x}/\hat n$ |
| Poisson | $P(X=k) = \dfrac{e^{-\lambda}\lambda^k}{k!}$ | $\hat\lambda = \bar{x}$ |

**Qualidade do ajuste** (medida descritiva comparativa):

$$\chi^2 = \sum_i \frac{(O_i - E_i)^2}{E_i}, \qquad E_i \approx n \cdot f(\text{ponto médio}_i) \cdot h$$

---

## 4. Decisões de implementação (e o que elas custaram)

### 4.1 Variância em dois passos, não pela "fórmula de máquina"

A forma algebricamente equivalente

$$s^2 = \frac{1}{n-1}\left(\sum x_i^2 - n\bar{x}^2\right)$$

permite calcular a variância em **uma única passada** pelos dados. Nós **não** a
usamos. Motivo: quando a média é grande em relação ao desvio, $\sum x_i^2$ e
$n\bar{x}^2$ são dois números enormes e quase iguais, e subtraí-los provoca
**cancelamento catastrófico** — os dígitos significativos se anulam e sobra
ruído de arredondamento.

Nossa implementação calcula $\bar{x}$ primeiro e só então acumula
$\sum(x_i - \bar{x})^2$: duas passadas, mas numericamente estável. O teste
`test_variancia_vs_numpy_sintetico[grande_escala]` usa exatamente o cenário
patológico (valores $\sim 10^6$ com desvio $\sim 10^4$) para provar que a
escolha valeu a pena.

### 4.2 Poisson em escala logarítmica

O cálculo direto de $P(X=k) = e^{-\lambda}\lambda^k / k!$ estoura o `float` para
valores modestos: com $\lambda = 189$ (a média de `cnt`) e $k = 189$,
$\lambda^k$ tem mais de 400 dígitos. Trabalhamos em log:

$$\ln P(X=k) = -\lambda + k\ln\lambda - \ln(k!), \qquad \ln(k!) = \ln\Gamma(k+1)$$

usando `math.lgamma`. O teste `test_poisson_lambda_grande_nao_estoura` verifica
$\lambda = k = 500$, onde a fórmula ingênua levantaria `OverflowError`.

### 4.3 O bug de borda no histograma (e como o teste o pegou)

Nossa primeira versão atribuía cada valor à sua classe assim:

```python
indice = int((valor - li_global) / h)   #
```

O teste contra `numpy.histogram` falhou em **um único caso**: coluna `hum`, com
$k = 20$ classes, 5 registros na classe errada.

**Diagnóstico:** com $h = 0{,}05$, a borda da classe 17 vale
$0{,}8500000000000001$ e não $0{,}85$ — porque $0{,}05$ não tem representação
binária exata. O valor $0{,}85$ é **menor** que essa borda, então pertence à
classe 16; mas `int(0.85 / 0.05)` devolve `17`, já que a divisão em ponto
flutuante resulta em $17{,}000000000000004$.

**Correção:** calculamos as bordas explicitamente e corrigimos o índice
comparando com elas — que é exatamente o que o NumPy faz internamente:

```python
if indice > 0 and valor < bordas[indice]:
    indice -= 1
elif indice < k - 1 and valor >= bordas[indice + 1]:
    indice += 1
```

Este episódio é a melhor justificativa que temos para o item "validação
automatizada" do enunciado: **o erro era invisível a olho nu** — o histograma
parecia perfeitamente normal — e só apareceu porque uma referência independente
discordava em 5 de 17.379 registros.

### 4.4 Ordenação própria (merge sort)

`sorted()` não é uma função estatística e seria permitido. Implementamos merge
sort mesmo assim porque mediana e percentis dependem inteiramente da ordenação —
se vamos afirmar que o cálculo é nosso, o passo do qual ele depende também deve
ser.

### 4.5 Tratamento de NaN e de entradas inválidas

Toda função passa por `_validar()`, que descarta `NaN` e valores não numéricos e
levanta `ValueError` com mensagem explícita quando a amostra é pequena demais
(a variância amostral exige $n \ge 2$; o coeficiente de variação recusa média
zero em vez de devolver infinito silenciosamente). Em `associacao`, um par
$(x_i, y_i)$ é descartado **inteiro** se qualquer um dos lados for inválido —
descartar só um lado quebraria o emparelhamento.

---

## 5. Validação contra NumPy e SciPy

### 5.1 A estratégia

Cada função é comparada com a referência em **três frentes**:

1. **Casos calculados à mão** — ex.: para $x = [2,4,4,4,5,5,7,9]$ temos
   $\bar{x} = 5$, $Md = 4{,}5$, $Mo = 4$, $\sigma^2 = 4$, $s^2 = 32/7$. Isso
   garante que a **fórmula** está certa, e não apenas "igual à de alguém".
2. **O dataset real** — as 17.379 linhas, onde erros de acumulação apareceriam.
3. **Amostras aleatórias com semente fixa**, em escalas hostis: valores da ordem
   de $10^6$, de $10^{-6}$, negativos, muito assimétricos e com muitos empates.

### 5.2 A tolerância adotada e por quê

**Tolerância relativa: $\varepsilon_{rel} = 10^{-9}$** (nove casas significativas).

Justificativa completa (também em `tests/conftest.py`):

- O `float` de 64 bits (IEEE 754) tem ~15–16 dígitos decimais significativos, e
  cada operação introduz erro relativo de até $2^{-53} \approx 1{,}1 \times 10^{-16}$.
- Somando $n = 17.379$ parcelas, o erro acumulado no pior caso cresce com $n$,
  chegando à ordem de $10^{-12}$.
- O NumPy usa **somatório pareado** (*pairwise summation*) e instruções
  vetoriais SIMD, o que **muda a ordem das operações**. Como a soma em ponto
  flutuante **não é associativa**, um resultado ligeiramente diferente do nosso
  somatório sequencial é esperado e correto.

$10^{-9}$ fica confortavelmente acima do ruído numérico esperado ($\sim 10^{-12}$)
e muito abaixo de qualquer **erro de fórmula**, que apareceria já na segunda ou
terceira casa decimal. Onde a tolerância precisou ser diferente, o teste explica
o motivo no próprio código (ex.: comparações de simulação usam limites derivados
do erro padrão teórico, não uma tolerância numérica).

### 5.3 Cobertura dos testes

```
tests/test_descritiva.py      200 testes
tests/test_associacao.py       54 testes
tests/test_frequencias.py      63 testes
tests/test_distribuicoes.py   140 testes
tests/test_simulacao.py        28 testes
tests/test_regra_de_ouro.py    18 testes (guarda da regra de ouro)
tests/test_app.py              15 testes (interface, ponta a ponta)
─────────────────────────────────────────
                              518 testes — todos passando
```

### 5.4 Mapa de correspondências

| `minhastats` | Referência |
|---|---|
| `media` | `numpy.mean` |
| `mediana` | `numpy.median`, `statistics.median` |
| `moda` | `statistics.multimode` |
| `variancia_populacional` | `numpy.var(ddof=0)`, `statistics.pvariance` |
| `variancia_amostral` | `numpy.var(ddof=1)`, `statistics.variance` |
| `desvio_padrao_*` | `numpy.std(ddof=0 e ddof=1)` |
| `amplitude`, `minimo`, `maximo` | `numpy.ptp`, `numpy.min`, `numpy.max` |
| `percentil`, `quartis` | `numpy.percentile(method="linear")` |
| `assimetria_momento` | `scipy.stats.skew(bias=True)` |
| `curtose_momento` | `scipy.stats.kurtosis(fisher=True, bias=True)` |
| `covariancia_amostral` | `numpy.cov(ddof=1)` |
| `correlacao_pearson` | `scipy.stats.pearsonr`, `numpy.corrcoef` |
| `regressao_linear` | `numpy.polyfit(deg=1)`, `scipy.stats.linregress` |
| `tabela_frequencias_continua` | `numpy.histogram` |
| `regra_sturges` | `numpy.histogram_bin_edges(bins="sturges")` |
| `coeficiente_binomial` | `math.comb` |
| `normal_pdf` / `normal_cdf` | `scipy.stats.norm.pdf` / `.cdf` |
| `uniforme_pdf` | `scipy.stats.uniform.pdf` |
| `exponencial_pdf` | `scipy.stats.expon.pdf` |
| `binomial_pmf` | `scipy.stats.binom.pmf` |
| `poisson_pmf` | `scipy.stats.poisson.pmf` |
| TCL (normalidade das médias) | `scipy.stats.normaltest` |

### 5.5 A regra de ouro virou teste

Confiar que ninguém vai escrever um `df["cnt"].mean()` num ajuste de última hora
é ingênuo. Por isso `tests/test_regra_de_ouro.py` **lê o código-fonte** com o
módulo `ast` e falha automaticamente se:

- algum arquivo de `minhastats/` importar qualquer coisa além de `math` e
  `random`;
- algum arquivo de `app/` (ou o `app.py`) chamar um método estatístico de
  biblioteca — `.mean()`, `.median()`, `.std()`, `.var()`, `.corr()`, `.cov()`,
  `.quantile()`, `.describe()`, `.skew()`, `.kurtosis()`, `.percentile()`.

Há ainda um teste que sobe um subprocesso Python com `numpy`, `scipy`, `pandas` e
`statistics` **bloqueados em `sys.modules`** e verifica que `import minhastats`
funciona e produz resultados corretos. Se o núcleo dependesse secretamente de
alguma dessas bibliotecas, esse teste quebraria.

Esse teste, aliás, encontrou um detalhe interessante: a asserção original era
`correlacao_pearson([1,2,3],[2,4,6]) == 1.0`, e falhou — o valor retornado é
`0.9999999999999998`. Correlação perfeita, mas não exatamente 1 em ponto
flutuante. A asserção foi corrigida para usar folga numérica, que é como
comparações de float devem ser escritas.

### 5.6 Testes de propriedade matemática

Além da comparação numérica, testamos **identidades teóricas** — que pegam erros
que a comparação sozinha deixaria passar:

- $s^2 = \sigma^2 \cdot \frac{n}{n-1}$
- $Q_2 = Md$ (consistência entre `percentil` e `mediana`)
- $\text{Cov}(X,X) = \text{Var}(X)$ e $\text{Cov}(X,Y) = \text{Cov}(Y,X)$
- $-1 \le r \le 1$ para todos os pares do dataset
- $r$ invariante a transformações lineares de $Y$
- $R^2 = r^2$ na regressão simples
- $SQ_{tot} = SQ_{reg} + SQ_{res}$
- a reta passa por $(\bar{x}, \bar{y})$ e $\sum e_i = 0$
- soma das pmf's = 1 (Binomial e Poisson)
- regra empírica 68–95–99,7 da Normal

---

## 6. Módulo 2 — Estatística descritiva interativa

O usuário escolhe uma variável (numérica ou categórica) e recebe:

- **medidas completas** — média, mediana, moda, mínimo, máximo, amplitude,
  quartis, IQR, variância e desvio padrão nas versões **amostral e
  populacional**, coeficiente de variação, erro padrão, assimetria (Pearson e
  momento) e curtose;
- **tabela de frequências** — em classes (com $k$ ajustável, sugerido por
  Sturges) para contínuas; por categoria para qualitativas, com $f_i$, $f_r$,
  percentual e acumuladas;
- **gráficos adequados ao tipo** — histograma e boxplot para numéricas; barras e
  pizza para categóricas;
- **detecção de outliers** pela regra do IQR, com os limites explícitos;
- **interpretação textual automática**, que combina quatro leituras: assimetria
  (posição relativa de média/mediana/moda), dispersão relativa (CV), achatamento
  (curtose) e presença de outliers.

Exemplo de saída automática para `Temperatura (°C)`:

> *"A distribuição de Temperatura (°C) é aproximadamente SIMÉTRICA (coeficiente
> de assimetria de Pearson = -0,047): média (20,376) e mediana (20,500)
> praticamente coincidem. (…) O excesso de curtose é -0,942 (< 0): a curva é
> PLATICÚRTICA, mais achatada que a Normal. Pela regra do IQR (limites -5,74 e
> 46,74), NENHUM outlier foi detectado."*

Há ainda um **cruzamento**: escolhida uma categórica, a aplicação calcula média,
mediana, desvio padrão e CV de uma variável numérica **dentro de cada
categoria** — com listas Python e `minhastats`, sem `groupby().mean()`.

---

## 7. Módulo 3 — Probabilidade e simulação

### 7.1 Lei dos Grandes Números

Três experimentos, todos com número de repetições e semente controlados pelo
usuário:

**(a) Moeda** — convergência da frequência relativa para $p$:

$$\hat{p}_n = \frac{1}{n}\sum_{i=1}^{n}X_i \xrightarrow[n\to\infty]{} p$$

Resultado com $p = 0{,}5$ e semente 42:

| $n$ | $\hat{p}_n$ | Erro absoluto | Ordem de $1/\sqrt{n}$ |
|---|---|---|---|
| 10 | 0,600000 | 0,100000 | 0,316228 |
| 100 | 0,500000 | 0,000000 | 0,100000 |
| 1.000 | 0,480000 | 0,020000 | 0,031623 |
| 10.000 | 0,499000 | 0,001000 | 0,010000 |
| 100.000 | 0,499340 | 0,000660 | 0,003162 |

O ponto pedagógico que o gráfico deixa evidente (com eixo $x$ logarítmico, para
que os primeiros lançamentos — os mais instáveis — não fiquem espremidos na
origem): **o erro não cai linearmente**. Ele decresce na ordem de $1/\sqrt{n}$,
então reduzir o erro pela metade exige **quadruplicar** as repetições.

**(b) Dado** — convergência da média para $E[X] = \frac{f+1}{2}$ e da frequência
de cada face para $1/f$, com barras comparando observado × teórico.

**(c) Estimativa de $\pi$** — bônus clássico: sorteando pontos uniformes em
$[0,1]^2$, a proporção dentro do quarto de círculo estima $\pi/4$:

$$\hat{\pi} = 4 \cdot \frac{\text{pontos dentro}}{n}$$

Com 200.000 pontos e semente 21: $\hat\pi = 3{,}13938$ (erro de 0,0022).

### 7.2 Teorema Central do Limite

$$\bar{X}_n \xrightarrow{d} N\!\left(\mu, \frac{\sigma^2}{n}\right)$$

O usuário escolhe a **variável do dataset**, o **tamanho da amostra** e o
**número de repetições**. Usando `casual` (a mais assimétrica do dataset), com
5.000 repetições e semente 2024:

| Tamanho da amostra $n$ | Assimetria das médias | $\sigma/\sqrt{n}$ (teórico) | Desvio observado | Discrepância |
|---|---|---|---|---|
| população | **2,4990** | — | — | — |
| 2 | 1,7899 | 34,8639 | 35,0149 | 0,43% |
| 5 | 1,1290 | 22,0499 | 21,8443 | 0,93% |
| 10 | 0,7690 | 15,5916 | 15,3473 | 1,57% |
| 30 | 0,4616 | 9,0018 | 8,8926 | 1,21% |
| 100 | 0,2347 | 4,9305 | 4,9324 | 0,04% |
| 200 | **0,1323** | 3,4864 | 3,4823 | 0,12% |

Duas leituras:

1. A assimetria cai de **2,499** para **0,132** — redução de **94,7%** — e o
   histograma das médias vira visivelmente um sino, com a Normal teórica
   sobreposta.
2. O desvio padrão das médias reproduz $\sigma/\sqrt{n}$ com **menos de 2% de
   erro em todos os tamanhos**. O teorema não é só qualitativo: ele acerta o
   número.

Um teste independente confirma: `test_tcl_com_n_grande_passa_no_teste_de_normalidade`
aplica `scipy.stats.normaltest` às médias amostrais com $n = 200$ e obtém
$p > 0{,}05$ — as médias não são distinguíveis de uma Normal.

---

## 8. Módulo 4 — Distribuições teóricas

O usuário escolhe a variável e uma ou mais candidatas entre Normal, Uniforme,
Exponencial, Poisson e Binomial. A aplicação estima os parâmetros **a partir dos
dados**, sobrepõe a curva ao histograma e calcula o $\chi^2$ comparativo.

### Resultado para `Temperatura (°C)`, $k = 16$ classes

| Distribuição | Parâmetros estimados | $\chi^2$ |
|---|---|---|
| **Normal** | $\hat\mu = 20{,}3765$, $\hat\sigma = 7{,}8948$ | **1.680,72** |
| Uniforme | $\hat a = 0{,}82$, $\hat b = 41{,}00$ | 6.428,86 |

A Normal ajusta **3,8× melhor** que a Uniforme. Mas nenhuma das duas ajusta
bem — e o núcleo explica por quê: a assimetria é praticamente nula
($g_1 = -0{,}006$, favorável à Normal), porém o excesso de curtose é
$g_2 = -0{,}942$, isto é, a distribuição é **platicúrtica**, mais achatada que a
Normal. Faz sentido físico: a temperatura não se concentra em torno de um valor
típico, ela percorre todo o intervalo anual. **A forma real está entre a Normal
e a Uniforme.**

### Resultado para `Aluguéis de usuários casuais`, $k = 16$ classes

| Distribuição | Parâmetros estimados | $\chi^2$ |
|---|---|---|
| Normal | $\hat\mu = 35{,}676$, $\hat\sigma = 49{,}305$ | 44.835.539 |
| **Exponencial** | $\hat\lambda = 0{,}028030$ | **3.035,42** |

O $\chi^2$ astronômico da Normal tem causa clara: sendo simétrica, ela prevê
frequência praticamente nula nas classes da cauda direita, onde os dados
efetivamente têm registros — e $(O_i - E_i)^2/E_i$ explode quando $E_i \to 0$. A
Exponencial, que é assimétrica por construção, ajusta **quatro ordens de
grandeza melhor**.

### Diagnóstico específico para contagens

Para variáveis de contagem, a aplicação calcula o **índice de dispersão**:

$$ID = \frac{s^2}{\bar{x}}$$

Na Poisson vale exatamente $ID = 1$ (média = variância). Os valores obtidos são
o assunto da terceira descoberta.

> **Nota metodológica:** o $\chi^2$ é usado aqui como **medida descritiva
> comparativa** entre candidatas, não como teste de hipótese formal — não
> calculamos p-valor nem corrigimos os graus de liberdade pelos parâmetros
> estimados. Uma conclusão formal exigiria um teste de aderência apropriado
> (Kolmogorov-Smirnov, Anderson-Darling ou $\chi^2$ com graus de liberdade
> corrigidos).

---

## 9. Módulo 5 — Correlação e regressão linear

O usuário escolhe X e Y entre as variáveis numéricas e recebe dispersão,
correlação, reta, equação, $R^2$, predição interativa e análise de resíduos.

### Resultados para os principais pares

| X | Y | $r$ | $R^2$ | Equação da reta |
|---|---|---|---|---|
| Temperatura (°C) | Total de aluguéis | +0,4048 | 0,1638 | $\hat{y} = 9{,}2999x - 0{,}0356$ |
| Sensação térmica (°C) | Total de aluguéis | +0,4009 | 0,1607 | $\hat{y} = 8{,}4636x - 11{,}8755$ |
| Umidade (%) | Total de aluguéis | −0,3229 | 0,1043 | $\hat{y} = -3{,}0359x + 379{,}8849$ |
| Hora do dia | Total de aluguéis | +0,3941 | 0,1553 | $\hat{y} = 10{,}3378x + 70{,}0952$ |
| Vento (km/h) | Total de aluguéis | +0,0932 | 0,0087 | $\hat{y} = 2{,}0632x + 163{,}1853$ |
| Registrados | Total de aluguéis | +0,9722 | 0,9451 | $\hat{y} = 1{,}1650x + 10{,}2965$ |

### Interpretação dos coeficientes (par temperatura × aluguéis)

- **$b = 9{,}2999$** — a cada **+1 °C**, o modelo prevê **+9,3 aluguéis por
  hora**.
- **$a = -0{,}0356$** — valor previsto quando a temperatura é 0 °C. A aplicação
  avisa quando $X = 0$ está fora da faixa observada; aqui está dentro
  ($x_{\min} = 0{,}82$ °C), mas o valor negativo já denuncia que a reta não é um
  bom modelo nos extremos — não existe número negativo de aluguéis.
- **$R^2 = 0{,}1638$** — a temperatura explica **16,4%** da variação total;
  **83,6% vêm de outros fatores**.
- **$s_e = 165{,}87$** — desvio típico dos pontos em relação à reta, na mesma
  unidade de $Y$. Comparado à média de 189,46 aluguéis, é enorme: as previsões
  individuais são pouco confiáveis.

### Predição interativa

O usuário digita um valor de X e a aplicação devolve $\hat{Y} = a + bX$,
destacando o ponto no gráfico. Se o valor estiver **fora da faixa observada**, a
aplicação exibe um alerta de **extrapolação** — a reta só foi ajustada dentro do
intervalo dos dados.

### Análise de resíduos

O gráfico de $e_i = y_i - \hat{y}_i$ contra $X$ mostra um **formato de funil**: a
dispersão dos resíduos cresce com a temperatura. Isso é **heterocedasticidade** —
uma violação de um dos pressupostos do modelo linear — e indica que a reta não
captura toda a estrutura dos dados. Confirmação numérica: a média dos resíduos é
da ordem de $10^{-13}$ (zero, a menos de erro de ponto flutuante), como a teoria
exige, mas o desvio padrão é de 165,86.

### Correlação não implica causalidade

Encontrar $r = 0{,}4048$ entre temperatura e aluguéis significa apenas que as
duas variáveis **se movem juntas nos dados observados**. Não prova que uma cause
a outra. Neste dataset a advertência é concreta: temperatura e demanda também
variam com a **estação do ano**, o **horário** e o **dia da semana** — variáveis
confundidoras que afetam ambas. Estabelecer causalidade exigiria um experimento
controlado ou um modelo causal explícito, não uma reta de regressão.

---

## 10. Módulo 6 — As três descobertas

### 1. A temperatura importa — mas explica menos de 17% dos aluguéis

**Números:** $r = 0{,}4048$; $R^2 = 0{,}1638$; reta
$\hat{y} = 9{,}2999x - 0{,}0356$; erro padrão da estimativa 165,87.

A correlação é positiva e moderada, como a intuição prevê. O achado não é esse:
é que **83,6% da variação ficam de fora**. E não por falta de relação — a
relação simplesmente **não é uma reta**. A demanda tem dois picos diários (média
de 359 aluguéis às 8h e 461 às 17h, contra 6,35 às 4h da manhã) que nenhuma reta
em função da temperatura pode capturar. O gráfico de resíduos confirma: em vez
de uma nuvem sem padrão, aparece um funil.

**Lição:** um $r$ "bonito" pode esconder um $R^2$ decepcionante. Como
$R^2 = r^2$, um $r$ de 0,40 vira apenas 16% de variação explicada.

---

### 2. Dois públicos com comportamentos opostos escondidos no mesmo total

| Perfil | Média em dia útil | Média em fim de semana/feriado | Variação |
|---|---|---|---|
| **Casual** (não cadastrado) | 25,56 | 57,44 | **+124,7%** |
| **Registrado** (cadastrado) | 167,65 | 123,96 | **−26,1%** |
| Total (`cnt`) | 193,21 | 181,41 | −6,1% |

Separando por tipo de usuário aparece um padrão que o total **esconde por
completo**: os dois públicos reagem ao calendário **em direções opostas**. São
dois fenômenos diferentes no mesmo dataset — **lazer** contra **deslocamento
pendular para o trabalho**.

A assinatura estatística confirma a separação: o público casual tem coeficiente
de variação de **138,2%** contra 98,4% dos registrados, excesso de curtose de
**7,57** (fortemente leptocúrtica, contra 2,75) e **1.192 outliers pela regra do
IQR** (6,86% dos registros, acima de 114 aluguéis/hora) — as tardes de fim de
semana com clima bom.

**Lição:** analisar só o agregado `cnt` levaria à conclusão errada de que "o dia
da semana quase não afeta a demanda" — a média total varia apenas −6,1%. É o
**paradoxo da agregação**: dois efeitos opostos se cancelando na soma.

---

### 3. Os dados violam a Poisson por um fator de 174× — e o TCL não se abala

| Variável | Índice de dispersão $s^2/\bar{x}$ | Valor sob Poisson |
|---|---|---|
| `cnt` | **173,66** | 1 |
| `registered` | 148,97 | 1 |
| `casual` | 68,14 | 1 |

Aluguéis por hora são uma **contagem** — o livro-texto mandaria testar a Poisson.
Mas a Poisson exige $\sigma^2 = \mu$, isto é, $ID = 1$. Obtivemos **173,66**.
É **sobredispersão extrema**: a variabilidade real é cerca de 174 vezes maior do
que a Poisson admite. O modelo está descartado antes mesmo de olhar o gráfico —
e o Módulo 4 confirma visualmente.

O contraponto é o que torna a descoberta bonita. Mesmo partindo de `casual`, que
é violentamente assimétrica ($g_1 = 2{,}499$, $g_2 = 7{,}569$), o **TCL funciona
exatamente como prometido**: a assimetria das médias amostrais cai para 0,132
com $n = 200$ (redução de 94,7%) e o desvio padrão observado reproduz
$\sigma/\sqrt{n}$ com erro inferior a 2% em **todos** os tamanhos testados.

**Lição:** o TCL é sobre a distribuição **das médias amostrais**, não sobre a dos
dados. Uma variável pode ser tão torta quanto `casual` e ainda assim permitir
inferência baseada na Normal — desde que a amostra seja grande o bastante. Não
precisamos assumir normalidade da população para trabalhar com a média dela.

---

### Achado bônus — a temperatura é a variável mais "bem-comportada" do dataset

Enquanto todas as variáveis de contagem são assimétricas e cheias de outliers, a
temperatura é o oposto: assimetria de momento de **−0,006** (praticamente zero),
média 20,38 °C contra mediana 20,50 °C — quase idênticas — e **zero outliers**
pela regra do IQR, o único caso assim no dataset. O detalhe curioso é o excesso
de curtose de **−0,942**: platicúrtica, mais achatada que a Normal.

---

## 11. Limitações reconhecidas

Listamos honestamente o que **não** fizemos:

1. **O $\chi^2$ do Módulo 4 não é um teste de hipótese.** Não calculamos p-valor
   nem corrigimos os graus de liberdade pelos parâmetros estimados. É uma medida
   descritiva para **comparar candidatas entre si**.
2. **A regressão é apenas simples (uma variável).** Os dados pedem múltiplas
   variáveis e provavelmente um modelo não linear — o próprio $R^2$ de 0,16 e o
   funil nos resíduos dizem isso. O enunciado pede regressão linear simples, e é
   o que entregamos, com o diagnóstico honesto de suas limitações.
3. **Não há intervalos de confiança nem testes de significância** para os
   coeficientes da regressão.
4. **A estimativa de $\hat{n}$ da Binomial** usa o máximo observado, um estimador
   enviesado para baixo; a Binomial é, de qualquer forma, uma candidata pobre
   para estas variáveis.
5. **O gerador de números aleatórios** é o Mersenne Twister do módulo `random` —
   adequado para simulação didática, não para criptografia.

---

## Reprodução

Todos os números deste relatório podem ser reproduzidos com:

```bash
pip install -r requirements.txt
pytest                    # 518 testes de validação
streamlit run app.py      # a aplicação
```

As simulações usam **sementes fixas** (42 para a LGN, 2024 para o TCL, 21 para o
π), então os valores das tabelas saem idênticos em qualquer máquina.
